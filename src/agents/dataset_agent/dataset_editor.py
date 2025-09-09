import os
import logfire
from pydantic import BaseModel

from agents.dataset_agent.engine_requests import get_table_columns
from .query_translator import query_translator_agent
from .query_extractor import query_extractor_agent
from .query_generator import query_generator_agent

logfire_token = os.environ["LOGFIRE_TOKEN"]

# 'if-token-present' means nothing will be sent (and the example will work) if you don't have logfire configured
logfire.configure(send_to_logfire=logfire_token)
logfire.instrument_pydantic_ai()
# logfire.instrument_httpx(capture_all=True)


class Dialect(BaseModel):
    dialect: str
    sql: str


class Column(BaseModel):
    column: str
    data_type: str


async def dataset_editor(
    query: str,
    default_dialect: str,
    con_id: str,
    database: str,
    schema: str,
    table: str,
):
    sql = ""
    used_columns = []
    dialects_sql = []
    unsupported_dialect_errors = []
    planner_result = await query_extractor_agent.run(query)

    print("USER QUERY")
    print(planner_result.output.user_query)
    print("SUPPORTED DIALECTS")
    print(planner_result.output.supported_dialects)
    print("UNSUPPORTED DIALECTS")
    print(planner_result.output.unsupported_dialects)

    if planner_result.output.error:
        return planner_result.output.error

    response_columns = await get_table_columns(
        database=database, schema=schema, table=table, connection_id=con_id
    )
    columns = response_columns["columns"]

    if planner_result.output.user_query:

        user_prompt = f"""
            User query: {planner_result.output.user_query}
            
            Table columns: {columns}
            """

        result = await query_generator_agent.run(user_prompt, deps=default_dialect)

        if result.output.error:
            return result.output.error
        if result.output.sql:
            sql = result.output.sql
        if result.output.used_columns:
            used_columns = result.output.used_columns

    if planner_result.output.supported_dialects:
        supported_dialects_without_default = [
            x for x in planner_result.output.supported_dialects if x != default_dialect
        ]

        for dialect in supported_dialects_without_default:
            result = await query_translator_agent.run(
                f"""
                Translate this SQL query {sql} from {default_dialect} to {dialect} dialect

                For context, the user query that was used to generate the original sql query is {planner_result.output.user_query},
                And these are the used columns used in the SQL expression with their data types: {used_columns} 
            

                """,
                deps={
                    "source_dialect": default_dialect,
                    "target_dialect": dialect,
                    "user_query": planner_result.output.user_query,
                },
            )

            if result.output.sql:
                dialects_sql.append({"dialect": dialect, "sql": result.output.sql})

            if planner_result.output.unsupported_dialects:
                unsupported_dialect_errors.append(
                    f'Sorry, we don\'t support {", ".join(planner_result.output.unsupported_dialects)} dialects.'
                )

    return {
        "sql": sql,
        "dialects_sql": dialects_sql,
        "unsupported_dialect_errors": unsupported_dialect_errors,
    }

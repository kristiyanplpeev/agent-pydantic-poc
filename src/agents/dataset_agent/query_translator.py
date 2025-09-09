from pydantic import BaseModel
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.google import GoogleModel
from common.providers.model_providers import google_provider, openai_provider


query_translator_model = GoogleModel("gemini-2.5-flash", provider=google_provider)


class TranslatorOutput(BaseModel):
    sql: str


query_translator_agent = Agent(query_translator_model, output_type=TranslatorOutput)


@query_translator_agent.instructions
def translator_instructions(ctx: RunContext[str]):
    return f"""You are an expert in SQL and cloud data warehouses. 
    Your task is to translate SQL query for a calculated column written for one data warehouse dialog into the correct dialog for another data warehouse.
    A calculated column is defined as a SQL expression that derives a new column based on existing columns in a table. 
    That SQL expression can be run as part of the SELECT list of a query.

    Instructions:
        1.	Take the input SQL query, written in {ctx.deps["source_dialect"].value} dialect.
        2.	Translate it into valid {ctx.deps["target_dialect"].value} SQL syntax.
        3.	Preserve the semantics, logic, and performance characteristics as much as possible.
        4.	If certain functions or data types are not available in the target warehouse, replace them with the closest equivalent and briefly comment on the substitution.
        5.	Do not add any explanations, only the SQL query.
    """

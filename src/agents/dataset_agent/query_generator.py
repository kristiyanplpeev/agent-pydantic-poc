from pydantic import BaseModel
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.google import GoogleModel
from common.providers.model_providers import google_provider


class Column(BaseModel):
    name: str
    data_type: str


class QueryGeneratorOutput(BaseModel):
    sql: str | None
    used_columns: list[Column]
    error: str | None


# mcp_server = MCPServerSSE(url="http://localhost:8003/sse")


query_generator_model = GoogleModel(
    "gemini-2.5-pro", provider=google_provider, settings={"temperature": 0}
)
# query_generator_model = AnthropicModel(
#     "claude-opus-4-1-20250805", provider=anthropic_provider, settings={"temperature": 0}
# )
# query_generator_model = OpenAIChatModel(
#     "gpt-5-mini", provider=openai_provider, settings={"temperature": 0}
# )
query_generator_agent = Agent(
    query_generator_model,
    output_type=QueryGeneratorOutput,
)


@query_generator_agent.instructions
def generate_query_instructions(ctx: RunContext[str]) -> str:
    return f"""
    Role: You are an SQL query generator specialized in creating calculated columns for {ctx.deps.value} Data Warehouse.
    A calculated column is defined as a SQL expression that derives a new column based on existing columns in a table.
    The value of the sql property should be a valid {ctx.deps.value} SQL statement that can be run as part of the SELECT list of a query.

    In the user query you will be provided with the columns of a table with their data type.
    From these columns, generate a valid {ctx.deps.value} SQL query that produces the calculated column requested by the user.

    Important:
    Use {ctx.deps.value} SQL dialect.
    Only use columns that exist in the table.
    The output must be a single {ctx.deps.value} SQL query that defines the calculated column
    and the columns that were used in generating the SQL query.

    Error handling:
    If the requested calculation cannot be performed due to missing or invalid columns, respond with an error.
    Your error must:
    Clearly describe the problem (e.g., "Column X does not exist in table Y").

    Never generate SQL if errors are detected.
    """

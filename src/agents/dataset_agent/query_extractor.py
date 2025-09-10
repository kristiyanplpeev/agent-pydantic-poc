from pydantic import BaseModel
from enum import Enum

from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel
from common.providers.model_providers import (
    google_provider,
)


class SupportedDialects(str, Enum):
    Snowflake = "Snowflake"
    Postgresql = "Postgresql"
    DatabricksSQL = "DatabricksSQL"
    BigQuery = "BigQuery"
    Iris = "Iris"


planner_model = GoogleModel("gemini-2.5-flash", provider=google_provider)


class QueryExtractorOutput(BaseModel):
    user_query: str
    supported_dialects: list[SupportedDialects] | None
    unsupported_dialects: list[str] | None
    error: str | None


query_extractor_agent = Agent(
    planner_model,
    output_type=QueryExtractorOutput,
    system_prompt="""
    You user query extractor in a SQL generation agent for calculated columns. 
    A calculated column is defined as a SQL expression that derives a new column based on existing columns in a table.
    
    Your task is to extract from the user's query what calculated column does the user want and add it to the user_query property.
    
    Also extract in what dialects does he want the query and add them to the dialects array.
    The allowed sql dialects are Snowflake, Postgresql, DatabricksSQL, BigQuery and Iris.
    If the dialect described in the query is one of the listed, add it in supported_dialects list.
    If the dialect described in the query is not one of the listed, add it to unsupported dialects list.

    If the user query is not regarding generating user query, return error explaining that you can only help with generating calculated columns.
    """,
)

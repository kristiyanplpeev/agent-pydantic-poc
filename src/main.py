from fastapi import FastAPI
from pydantic import BaseModel

from agents.dataset_agent.dataset_editor import dataset_editor
from agents.dataset_agent.query_extractor import SupportedDialects
from dotenv import load_dotenv

load_dotenv()


class Body(BaseModel):
    query: str
    default_dialect: SupportedDialects
    con_id: str
    database: str
    schema: str
    table: str


app = FastAPI()


@app.post("/chat")
async def chat(body: Body):
    return await dataset_editor(
        query=body.query,
        default_dialect=body.default_dialect,
        con_id=body.con_id,
        database=body.database,
        schema=body.schema,
        table=body.table,
    )

import os

import httpx
from dotenv import load_dotenv

load_dotenv()

headers = {"Content-Type": "application/json"}
engine_url = os.environ["ENGINE_URL"]
keycloak_url = os.environ["KEYCLOAK_URL"]


async def get_access_token():
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    url = f"{keycloak_url}/realms/atscale/protocol/openid-connect/token"
    form_data = {
        "client_id": "atscale-modeler",
        "client_secret": "1N0OcPo0pWEnmsQEjizJDB7S4bLFZzWC",
        "username": "atscale-kc-admin",
        "password": "@scaleAdmin123",
        "grant_type": "password",  # or whatever grant you’re using
    }

    async with httpx.AsyncClient(timeout=30.0) as client:

        response = await client.post(url, headers=headers, data=form_data)
        response.raise_for_status()  # Raises an exception for 4xx/5xx status codes
        data = response.json()

        return data["access_token"]


async def get_table_columns(database: str, schema: str, table: str, connection_id: str):
    url = f"{engine_url}/data-sources/conn/{connection_id}/table/{table}/info?database={database}&schema={schema}"

    token = await get_access_token()

    if token:
        headers["Authorization"] = f"Bearer {token}"

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()  # Raises an exception for 4xx/5xx status codes
        data = response.json()["response"]

        return data

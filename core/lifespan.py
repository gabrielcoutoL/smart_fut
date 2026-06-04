from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI

fake_teams_db = []
fake_matches_db = []


@asynccontextmanager
async def lifespan(app: FastAPI):

    client = httpx.AsyncClient()
    print("Servidor Iniciando: Conexões abertas.")

    yield {"http_client": client}

    await client.aclose()
    print("Servidor Desligando: Conexões encerradas.")

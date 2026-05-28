import os

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from core import exceptions
from routers import matches, teams

ENV = os.getenv("ENV")

tags_metadata = [
    {"name": "Teams", "description": "Operações de CRUD dos times."},
    {"name": "Matches", "description": "Operações de CRUD das partidas."},
]

app = FastAPI(
    title="Smart Fut API",
    docs_url=None if ENV == "production" else "/docs",
    redoc_url=None if ENV == "production" else "/redoc",
    openapi_url=None if ENV == "production" else "/openapi.json",
)

app.include_router(teams.router, prefix="/teams", tags=["Teams"])
app.include_router(matches.router, prefix="/matches", tags=["Matches"])


@app.exception_handler(exceptions.DomainException)
def domain_exception_handler(request: Request, exc: exceptions.DomainException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.code, "message": exc.message}},
    )

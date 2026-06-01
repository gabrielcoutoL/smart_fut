import os
import time
import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
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


@app.middleware("http")
async def add_custom_headers_and_log(request: Request, call_next):
    request_id = str(uuid.uuid4())
    start_time = time.time()

    response = await call_next(request)

    process_time = time.time() - start_time
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time-Sec"] = str(round(process_time, 4))

    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://datacraque.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

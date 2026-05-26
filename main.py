from fastapi import FastAPI

from routers import teams

app = FastAPI(title="Smart Fut API")

app.include_router(teams.router, prefix="/teams", tags=["Teams"])

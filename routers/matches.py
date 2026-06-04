from datetime import datetime, timezone
from http import HTTPStatus

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Body,
    Depends,
    HTTPException,
    Path,
    WebSocket,
    WebSocketDisconnect,
)

from core.bg_tasks import recalculate_advanced_metrics
from core.exceptions import DomainException
from core.lifespan import fake_matches_db
from core.security import verify_api_key
from core.websockets import ConnectionManager
from routers.teams import fake_teams_db
from schemas.matches import MatchCreate, MatchResponse

manager = ConnectionManager()

router = APIRouter()


@router.post(
    "/",
    response_model=MatchResponse,
    status_code=HTTPStatus.CREATED,
    dependencies=[Depends(verify_api_key)],
)
async def create_match(
    background_tasks: BackgroundTasks,
    match: MatchCreate = Body(
        openapi_examples={
            "match_created": {
                "summary": "Exemplo de partida criada com sucesso",
                "description": "Payload enviado para a criação de uma partida",
                "value": {
                    "home_team_id": 1,
                    "away_team_id": 2,
                    "home_goals": 0,
                    "away_goals": 1,
                    "season": 2026,
                },
            }
        }
    ),
):

    if not any(d.get("id") == match.away_team_id for d in fake_teams_db):
        raise DomainException(
            status_code=404,
            code="TEAM_NOT_FOUND",
            message=f"TIME {match.away_team_id} NÃO ENCONTRADO",
        )

    if not any(d.get("id") == match.home_team_id for d in fake_teams_db):
        raise DomainException(
            status_code=404,
            code="TEAM_NOT_FOUND",
            message=f"TIME {match.home_team_id} NÃO ENCONTRADO",
        )

    match_id = len(fake_matches_db) + 1
    match_data = match.model_dump()

    match_record = {
        **match_data,
        "id": match_id,
        "created_at": datetime.now(tz=timezone.utc),
    }

    fake_matches_db.append(match_record)

    background_tasks.add_task(recalculate_advanced_metrics, match_record["id"])

    return match_record


@router.post("/{match_id}/events")
async def broadcast_events(payload: dict, match_id: int = Path(gt=0)):
    await manager.broadcast(payload, match_id)


@router.get("/", response_model=list[MatchResponse], status_code=HTTPStatus.OK)
def get_matches(skip: int = 0, limit: int = 10, season: int | None = None):

    if season is not None:
        filtered_matches = [m for m in fake_matches_db if m["season"] == season]

        return filtered_matches[skip : skip + limit]

    return fake_matches_db[skip : skip + limit]


@router.get("/{match_id}", response_model=MatchResponse, status_code=HTTPStatus.OK)
def get_match_by_id(match_id: int = Path(gt=0)):

    match = next((m for m in fake_matches_db if m["id"] == match_id), None)

    if not match:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Match not found")

    return match


@router.websocket("/{match_id}/live")
async def websocket_match(websocket: WebSocket, match_id: int = Path(gt=0)):

    manager.connect(websocket=websocket, match_id=match_id)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket=websocket, match_id=match_id)

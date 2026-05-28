from datetime import datetime, timezone
from http import HTTPStatus

from fastapi import APIRouter, Body, HTTPException, Path

from core.exceptions import DomainException
from routers.teams import fake_teams_db
from schemas.matches import MatchCreate, MatchResponse

router = APIRouter()

fake_matches_db = []


@router.post("/", response_model=MatchResponse, status_code=HTTPStatus.CREATED)
def create_match(
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
    return match_record


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

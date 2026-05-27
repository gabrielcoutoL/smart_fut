from http import HTTPStatus

from fastapi import APIRouter

from schemas.teams import TeamCreate, TeamResponse

router = APIRouter()

fake_teams_db = []


@router.post("/", status_code=HTTPStatus.CREATED, response_model=TeamResponse)
def create_team(team: TeamCreate):

    team_id = len(fake_teams_db) + 1

    team_data = team.model_dump()

    team_record = {**team_data, "id": team_id}

    fake_teams_db.append(team_record)

    return team_record


@router.get("/", status_code=HTTPStatus.OK, response_model=list[TeamResponse])
def get_teams():

    return fake_teams_db

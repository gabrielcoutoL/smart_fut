from datetime import datetime

from pydantic import BaseModel


class MatchCreate(BaseModel):
    home_team_id: int
    away_team_id: int
    home_goals: int
    away_goals: int
    season: int


class MatchResponse(MatchCreate):
    id: int
    created_at: datetime

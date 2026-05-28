from datetime import datetime

from pydantic import BaseModel, Field, model_validator


class MatchCreate(BaseModel):
    home_team_id: int
    away_team_id: int
    home_goals: int = Field(ge=0)
    away_goals: int = Field(ge=0)
    season: int

    @model_validator(mode="after")
    def teams_validation(self):
        if self.home_team_id == self.away_team_id:
            raise ValueError("O time mandante não pode ser o mesmo que o visitante!")
        return self


class MatchResponse(MatchCreate):
    id: int
    created_at: datetime

from pydantic import BaseModel


class TeamCreate(BaseModel):
    name: str
    stadium: str
    foundation_year: int


class TeamResponse(TeamCreate):
    id: int

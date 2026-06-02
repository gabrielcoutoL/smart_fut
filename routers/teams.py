from http import HTTPStatus

from fastapi import APIRouter, Depends, File, Header, HTTPException, Path, UploadFile

from core.security import verify_api_key
from schemas.teams import TeamCreate, TeamResponse

router = APIRouter()

fake_teams_db = []


@router.post(
    "/",
    status_code=HTTPStatus.CREATED,
    response_model=TeamResponse,
    dependencies=[Depends(verify_api_key)],
)
def create_team(team: TeamCreate):

    team_id = len(fake_teams_db) + 1

    team_data = team.model_dump()

    team_record = {**team_data, "id": team_id}

    fake_teams_db.append(team_record)

    return team_record


@router.post("/{team_id}/crest", status_code=HTTPStatus.CREATED)
async def create_logo(
    team_id: int = Path(),
    file: UploadFile = File(),
    content_length: int = Header(default=0),
):
    if content_length > 2_097_152:
        raise HTTPException(
            status_code=HTTPStatus.REQUEST_ENTITY_TOO_LARGE,
            detail="Arquivo muito grande !",
        )

    file_header = await file.read(8)

    png_header = b"\x89PNG\r\n\x1a\n"
    jpeg_header = b"\xff\xd8\xff"

    if file_header.startswith(png_header) or file_header.startswith(jpeg_header):
        await file.seek(0)
    else:
        raise HTTPException(
            status_code=HTTPStatus.UNSUPPORTED_MEDIA_TYPE,
            detail="Formato não suportado!",
        )

    return {"filename": file.filename, "status": "Upload concluído"}


@router.get("/", status_code=HTTPStatus.OK, response_model=list[TeamResponse])
def get_teams():

    return fake_teams_db

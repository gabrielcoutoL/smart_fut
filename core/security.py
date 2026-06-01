from typing import Annotated

from fastapi import Header, HTTPException, status

API_SECRET_TOKEN = "super-secret-token"


def verify_api_key(x_api_key: Annotated[str | None, Header(alias="X-API-Key")] = None):
    if x_api_key != API_SECRET_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas!"
        )
    return x_api_key

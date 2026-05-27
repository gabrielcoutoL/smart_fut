import pytest
from fastapi.testclient import TestClient

from main import app
from routers.teams import fake_teams_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_database():

    fake_teams_db.clear()
    yield


def test_post_team():

    response = client.post(
        "/teams/",
        json={"name": "Atletico MG", "stadium": "Arena MRV", "foundation_year": 1908},
    )

    assert response.status_code == 201
    assert response.json() == {
        "name": "Atletico MG",
        "stadium": "Arena MRV",
        "foundation_year": 1908,
        "id": 1,
    }


def test_get_teams():

    fake_teams_db.append(
        {
            "name": "Atletico MG",
            "stadium": "Arena MRV",
            "foundation_year": 1908,
            "id": 1,
        }
    )

    response = client.get("/teams/")

    assert response.status_code == 200
    assert response.json() == [
        {
            "name": "Atletico MG",
            "stadium": "Arena MRV",
            "foundation_year": 1908,
            "id": 1,
        }
    ]

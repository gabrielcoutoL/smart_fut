import pytest
from fastapi.testclient import TestClient

from main import app
from routers.matches import fake_matches_db
from routers.teams import fake_teams_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_database():

    fake_teams_db.clear()
    fake_matches_db.clear()
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


def test_post_match():
    fake_teams_db.extend(
        [
            {
                "id": 1,
                "name": "Team A",
                "stadium": "Stadium A",
                "foundation_year": 1900,
            },
            {
                "id": 2,
                "name": "Team B",
                "stadium": "Stadium B",
                "foundation_year": 1900,
            },
        ]
    )

    payload = {
        "home_team_id": 1,
        "away_team_id": 2,
        "home_goals": 2,
        "away_goals": 1,
        "season": 2026,
    }

    response = client.post("/matches/", json=payload)
    data = response.json()

    assert response.status_code == 201
    assert data["home_team_id"] == 1
    assert data["season"] == 2026
    assert "id" in data
    assert "created_at" in data


def test_get_match_by_id_not_found():
    response = client.get("/matches/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Match not found"


def test_get_match_invalid_id_path_validation():
    response = client.get("/matches/-1")

    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == "greater_than"


def test_get_matches_pagination_and_filters():
    fake_matches_db.extend(
        [
            {
                "id": 1,
                "home_team_id": 1,
                "away_team_id": 2,
                "home_goals": 1,
                "away_goals": 1,
                "season": 2025,
                "created_at": "2026-01-01T00:00:00Z",
            },
            {
                "id": 2,
                "home_team_id": 3,
                "away_team_id": 4,
                "home_goals": 2,
                "away_goals": 0,
                "season": 2026,
                "created_at": "2026-01-01T00:00:00Z",
            },
            {
                "id": 3,
                "home_team_id": 1,
                "away_team_id": 3,
                "home_goals": 0,
                "away_goals": 0,
                "season": 2026,
                "created_at": "2026-01-01T00:00:00Z",
            },
        ]
    )

    response_pagination = client.get("/matches/?limit=2")
    assert response_pagination.status_code == 200
    assert len(response_pagination.json()) == 2

    response_season = client.get("/matches/?season=2025")
    assert response_season.status_code == 200

    data_season = response_season.json()
    assert len(data_season) == 1
    assert data_season[0]["id"] == 1


def test_post_match_negative_goals():
    payload = {
        "home_team_id": 1,
        "away_team_id": 2,
        "home_goals": -2,
        "away_goals": 1,
        "season": 2026,
    }

    response = client.post("/matches/", json=payload)

    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == "greater_than_equal"


def test_post_match_same_team():
    payload = {
        "home_team_id": 1,
        "away_team_id": 1,
        "home_goals": 2,
        "away_goals": 1,
        "season": 2026,
    }

    response = client.post("/matches/", json=payload)

    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == "value_error"


def test_post_match_team_not_exists():
    payload = {
        "home_team_id": 50,
        "away_team_id": 1,
        "home_goals": 2,
        "away_goals": 1,
        "season": 2026,
    }

    response = client.post("/matches/", json=payload)

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "TEAM_NOT_FOUND"
    assert "NÃO ENCONTRADO" in response.json()["error"]["message"]

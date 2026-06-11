from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities as app_activities

client = TestClient(app)
INITIAL_ACTIVITIES = deepcopy(app_activities)


@pytest.fixture(autouse=True)
def reset_activities():
    app_activities.clear()
    app_activities.update(deepcopy(INITIAL_ACTIVITIES))
    yield


def test_get_activities_returns_data():
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert data["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"


def test_signup_for_activity_adds_participant():
    response = client.post("/activities/Chess%20Club/signup?email=test.student@mergington.edu")

    assert response.status_code == 200
    payload = response.json()
    assert "Signed up test.student@mergington.edu for Chess Club" in payload["message"]
    assert "test.student@mergington.edu" in app_activities["Chess Club"]["participants"]


def test_signup_duplicate_returns_400():
    existing_email = app_activities["Chess Club"]["participants"][0]
    response = client.post(f"/activities/Chess%20Club/signup?email={existing_email}")

    assert response.status_code == 400
    payload = response.json()
    assert payload["detail"] == "Student already signed up"


def test_signup_for_unknown_activity_returns_404():
    response = client.post("/activities/Unknown%20Club/signup?email=test.student@mergington.edu")

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_participant_from_activity():
    participant = app_activities["Programming Class"]["participants"][0]
    response = client.delete(f"/activities/Programming%20Class/participants/{participant}")

    assert response.status_code == 200
    payload = response.json()
    assert f"Removed {participant} from Programming Class" in payload["message"]
    assert participant not in app_activities["Programming Class"]["participants"]


def test_remove_missing_participant_returns_404():
    response = client.delete("/activities/Programming%20Class/participants/missing.student@mergington.edu")

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def test_remove_participant_from_unknown_activity_returns_404():
    response = client.delete("/activities/Unknown%20Club/participants/test.student@mergington.edu")

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"

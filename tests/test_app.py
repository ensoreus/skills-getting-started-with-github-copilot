from copy import deepcopy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    original_activities = deepcopy(activities)

    activities.clear()
    activities.update(deepcopy(original_activities))

    yield

    activities.clear()
    activities.update(deepcopy(original_activities))


def test_get_activities_returns_activity_catalog(client):
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert expected_activity in payload
    assert payload[expected_activity]["participants"] == [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]


def test_signup_for_activity_adds_student(client):
    # Arrange
    activity_name = "Chess Club"
    email = "student@example.com"

    # Act
    response = client.post(
        f"/activities/{quote(activity_name)}/signup?email={quote(email)}"
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in activities[activity_name]["participants"]


def test_signup_duplicate_student_returns_400(client):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{quote(activity_name)}/signup?email={quote(email)}"
    )

    # Assert
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student is already signed up for this activity"
    }


def test_signup_missing_activity_returns_404(client):
    # Arrange
    activity_name = "Unknown Club"
    email = "student@example.com"

    # Act
    response = client.post(
        f"/activities/{quote(activity_name)}/signup?email={quote(email)}"
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_participant_removes_student_from_activity(client):
    # Arrange
    activity_name = "Chess Club"
    email = "student@example.com"
    signup_response = client.post(
        f"/activities/{quote(activity_name)}/signup?email={quote(email)}"
    )
    assert signup_response.status_code == 200

    # Act
    response = client.delete(
        f"/activities/{quote(activity_name)}/participants/{quote(email)}"
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from {activity_name}"}
    assert email not in activities[activity_name]["participants"]


def test_unregister_missing_participant_returns_404(client):
    # Arrange
    activity_name = "Chess Club"
    email = "missing@example.com"

    # Act
    response = client.delete(
        f"/activities/{quote(activity_name)}/participants/{quote(email)}"
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Participant not found"}


def test_unregister_missing_activity_returns_404(client):
    # Arrange
    activity_name = "Unknown Club"
    email = "student@example.com"

    # Act
    response = client.delete(
        f"/activities/{quote(activity_name)}/participants/{quote(email)}"
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}

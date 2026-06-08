from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)
initial_activities = deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update(deepcopy(initial_activities))
    yield


def test_root_redirects_to_index_html():
    # Arrange
    expected_path = "/static/index.html"

    # Act
    response = client.get("/")

    # Assert
    assert response.status_code == 200
    assert response.url.path.endswith(expected_path)


def test_get_activities_returns_all_activities():
    # Arrange
    expected_activities = deepcopy(initial_activities)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == expected_activities


def test_signup_for_activity_adds_participant():
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    expected_message = {"message": f"Signed up {email} for {activity_name}"}

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == expected_message
    assert email in activities[activity_name]["participants"]


def test_signup_for_activity_returns_400_for_existing_student():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    expected_detail = "Student is already signed up for this activity"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == expected_detail


def test_signup_for_unknown_activity_returns_404():
    # Arrange
    activity_name = "Nonexistent Club"
    email = "student@mergington.edu"
    expected_detail = "Activity not found"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == expected_detail


def test_remove_participant_from_activity():
    # Arrange
    activity_name = "Programming Class"
    email = "emma@mergington.edu"
    expected_message = {"message": f"Removed {email} from {activity_name}"}

    # Act
    response = client.delete(f"/activities/{activity_name}/participants", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == expected_message
    assert email not in activities[activity_name]["participants"]


def test_remove_unknown_activity_returns_404():
    # Arrange
    activity_name = "Unknown Club"
    email = "student@mergington.edu"
    expected_detail = "Activity not found"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == expected_detail


def test_remove_unknown_participant_returns_404():
    # Arrange
    activity_name = "Gym Class"
    email = "ghost@mergington.edu"
    expected_detail = "Participant not found"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == expected_detail

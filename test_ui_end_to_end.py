import copy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


def test_static_ui_assets_load_correctly():
    index_response = client.get("/static/index.html")
    assert index_response.status_code == 200
    assert "Mergington High School Activities" in index_response.text
    assert "signup-form" in index_response.text

    js_response = client.get("/static/app.js")
    assert js_response.status_code == 200
    assert "fetchActivities" in js_response.text


def test_signup_flow_and_duplicate_error_message():
    email = "ui-test@example.com"
    activity_name = "Chess Club"
    response = client.post(
        f"/activities/{quote(activity_name)}/signup",
        params={"email": email},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["message"] == f"Signed up {email} for {activity_name}"

    list_response = client.get("/activities")
    assert list_response.status_code == 200
    activities_data = list_response.json()
    participants = [p.lower() for p in activities_data[activity_name]["participants"]]
    assert email.lower() in participants

    duplicate_response = client.post(
        f"/activities/{quote(activity_name)}/signup",
        params={"email": email},
    )
    assert duplicate_response.status_code == 400
    assert duplicate_response.json()["detail"] == (
        "A student with this email is already signed up for the selected activity."
    )

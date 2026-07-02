from urllib.parse import quote


def test_get_activities_returns_activity_list(client):
    # Arrange

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert data["Chess Club"]["max_participants"] == 12


def test_signup_for_activity_adds_student(client):
    # Arrange
    email = "backend-test@example.com"
    activity_name = "Chess Club"

    # Act
    response = client.post(
        f"/activities/{quote(activity_name)}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert payload["message"] == f"Signed up {email} for {activity_name}"

    updated_response = client.get("/activities")
    updated_data = updated_response.json()
    participants = [participant.lower() for participant in updated_data[activity_name]["participants"]]
    assert email.lower() in participants


def test_duplicate_signup_returns_friendly_error(client):
    # Arrange
    email = "duplicate-test@example.com"
    activity_name = "Chess Club"

    # Act
    client.post(
        f"/activities/{quote(activity_name)}/signup",
        params={"email": email},
    )
    duplicate_response = client.post(
        f"/activities/{quote(activity_name)}/signup",
        params={"email": email},
    )

    # Assert
    assert duplicate_response.status_code == 400
    assert duplicate_response.json()["detail"] == "A student with this email is already signed up for the selected activity."


def test_invalid_email_returns_400(client):
    # Arrange
    invalid_email = "not-an-email"
    activity_name = "Chess Club"

    # Act
    response = client.post(
        f"/activities/{quote(activity_name)}/signup",
        params={"email": invalid_email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid email address"


def test_nonexistent_activity_returns_404(client):
    # Arrange
    email = "missing-activity@example.com"
    activity_name = "Nonexistent Club"

    # Act
    response = client.post(
        f"/activities/{quote(activity_name)}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"

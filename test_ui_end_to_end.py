import copy
import unittest
from urllib.parse import quote

from fastapi.testclient import TestClient
from src.app import activities, app

client = TestClient(app)


class TestUIEndToEnd(unittest.TestCase):
    def setUp(self):
        self.original_activities = copy.deepcopy(activities)

    def tearDown(self):
        activities.clear()
        activities.update(self.original_activities)

    def test_static_ui_assets_load_correctly(self):
        index_response = client.get("/static/index.html")
        self.assertEqual(index_response.status_code, 200)
        self.assertIn("Mergington High School Activities", index_response.text)
        self.assertIn("signup-form", index_response.text)

        js_response = client.get("/static/app.js")
        self.assertEqual(js_response.status_code, 200)
        self.assertIn("fetchActivities", js_response.text)

    def test_signup_flow_and_duplicate_error_message(self):
        email = "ui-test@example.com"
        activity_name = "Chess Club"
        response = client.post(
            f"/activities/{quote(activity_name)}/signup",
            params={"email": email},
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["message"], f"Signed up {email} for {activity_name}")

        list_response = client.get("/activities")
        self.assertEqual(list_response.status_code, 200)
        activities_data = list_response.json()
        participants = [p.lower() for p in activities_data[activity_name]["participants"]]
        self.assertIn(email.lower(), participants)

        duplicate_response = client.post(
            f"/activities/{quote(activity_name)}/signup",
            params={"email": email},
        )
        self.assertEqual(duplicate_response.status_code, 400)
        self.assertEqual(
            duplicate_response.json()["detail"],
            "A student with this email is already signed up for the selected activity."
        )

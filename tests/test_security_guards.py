import copy
import unittest

from fastapi.testclient import TestClient

from src.app import app, activities


class SecurityGuardsTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.original_activities = copy.deepcopy(activities)

    def tearDown(self):
        activities.clear()
        activities.update(self.original_activities)

    def test_signup_blocks_sql_like_email_payload(self):
        response = self.client.post(
            "/activities/Chess Club/signup",
            params={"email": "student@example.com'; DROP TABLE users; --"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("Potential SQL payload", response.json()["detail"])
        self.assertNotIn(
            "student@example.com'; DROP TABLE users; --",
            activities["Chess Club"]["participants"],
        )

    def test_signup_blocks_sql_like_activity_name_payload(self):
        response = self.client.post(
            "/activities/Chess Club; SELECT * FROM users/signup",
            params={"email": "student@example.com"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("Potential SQL payload", response.json()["detail"])

    def test_signup_still_allows_normal_input(self):
        email = "new.student@mergington.edu"

        response = self.client.post(
            "/activities/Chess Club/signup",
            params={"email": email},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(email, activities["Chess Club"]["participants"])


if __name__ == "__main__":
    unittest.main()

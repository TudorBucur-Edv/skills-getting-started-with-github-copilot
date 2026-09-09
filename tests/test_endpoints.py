"""
Tests for FastAPI endpoints using the AAA (Arrange-Act-Assert) pattern.
"""

import pytest


class TestRoot:
    """Tests for GET / endpoint"""

    def test_root_redirects_to_static_index(self, client):
        """
        Arrange: TestClient is ready
        Act: Make GET request to /
        Assert: Should redirect to /static/index.html
        """
        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, client, clean_activities):
        """
        Arrange: Activities list with multiple entries is set up
        Act: Make GET request to /activities
        Assert: Response contains all activities with correct structure
        """
        # Arrange
        expected_keys = {"Chess Club", "Programming Class", "Gym Class"}

        # Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        assert response.status_code == 200
        assert set(data.keys()) >= expected_keys
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data

    def test_get_activities_returns_correct_participant_count(self, client, clean_activities):
        """
        Arrange: Chess Club has 2 participants
        Act: Make GET request to /activities
        Assert: Response shows correct participant count
        """
        # Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        assert response.status_code == 200
        assert len(data["Chess Club"]["participants"]) == 2
        assert "michael@mergington.edu" in data["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in data["Chess Club"]["participants"]

    def test_get_activities_participant_list_structure(self, client, clean_activities):
        """
        Arrange: Activities are set up with participants
        Act: Make GET request to /activities
        Assert: Participants are returned as a list
        """
        # Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        assert response.status_code == 200
        for activity_data in data.values():
            assert isinstance(activity_data["participants"], list)


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_successful(self, client, clean_activities, sample_email):
        """
        Arrange: New email that hasn't signed up yet
        Act: POST to /activities/Chess Club/signup with new email
        Assert: Status 200, participant is added to activity
        """
        # Arrange
        activity_name = "Chess Club"
        email = sample_email

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"
        assert email in clean_activities[activity_name]["participants"]

    def test_signup_adds_participant_to_list(self, client, clean_activities, sample_email):
        """
        Arrange: Activity with initial participants and new email
        Act: POST to signup
        Assert: New email is in participants list and count increased
        """
        # Arrange
        activity_name = "Programming Class"
        initial_count = len(clean_activities[activity_name]["participants"])

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={sample_email}"
        )

        # Assert
        assert response.status_code == 200
        updated_count = len(clean_activities[activity_name]["participants"])
        assert updated_count == initial_count + 1
        assert sample_email in clean_activities[activity_name]["participants"]

    def test_signup_activity_not_found(self, client, clean_activities, sample_email):
        """
        Arrange: Non-existent activity name
        Act: POST to /activities/NonExistent/signup
        Assert: Status 404, activity not found error
        """
        # Arrange
        activity_name = "Nonexistent Activity"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={sample_email}"
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_duplicate_email_rejected(self, client, clean_activities):
        """
        Arrange: Email already signed up for an activity
        Act: Try to signup the same email again
        Assert: Status 400, already signed up error
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already in Chess Club

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student is already signed up for this activity"

    def test_signup_multiple_activities_allowed(self, client, clean_activities, sample_email):
        """
        Arrange: Same student email, different activities
        Act: Sign up for Chess Club, then Programming Class
        Assert: Both signups succeed
        """
        # Arrange
        email = sample_email

        # Act
        response1 = client.post(f"/activities/Chess Club/signup?email={email}")
        response2 = client.post(f"/activities/Programming Class/signup?email={email}")

        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert email in clean_activities["Chess Club"]["participants"]
        assert email in clean_activities["Programming Class"]["participants"]


class TestUnregister:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_successful(self, client, clean_activities):
        """
        Arrange: Participant is signed up for an activity
        Act: DELETE /activities/Chess Club/unregister with their email
        Assert: Status 200, participant is removed
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already in Chess Club

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Removed {email} from {activity_name}"
        assert email not in clean_activities[activity_name]["participants"]

    def test_unregister_removes_from_participants(self, client, clean_activities):
        """
        Arrange: Activity with initial participants
        Act: DELETE to unregister one participant
        Assert: Participant count decreased and email not in list
        """
        # Arrange
        activity_name = "Programming Class"
        email = "emma@mergington.edu"
        initial_count = len(clean_activities[activity_name]["participants"])

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )

        # Assert
        assert response.status_code == 200
        updated_count = len(clean_activities[activity_name]["participants"])
        assert updated_count == initial_count - 1
        assert email not in clean_activities[activity_name]["participants"]

    def test_unregister_activity_not_found(self, client, clean_activities):
        """
        Arrange: Non-existent activity name
        Act: DELETE from /activities/NonExistent/unregister
        Assert: Status 404, activity not found error
        """
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "test@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_unregister_student_not_signed_up(self, client, clean_activities):
        """
        Arrange: Email not signed up for activity
        Act: Try to unregister that email
        Assert: Status 400, not signed up error
        """
        # Arrange
        activity_name = "Chess Club"
        email = "notstudent@mergington.edu"  # Not in Chess Club

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student is not signed up for this activity"

    def test_unregister_only_specified_participant_removed(self, client, clean_activities):
        """
        Arrange: Activity with multiple participants
        Act: Unregister one specific participant
        Assert: Only that participant removed, others remain
        """
        # Arrange
        activity_name = "Chess Club"
        email_to_remove = "michael@mergington.edu"
        email_to_keep = "daniel@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email_to_remove}"
        )

        # Assert
        assert response.status_code == 200
        assert email_to_remove not in clean_activities[activity_name]["participants"]
        assert email_to_keep in clean_activities[activity_name]["participants"]


class TestSignupAndUnregisterFlow:
    """Integration tests combining signup and unregister operations"""

    def test_signup_then_unregister(self, client, clean_activities, sample_email):
        """
        Arrange: New participant email
        Act: Sign up, then unregister
        Assert: Both operations succeed, participant state changes
        """
        # Arrange
        activity_name = "Chess Club"
        email = sample_email

        # Act - Signup
        signup_response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        assert email in clean_activities[activity_name]["participants"]

        # Act - Unregister
        unregister_response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )

        # Assert
        assert signup_response.status_code == 200
        assert unregister_response.status_code == 200
        assert email not in clean_activities[activity_name]["participants"]

    def test_signup_unregister_signup_again(self, client, clean_activities, sample_email):
        """
        Arrange: Participant email
        Act: Sign up, unregister, sign up again
        Assert: Can re-signup after unregistering
        """
        # Arrange
        activity_name = "Gym Class"
        email = sample_email

        # Act - First signup
        response1 = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert response1.status_code == 200

        # Act - Unregister
        response2 = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        assert response2.status_code == 200

        # Act - Sign up again
        response3 = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response3.status_code == 200
        assert email in clean_activities[activity_name]["participants"]

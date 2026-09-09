"""
Pytest configuration and fixtures for FastAPI app tests.
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Provide a TestClient for making HTTP requests to the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def clean_activities():
    """
    Reset activities to a clean state before each test.
    This ensures test isolation and prevents tests from affecting each other.
    """
    # Save original state
    original_activities = {
        key: {
            "description": value["description"],
            "schedule": value["schedule"],
            "max_participants": value["max_participants"],
            "participants": value["participants"].copy()
        }
        for key, value in activities.items()
    }
    
    # Yield to the test
    yield activities
    
    # Restore original state after test
    activities.clear()
    activities.update(original_activities)


@pytest.fixture
def sample_activity():
    """Provide sample activity data for tests."""
    return {
        "name": "Chess Club",
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    }


@pytest.fixture
def sample_email():
    """Provide a sample email for signup tests."""
    return "newstudent@mergington.edu"

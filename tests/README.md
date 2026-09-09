# Tests for Mergington High School Activities API

This directory contains pytest-based unit tests for the FastAPI backend application.

## Test Structure

Tests are organized using the **AAA (Arrange-Act-Assert)** pattern:
- **Arrange:** Set up test fixtures, initial data, and test client
- **Act:** Execute the endpoint being tested
- **Assert:** Verify response status, data, and side effects

## Test Organization

- `conftest.py` — Pytest configuration and shared fixtures
- `test_endpoints.py` — All endpoint tests organized by endpoint

### Test Classes

- **TestRoot** — Tests for GET / redirect endpoint
- **TestGetActivities** — Tests for retrieving all activities
- **TestSignup** — Tests for POST /activities/{activity_name}/signup endpoint
- **TestUnregister** — Tests for DELETE /activities/{activity_name}/unregister endpoint
- **TestSignupAndUnregisterFlow** — Integration tests combining multiple operations

## Running Tests

### Run all tests
```bash
pytest
```

### Run tests with verbose output
```bash
pytest -v
```

### Run specific test file
```bash
pytest tests/test_endpoints.py
```

### Run specific test class
```bash
pytest tests/test_endpoints.py::TestSignup
```

### Run specific test
```bash
pytest tests/test_endpoints.py::TestSignup::test_signup_successful
```

### Run with coverage report
```bash
pytest --cov=src --cov-report=html
```

## Fixtures

### `client`
Provides a FastAPI TestClient for making HTTP requests to the application.

```python
def test_example(client):
    response = client.get("/activities")
```

### `clean_activities`
Resets the activities dictionary to its original state before each test, ensuring test isolation.

```python
def test_example(clean_activities):
    # clean_activities is the activities dict in a clean state
```

### `sample_email`
Provides a sample email address for signup/unregister tests.

```python
def test_example(client, clean_activities, sample_email):
    response = client.post(f"/activities/Chess Club/signup?email={sample_email}")
```

### `sample_activity`
Provides sample activity data for reference.

```python
def test_example(sample_activity):
    activity_name = sample_activity["name"]
```

## Test Coverage

The test suite covers:

- ✅ GET / — redirect behavior
- ✅ GET /activities — data retrieval and participant listing
- ✅ POST /signup — successful signup, duplicate prevention, activity validation
- ✅ DELETE /unregister — successful removal, participant validation
- ✅ Integration flows — signup → unregister → signup again patterns

## Adding New Tests

When adding new tests:

1. Place them in the appropriate test class or create a new one
2. Follow the AAA pattern with clear comments
3. Use descriptive test names that explain what is being tested
4. Use the provided fixtures for setup
5. Use `clean_activities` fixture to ensure test isolation

Example:

```python
def test_my_feature(client, clean_activities, sample_email):
    """
    Arrange: Set up initial state
    Act: Perform the action
    Assert: Verify the result
    """
    # Arrange
    activity_name = "Chess Club"
    
    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={sample_email}")
    
    # Assert
    assert response.status_code == 200
```

## Dependencies

- `pytest` — Test framework
- `fastapi` — Web framework (imported from src/)
- `httpx` — HTTP client (used by TestClient)

Run `pip install -r requirements.txt` to install dependencies.

import pytest
from fastapi.testclient import TestClient
import requests
import os

# Import the FastAPI app instance
from app.main import app

@pytest.fixture(scope="session")
def client():
    """
    A fixture that provides a test client for the FastAPI app.
    This client will be used in tests to make requests to the endpoints.
    """
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="module")
def test_data():
    """
    A fixture to store and share data between test functions within a module.
    This is useful for passing IDs (like pool_id, stream_id) from one test to another.
    """
    return {}

@pytest.fixture(autouse=True)
def clear_emulator_data():
    """
    An auto-use fixture that runs before each test function.
    It sends a DELETE request to the Firestore emulator to clear all data,
    ensuring that each test runs in a clean, isolated environment.
    """
    # The emulator must be running for this to work
    emulator_host = os.getenv("FIRESTORE_EMULATOR_HOST")
    if emulator_host:
        # The URL to clear the database is specific to the Firestore emulator
        clear_db_url = f"http://{emulator_host}/emulator/v1/projects/{os.getenv('GOOGLE_CLOUD_PROJECT')}/databases/(default)/documents"
        try:
            requests.delete(clear_db_url)
        except requests.exceptions.ConnectionError as e:
            pytest.fail(f"Could not connect to Firestore emulator at {emulator_host}. Is it running? Error: {e}")
    yield

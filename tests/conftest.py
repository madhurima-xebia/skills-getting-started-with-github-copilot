import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture(scope="function")
def client():
    original_activities = copy.deepcopy(activities)
    test_client = TestClient(app)

    yield test_client

    activities.clear()
    activities.update(original_activities)

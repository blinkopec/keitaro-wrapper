from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.keitaro import KeitaroClient

BASE = "https://keitaro.test"


@pytest.fixture
def client() -> Generator[TestClient]:
    with TestClient(app) as test_client:
        app.state.keitaro = KeitaroClient(base_url=BASE, api_key="test-key")
        yield test_client
        app.state.keitaro = None

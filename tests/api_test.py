import os
import requests
import pytest


@pytest.fixture
def api_url():
    """Base URL for the API under test. Can be overridden via API_BASE_URL env var."""
    return os.getenv("API_BASE_URL", "http://localhost:8000").rstrip("/")


@pytest.fixture
def http_get():
    """Wrapper around requests.get so tests can monkeypatch it easily."""
    return requests.get


# first test is, if /live returns {"status": "alive"}
def test_alive(http_get, api_url):
    response = http_get(f"{api_url}/live")
    assert response.status_code == 200
    assert response.json() == {"status": "alive"}


# second test is, if /ready returns {"status": "ready"} or {"status": "not_ready"}
def test_ready(http_get, api_url):
    response = http_get(f"{api_url}/ready")
    assert response.status_code == 200
    assert response.json() in ({"status": "ready"}, {"status": "not_ready"})

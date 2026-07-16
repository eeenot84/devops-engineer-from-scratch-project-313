import pytest

from main import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_ping_success(client):
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.data.decode() == "pong"

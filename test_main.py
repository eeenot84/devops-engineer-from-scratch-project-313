import pytest


@pytest.fixture
def client(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    monkeypatch.setenv("BASE_URL", "https://short.io")
    monkeypatch.delenv("SENTRY_DSN", raising=False)

    import database

    database.reset_engine()

    import main

    application = main.create_app()
    application.config["TESTING"] = True
    with application.test_client() as test_client:
        yield test_client


def test_ping_success(client):
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.data.decode() == "pong"


def test_create_link(client):
    response = client.post(
        "/api/links",
        json={
            "original_url": "https://example.com/long-url",
            "short_name": "exmpl",
        },
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data["id"] == 1
    assert data["original_url"] == "https://example.com/long-url"
    assert data["short_name"] == "exmpl"
    assert data["short_url"] == "https://short.io/r/exmpl"


def test_create_link_duplicate_short_name(client):
    payload = {
        "original_url": "https://example.com/long-url",
        "short_name": "exmpl",
    }
    assert client.post("/api/links", json=payload).status_code == 201
    response = client.post("/api/links", json=payload)
    assert response.status_code == 409
    assert response.get_json() == {"error": "Entity with short_name already exists"}


def test_list_links(client):
    client.post(
        "/api/links",
        json={"original_url": "https://example.com/1", "short_name": "one"},
    )
    client.post(
        "/api/links",
        json={"original_url": "https://example.com/2", "short_name": "two"},
    )
    response = client.get("/api/links")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2
    assert data[0]["short_name"] == "one"
    assert data[1]["short_name"] == "two"


def test_get_link(client):
    created = client.post(
        "/api/links",
        json={"original_url": "https://example.com/long-url", "short_name": "exmpl"},
    ).get_json()
    response = client.get(f"/api/links/{created['id']}")
    assert response.status_code == 200
    assert response.get_json() == created


def test_get_link_not_found(client):
    response = client.get("/api/links/999")
    assert response.status_code == 404
    assert response.get_json() == {"error": "Not Found"}


def test_update_link(client):
    created = client.post(
        "/api/links",
        json={"original_url": "https://example.com/old", "short_name": "old"},
    ).get_json()
    response = client.put(
        f"/api/links/{created['id']}",
        json={"original_url": "https://example.com/new", "short_name": "new"},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["original_url"] == "https://example.com/new"
    assert data["short_name"] == "new"
    assert data["short_url"] == "https://short.io/r/new"


def test_update_link_not_found(client):
    response = client.put(
        "/api/links/999",
        json={"original_url": "https://example.com/new", "short_name": "new"},
    )
    assert response.status_code == 404
    assert response.get_json() == {"error": "Not Found"}


def test_update_link_duplicate_short_name(client):
    client.post(
        "/api/links",
        json={"original_url": "https://example.com/1", "short_name": "one"},
    )
    second = client.post(
        "/api/links",
        json={"original_url": "https://example.com/2", "short_name": "two"},
    ).get_json()
    response = client.put(
        f"/api/links/{second['id']}",
        json={"original_url": "https://example.com/2", "short_name": "one"},
    )
    assert response.status_code == 409
    assert response.get_json() == {"error": "Entity with short_name already exists"}


def test_delete_link(client):
    created = client.post(
        "/api/links",
        json={"original_url": "https://example.com/long-url", "short_name": "exmpl"},
    ).get_json()
    response = client.delete(f"/api/links/{created['id']}")
    assert response.status_code == 204
    assert response.data == b""
    assert client.get(f"/api/links/{created['id']}").status_code == 404


def test_delete_link_not_found(client):
    response = client.delete("/api/links/999")
    assert response.status_code == 404
    assert response.get_json() == {"error": "Not Found"}

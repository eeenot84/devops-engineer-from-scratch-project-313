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
    assert response.headers["Content-Range"] == "links 0-2/2"


def _seed_links(client, count: int) -> None:
    for i in range(count):
        client.post(
            "/api/links",
            json={
                "original_url": f"https://example.com/{i}",
                "short_name": f"name-{i}",
            },
        )


def test_list_links_range_first_page(client):
    _seed_links(client, 12)
    response = client.get("/api/links", query_string={"range": "[0,10]"})
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 10
    assert data[0]["short_name"] == "name-0"
    assert data[9]["short_name"] == "name-9"
    assert response.headers["Content-Range"] == "links 0-10/12"
    assert response.headers["Accept-Ranges"] == "links"


def test_list_links_range_skip(client):
    _seed_links(client, 11)
    response = client.get("/api/links", query_string={"range": "[5, 10]"})
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 5
    assert data[0]["short_name"] == "name-5"
    assert data[4]["short_name"] == "name-9"
    assert response.headers["Content-Range"] == "links 5-10/11"


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


def test_cors_preflight(client):
    response = client.options(
        "/api/links",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Content-Type",
        },
    )
    assert response.status_code in (200, 204)
    assert response.headers.get("Access-Control-Allow-Origin") == "http://localhost:5173"


def test_cors_exposes_content_range(client):
    client.post(
        "/api/links",
        json={"original_url": "https://example.com/1", "short_name": "one"},
    )
    response = client.get(
        "/api/links",
        headers={"Origin": "http://localhost:5173"},
    )
    assert response.status_code == 200
    assert response.headers.get("Access-Control-Allow-Origin") == "http://localhost:5173"
    expose = response.headers.get("Access-Control-Expose-Headers", "")
    assert "Content-Range" in expose


def test_redirect_short_link(client):
    client.post(
        "/api/links",
        json={"original_url": "https://example.com/target", "short_name": "go"},
    )
    response = client.get("/r/go")
    assert response.status_code == 302
    assert response.headers["Location"] == "https://example.com/target"


def test_redirect_short_link_not_found(client):
    response = client.get("/r/missing")
    assert response.status_code == 404
    assert response.get_json() == {"error": "Not Found"}

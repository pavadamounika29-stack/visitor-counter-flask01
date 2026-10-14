import fakeredis
import pytest
import redis

from app import create_app


@pytest.fixture
def client():
    app = create_app(redis_client=fakeredis.FakeRedis(decode_responses=True))
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_index_increments_counter(client):
    first = client.get("/")
    second = client.get("/")
    assert first.status_code == 200
    assert b"Visitor Counter" in first.data
    assert b">1<" in first.data
    assert b">2<" in second.data


def test_api_visits_starts_at_zero(client):
    response = client.get("/api/visits")
    assert response.status_code == 200
    assert response.get_json() == {"visits": 0}


def test_api_visits_after_page_views(client):
    client.get("/")
    client.get("/")
    client.get("/")
    assert client.get("/api/visits").get_json()["visits"] == 3


def test_health_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok", "redis": "up"}


class BrokenRedis:
    """Stands in for a Redis server that cannot be reached."""

    def ping(self):
        raise redis.exceptions.ConnectionError("redis is down")


def test_health_degraded_when_redis_down():
    app = create_app(redis_client=BrokenRedis())
    response = app.test_client().get("/health")
    assert response.status_code == 503
    assert response.get_json()["redis"] == "down"


def test_version_endpoint(client):
    response = client.get("/version")
    body = response.get_json()
    assert response.status_code == 200
    assert "version" in body
    assert "environment" in body

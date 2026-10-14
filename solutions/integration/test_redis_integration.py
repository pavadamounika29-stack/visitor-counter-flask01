"""Integration tests: run the application against a REAL Redis server.

Not collected by the default `pytest` run (pytest.ini -> testpaths = tests).
Run explicitly:  REDIS_HOST=... REDIS_PORT=... pytest integration
"""
import os

import pytest
import redis

from app import create_app


@pytest.fixture
def real_redis():
    client = redis.Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", "6379")),
        decode_responses=True,
    )
    client.delete("visits")
    yield client
    client.delete("visits")


def test_health_reports_redis_up(real_redis):
    response = create_app(redis_client=real_redis).test_client().get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok", "redis": "up"}


def test_counter_is_stored_in_redis(real_redis):
    client = create_app(redis_client=real_redis).test_client()
    client.get("/")
    client.get("/")
    assert client.get("/api/visits").get_json() == {"visits": 2}
    assert real_redis.get("visits") == "2"

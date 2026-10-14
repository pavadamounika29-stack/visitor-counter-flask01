"""Visitor Counter - a small Flask + Redis application used throughout the
Jenkins & GitHub Actions CI/CD course.

The application is intentionally simple so that students can focus on the
CI/CD pipeline rather than on application code.
"""
import os
import socket

import redis
from flask import Flask, jsonify, render_template

__version__ = "1.0.0"


def create_app(redis_client=None):
    """Application factory.

    A Redis client can be injected (tests pass a fakeredis instance);
    otherwise one is created from REDIS_HOST / REDIS_PORT.
    """
    app = Flask(__name__)

    if redis_client is None:
        redis_client = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", "6379")),
            socket_connect_timeout=2,
            decode_responses=True,
        )
    app.config["REDIS"] = redis_client

    app_version = os.getenv("APP_VERSION", __version__)
    environment = os.getenv("APP_ENV", "dev")

    @app.route("/")
    def index():
        visits = redis_client.incr("visits")
        return render_template(
            "index.html",
            visits=visits,
            version=app_version,
            environment=environment,
            hostname=socket.gethostname(),
        )

    @app.route("/api/visits")
    def visits():
        count = int(redis_client.get("visits") or 0)
        return jsonify(visits=count)

    @app.route("/health")
    def health():
        try:
            redis_client.ping()
            redis_status = "up"
        except redis.exceptions.RedisError:
            redis_status = "down"
        status = "ok" if redis_status == "up" else "degraded"
        code = 200 if status == "ok" else 503
        return jsonify(status=status, redis=redis_status), code

    @app.route("/version")
    def version():
        return jsonify(version=app_version, environment=environment)

    return app

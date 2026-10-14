# Visitor Counter (Flask + Redis)

The class application for the course **Jenkins & GitHub Actions – Enterprise CI/CD and DevSecOps**.

A small Flask web app that counts page visits in Redis. It is intentionally simple, so the
course can focus on the CI/CD pipelines around it.

| Endpoint      | Returns                                           |
|---------------|---------------------------------------------------|
| `/`           | HTML page with the visit counter                  |
| `/api/visits` | `{"visits": <n>}`                                 |
| `/health`     | `{"status": "ok", "redis": "up"}` (503 if Redis is down) |
| `/version`    | `{"version": ..., "environment": ...}`            |

## Run locally

```bash
docker build -t visitor-counter:local .
docker compose up -d          # web on http://localhost:5000 + redis
docker compose down
```

## Test

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements-dev.txt
flake8 app tests integration wsgi.py
pytest --cov=app                                  # unit tests (Redis faked)
REDIS_HOST=localhost REDIS_PORT=6379 pytest integration   # needs a real Redis
```

## Repository layout

| Path | Purpose |
|------|---------|
| `app/` | Flask application |
| `tests/` | Unit tests (fakeredis) |
| `integration/` | Integration tests against a real Redis (you add them in Lab 10; reference in `solutions/integration/`) |
| `Dockerfile`, `docker-compose.yml` | Image and deployment |
| `sonar-project.properties`, `.coveragerc`, `pytest.ini` | Quality configuration |
| `solutions/` | Reference versions of the final Jenkinsfile and GitHub Actions workflows |

In the labs you write your own `Jenkinsfile` and `.github/workflows/*.yml` step by step.
Look in `solutions/` only if you are stuck.

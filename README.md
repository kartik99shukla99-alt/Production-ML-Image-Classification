# Production ML Image Classification API

A containerized image classification API prototype built with FastAPI, Redis, Celery, Prometheus, Grafana, and Flower. The API validates uploaded images, hashes them for Redis caching, and queues cache misses for asynchronous processing.

> **Prototype note:** The current classifier returns fixed sample labels after a simulated 1.5-second inference delay. It is not a trained image classification model. The AWS architecture in [`docs/architecture.md`](docs/architecture.md) is a proposed production design; those AWS services are not deployed by this repository.

## Features

- `POST /v1/predictions` accepts JPEG, PNG, or WebP images up to 5 MB.
- SHA-256 image hashing and Redis prediction caching with a 24-hour TTL.
- Asynchronous cache-miss processing with Celery and Redis.
- Redis memory limit of 2 GB with `allkeys-lru` eviction in Compose.
- Prometheus API/cache metrics, a provisioned Grafana dashboard, and Flower task monitoring.
- API health and readiness endpoints.

## Requirements

- Docker Desktop with Docker Compose
- Git (to clone the repository)

## Run with Docker Compose

Clone the repository and enter its directory:

```powershell
git clone https://github.com/kartik99shukla99-alt/Production-ML-Image-Classification.git
cd Production-ML-Image-Classification
```

Create the local environment file from the example:

```powershell
Copy-Item .env.example .env
```

Start the services:

```powershell
docker compose up --build
```

The API and background worker use Compose's internal Redis hostname automatically. Keep `.env` local; it is excluded from Git.

To stop the services, press `Ctrl+C`, then run:

```powershell
docker compose down
```

To also remove the persistent Redis and Grafana data volumes:

```powershell
docker compose down --volumes
```

## Service URLs

| Service | URL | Purpose |
| --- | --- | --- |
| FastAPI Swagger UI | http://localhost:8000/docs | Explore and call the API |
| Liveness | http://localhost:8000/health | Check that the API process responds |
| Readiness | http://localhost:8000/ready | Check API and Redis connectivity |
| Prometheus metrics | http://localhost:8000/metrics | Scraped API and cache metrics |
| Prometheus UI | http://localhost:9090 | Query metrics and inspect targets |
| Grafana | http://localhost:3000 | View the provisioned dashboard |
| Flower | http://localhost:5555 | Inspect Celery workers and tasks |

Grafana's initial credentials are `admin` / `admin`; change the password when prompted. Flower is exposed on localhost for development and has no authentication configured in this prototype.

## Submit and check a prediction

In Swagger at http://localhost:8000/docs, call `POST /v1/predictions` with an image file. The response is normally `202 Accepted` with a task ID and `PENDING` status. Poll the returned task ID:

```text
GET /v1/predictions/{task_id}
```

The status progresses to `SUCCESS` with prediction results, or `FAILED` if processing fails. Submitting the same image again should return cached results immediately with `SUCCESS`.

Accepted image types: `image/jpeg`, `image/png`, and `image/webp`. Maximum upload size: 5 MB.

## Local development without Docker

Create and activate a virtual environment, install dependencies, and start Redis separately:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

Start a Celery worker in a second terminal after activating the same environment:

```powershell
celery -A app.tasks.classification:celery_app worker --loglevel=info --pool=solo
```

For local development, `.env.example` defaults to Redis at `localhost:6379`. Start a local Redis instance before running the API and worker.

## Monitoring

The Compose stack provisions Prometheus scraping and Grafana dashboards from `monitoring/`. Useful metrics include HTTP request rate and latency, cache hits and misses, model inference count, Redis exporter metrics, and Celery task/queue metrics. Load-testing is optional; install Locust separately with `pip install locust` and provide a local test image under `tests/test_images/` before running `locust -f tests/load_test.py`.

## Project structure

```text
app/
  api/                 FastAPI routes
  cache/               Redis cache and Prometheus cache counters
  services/            Image validation and file storage
  tasks/               Celery classification task
monitoring/            Prometheus rules and Grafana provisioning/dashboard
docs/                  Proposed AWS architecture
tests/                 Optional Locust load test
docker-compose.yml     Local multi-container stack
Dockerfile             API and worker image
```

## Security and data notes

- Do not commit `.env`, credentials, uploaded images, or private datasets.
- Uploaded files are stored temporarily under `data/uploads` for worker processing; that directory is ignored by Git.
- The proposed 30-day structured prediction logging and AWS retention architecture are documented design goals. This local prototype does not implement a durable 30-day audit store or CloudWatch integration.
- Configure authentication, TLS, and access controls before exposing the services beyond a trusted local development environment.

## License

No license file is currently included. All rights reserved unless the repository owner adds a license.

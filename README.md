# Delivery Service

Delivery Service is a Python backend for courier dispatching and order delivery simulation.  
It combines a clean domain core with multiple adapters (HTTP, Kafka, PostgreSQL, gRPC) and runs periodic background jobs to assign and move couriers.

## What This Service Does

- Stores couriers, orders, and courier storage capacity.
- Creates orders from incoming basket-confirmed Kafka events.
- Resolves order destination coordinates via an external Geo gRPC service.
- Continuously assigns the best available courier to created orders.
- Continuously moves couriers toward assigned orders and marks orders as completed.

## Architecture at a Glance

The project follows a layered / hexagonal style:

- `core/domain`: business entities and domain rules (`Courier`, `Order`, `StoragePlace`, dispatcher logic).
- `core/application/use_cases`: command/query handlers orchestrating domain + repositories.
- `core/ports`: interfaces for repositories and external services.
- `adapters/incoming`: inbound interfaces (HTTP and Kafka consumer).
- `adapters/out`: outbound integrations (PostgreSQL repositories, gRPC geo client).
- `api/`: FastAPI app wiring, DB session setup, and background schedulers.

## Main Runtime Flow

1. A basket confirmation event is consumed from Kafka topic `baskets.events`.
2. The service calls Geo gRPC to convert `street` into `(x, y)` coordinates.
3. A new order is created in Postgres with status `CREATED`.
4. A scheduler job (`assign_orders_job`) runs every second and assigns created orders to the best free courier.
5. Another job (`move_couriers_job`) runs every second and moves couriers toward delivery points until orders are completed.

## Tech Stack

- Python 3.11+
- FastAPI + Uvicorn
- SQLAlchemy (sync engine) + PostgreSQL
- FastStream Kafka router
- gRPC client for Geo service
- APScheduler for background jobs
- Pytest + Testcontainers for tests
- `uv` for dependency management

## Quick Start (Docker Compose)

### Prerequisites

- Docker + Docker Compose
- External Docker network named `microservices` (required by `docker-compose.yml`)

Create the shared network once:

```bash
docker network create microservices
```

Start the app and Postgres:

```bash
docker compose up --build
```

After startup:

- API: `http://localhost:8082`
- Swagger UI: `http://localhost:8082/docs`

## Local Development Run

1. Install dependencies:

```bash
uv sync --dev
```

2. Create `.env` from the example and adjust DB host/port for local execution (usually `localhost:5433` if Postgres is started via Compose):

```bash
cp env.example .env
```

3. Start API:

```bash
uv run python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8082
```

## External Dependencies

`docker-compose.yml` starts only this service and Postgres.  
Two integrations are expected to exist in the same Docker network:

- Kafka broker reachable as `kafka:19092`
- Geo gRPC service reachable as `geo:5004`

Without them:

- Kafka-driven order creation will not work.
- Creating orders via use case path that calls Geo service will fail.

## HTTP API (Current Surface)

Base path: `/api/v1`

- `POST /couriers` - create courier (`name`, `speed`).
- `GET /couriers` - list couriers.
- `POST /orders` - create a test order (internal stub endpoint).
- `GET /orders/active` - list non-completed orders.

## Project Structure

```text
api/                              # FastAPI app, settings, DB, background jobs
src/delivery/core/domain/         # Domain model and business rules
src/delivery/core/application/    # Use cases (commands/queries)
src/delivery/core/ports/          # Ports/interfaces
src/delivery/adapters/incoming/   # HTTP and Kafka consumers
src/delivery/adapters/out/        # Postgres repos and gRPC clients
tests/                            # Unit + integration tests
docker-compose.yml
Dockerfile
```

## Testing

Run all tests:

```bash
uv run pytest -q
```

Note: integration tests use Testcontainers and require Docker.

## Notes

- Database tables are created on application startup from SQLAlchemy metadata.
- This repository currently uses a simulation-style dispatch loop (1-second scheduler ticks) for assignment and movement.

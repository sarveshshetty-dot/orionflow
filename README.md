# OrionFlow

A scalable, production-ready distributed workflow orchestration platform. OrionFlow allows you to define background workflows with interdependent tasks, provides real-time tracking, automatic retries with exponential backoff, cron-based scheduling, and a fleet of distributed task workers.

## Architecture

```text
+-------------------+      +-------------------+
|  Next.js (Web UI) |----->|  FastAPI (API)    |
|  Tailwind/Zustand |<-----|  WebSockets       |
+-------------------+      +--------+----------+
                                    |
                                    |  (REST / WS)
                                    v
                            +-----------------+
                            | PostgreSQL (DB) | <-- Core source of truth
                            +-----------------+     (Workflows, Tasks, Runs)

+---------------+           +-----------------+
| Worker Fleet  | <=======> | Redis (Queue &  |
| (Python)      |    POP    |  Pub/Sub Logs)  |
+---------------+           +-----------------+
        ^                            ^
        | executes tasks             |
        v                            |
+---------------+                    |
| Scheduler     | -------------------+
| (Python)      |    ENQUEUE
+---------------+
```

### Components:
- **API Server** (`app.api.main`): Exposes REST routes and WebSocket logic for tracking.
- **Worker Node** (`app.workers.main`): Distributed worker script that polls Redis, executes Python functions, logs success/failure to the database, and streams real-time logs through Redis Pub/Sub.
- **Workflow Engine** (`app.workflows.engine`): State machine logic that evaluates transitions and pushes the next job step into Redis when a prior step finishes.
- **Scheduler** (`app.scheduler.main`): CRON evaluator script polling active schedules to initiate runs.
- **Frontend**: A gorgeous dark-themed Next.js dashboard mimicking premium SaaS products. Uses Zustand for WebSocket state hydration.

## Running Locally

1. Make sure you have Docker and Docker Compose installed.
2. Ensure ports `8000`, `3000`, `6379`, and `5432` are available.
3. Open a terminal and run:

```bash
docker-compose up --build
```

You can now navigate to:
- **Frontend Dashboard:** http://localhost:3000
- **Backend Swagger:** http://localhost:8000/docs

### Default Environment Info
- Postgres uses `postgres` / `postgrespassword` on port `5432`
- Redis uses port `6379`

*Note*: The frontend relies on Next.js `standalone` mode for the Docker build, to ensure the smallest possible container image. Make sure the `next.config.js` sets `output: "standalone"` if you rebuild. (By default in Next 14, standard build is used unless configured - the Dockerfile handles compiling).

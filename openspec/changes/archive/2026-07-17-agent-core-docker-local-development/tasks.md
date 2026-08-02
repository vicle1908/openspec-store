## 1. Docker local development assets

- [x] 1.1 Add a `Dockerfile` for local development using pinned Python and uv versions.
- [x] 1.2 Add `compose.yaml` with app + Postgres services and pinned images.
- [x] 1.3 Add `.env.docker.example` with local DSN defaults.
- [x] 1.4 Add a helper script for common Docker dev flows.

## 2. Runtime alignment

- [x] 2.1 Accept `DBOS_DATABASE_URL` alongside `POSTGRES_URL` during durable execution validation.
- [x] 2.2 Add tests that assert the Docker assets stay pinned and the env validation accepts DBOS DSNs.

## 3. Documentation

- [x] 3.1 Update `README.md` with local Docker startup instructions.
- [x] 3.2 Update `docs/configuration.md` to explain DBOS/Postgres DSN compatibility.
- [x] 3.3 Update `examples/README.md` to point to the Docker local dev workflow.

## 4. Verification

- [x] 4.1 Validate the new OpenSpec change.
- [x] 4.2 Run Python tests and Docker asset checks.

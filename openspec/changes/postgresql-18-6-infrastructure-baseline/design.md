# Design: PostgreSQL 18.6 infrastructure baseline

## Decision

Use the immutable patch-level image tag `postgres:18.6-trixie` for every PostgreSQL service in the agent-core local Compose stack and the agent-harness integration fixture.

## Service Matrix

| Surface | Before | After | Reason |
|---|---|---|---|
| agent-core primary DB | `postgres:18.4-trixie` | `postgres:18.6-trixie` | latest PostgreSQL 18 Trixie patch |
| agent-core scheduler DB | `postgres:18.4-trixie` | `postgres:18.6-trixie` | same ecosystem baseline |
| Langfuse metadata DB | `postgres:16` | `postgres:18.6-trixie` | supported by Langfuse v4 minimum >=15 |
| MLflow metadata DB | `postgres:16` | `postgres:18.6-trixie` | SQLAlchemy PostgreSQL backend, no major ceiling |
| agent-harness integration fixture | `postgres:18.4-trixie` | `postgres:18.6-trixie` | test production parity |

## Compatibility and Rollback

- PostgreSQL 18.6 is a patch/minor update within the PostgreSQL 18 baseline for the primary and scheduler databases.
- The Langfuse and MLflow databases use their own logical databases and existing volumes; the image replacement does not alter service connection strings.
- Existing Compose volumes are intentionally preserved. This change does not perform an in-place data migration.
- Existing PostgreSQL 17 rollback language in historical migration specifications is retained as historical operational context.

## Verification

1. Validate Compose with `docker compose -f compose.yaml config --quiet`.
2. Pull `postgres:18.6-trixie` and run an isolated `pg_isready`/`SHOW server_version` smoke container.
3. Run agent-core Docker-local tests, full pytest, Ruff, strict mypy, and `uv lock --check`.
4. Run agent-harness PostgreSQL fixture and full suite.
5. Run OpenSpec strict validation across the store.
6. Sweep active infrastructure surfaces for stale `18.4` and `postgres:16` references.

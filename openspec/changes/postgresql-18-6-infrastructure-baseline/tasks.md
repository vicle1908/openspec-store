# Tasks: PostgreSQL 18.6 infrastructure baseline

## Implementation

- [x] Upgrade the four agent-core Compose PostgreSQL images to `postgres:18.6-trixie`.
- [x] Upgrade the agent-harness PostgreSQL integration fixture to `postgres:18.6-trixie`.
- [x] Update agent-core Docker image tests.
- [x] Update agent-core README, AGENTS.md, and observability documentation.
- [x] Update current normative OpenSpec references from 18.4 to 18.6.

## Verification

- [x] Verify Docker Hub lists `postgres:18.6-trixie` as the latest official Trixie PostgreSQL 18 image.
- [x] Validate agent-core Compose configuration.
- [x] Pull and smoke-test PostgreSQL 18.6 with `pg_isready` and `SHOW server_version`.
- [x] Run agent-core Docker-local tests.
- [x] Run agent-core full test suite.
- [x] Run agent-core Ruff, format, strict mypy, lock, and diff checks.
- [x] Run agent-harness PostgreSQL fixture test and full suite.
- [x] Run OpenSpec strict validation across the store.
- [x] Sweep active code, docs, and specs for stale PostgreSQL 18.4 / `postgres:16` references.

## Completion Evidence

- agent-core first-party baseline commit: `e1975dc`.
- agent-core all-service upgrade commit: `f0f4abf`.
- agent-harness fixture upgrade commit: `8d5238b`.
- Docker Hub verified `postgres:18.6-trixie`; smoke server reported PostgreSQL 18.6.

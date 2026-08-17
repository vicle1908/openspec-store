# Proposal: Upgrade ecosystem container images

## Why

The workspace containerized infrastructure uses image tags that have drifted from current releases, include floating `latest` tags that break reproducibility, and contain a PostgreSQL 16→18 incompatibility for the Langfuse/MLflow databases. A Langfuse 3→4 major version jump is available.

Existing deployments may contain PostgreSQL 16 data directories. This workstation has no Langfuse/MLflow PostgreSQL volumes, so local verification uses fresh PostgreSQL 18 initialization. The migration procedure must nevertheless preserve and handle PG16 volumes safely for other environments.

Redis 8 is **evaluated but deferred** for the Langfuse stack — Langfuse v4.11.0 pins Redis 7 in its official Compose baseline. Redis 8 compatibility is not proven.

## What Changes

- Define a container image governance policy: exact immutable tags required for stateful services, floating tags prohibited except with documented digest exception.
- Define a PostgreSQL 16→18 migration strategy for observability databases (preserve old volumes, create versioned PG18 volumes, `pg_dump`/`pg_restore` when data must be retained).
- Upgrade go-microservices infrastructure images where patches are available.
- Pin floating tags for stateful services (ClickHouse, MLflow, MinIO) with documented rationale.
- Upgrade Langfuse 3→4 (server + worker as atomic unit, environment/config changes expected). ClickHouse pinned to 25.12 line, Redis retained at 7.
- Evaluate Redis 8 upgrade (deferred for Langfuse; evaluated for standalone services only).
- Update base images in Go Dockerfiles and distroless runtimes.
- Update test assertions, verification scripts, and CI service containers as needed.

## Scope

Primarily infrastructure, tests, verification scripts, specifications, and documentation. Application configuration or compatibility code may change where required by a major-version migration. Archived OpenSpec changes and generated Graphify outputs SHALL NOT be modified.

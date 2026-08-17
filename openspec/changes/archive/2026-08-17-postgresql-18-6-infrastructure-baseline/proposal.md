# Proposal: Upgrade the PostgreSQL infrastructure baseline to 18.6

## Why

PostgreSQL 18.6 is the latest available PostgreSQL 18 patch release on Docker Hub. The workspace still contained first-party `18.4-trixie` references and third-party service `postgres:16` images in the agent-core local infrastructure. Keeping mixed, stale image tags weakens reproducibility and means infrastructure is not aligned to the latest approved PostgreSQL 18 patch release.

## What Changes

- Upgrade all four agent-core Compose PostgreSQL services to `postgres:18.6-trixie`.
- Upgrade the agent-harness PostgreSQL integration fixture to `postgres:18.6-trixie`.
- Align agent-core documentation and Docker image tests.
- Align all current normative OpenSpec references from PostgreSQL 18.4 to 18.6.
- Preserve historical archived changes and PostgreSQL 17 rollback history.

## Compatibility Evidence

- Docker Hub official `library/postgres:18.6-trixie` was verified as the latest non-floating Trixie PostgreSQL 18 image, pushed 2026-08-13 and listed as updated 2026-08-15.
- Langfuse self-hosting documentation states PostgreSQL >=15 is supported for v4 and recommends PostgreSQL 16; PostgreSQL 18.6 satisfies the minimum and is a compatible forward patch/minor baseline.
- MLflow backend-store documentation supports PostgreSQL through SQLAlchemy without a PostgreSQL major-version ceiling; PostgreSQL 18.6 is compatible with the documented PostgreSQL backend-store contract.

## Scope

This is an infrastructure image and documentation alignment. No application schema or data migration is introduced. Existing fresh-start and no-data-migration semantics remain unchanged.

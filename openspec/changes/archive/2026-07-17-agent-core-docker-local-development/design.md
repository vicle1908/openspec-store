## Context

agent-core needs a repeatable local Docker workflow that mirrors the durable execution setup used by the runtime:

- app container builds from a pinned Python base image
- Postgres container uses the current official stable major/minor tag
- local env vars expose the internal DSNs needed by DBOS and memory
- the setup should not rely on legacy workspace paths

## Goals

- Provide a one-command local dev stack.
- Keep image versions explicit and pinned.
- Keep secrets in local env files, not in committed YAML.
- Make the setup easy to run, stop, and test.

## Non-Goals

- Production deployment orchestration
- Kubernetes/Helm manifests
- Publishing images to a registry
- Remote CI deployment automation

## Decisions

1. **Docker Compose is the local dev entry point**
   - The stack uses `compose.yaml` and a helper script for common flows.

2. **Images are pinned, not floating**
   - Python base image: `python:3.14.5-slim-trixie`
   - Postgres image: `postgres:18.4-trixie`
   - This keeps local development reproducible while using the current stable releases verified from Docker Hub.

3. **Postgres 18 volume mounts target `/var/lib/postgresql`**
   - The official Postgres 18 images now use major-version-specific data directories.
   - Mounting `/var/lib/postgresql/data` creates an unused mount boundary and the container refuses to start.
   - The local stack therefore mounts the persistent volume at `/var/lib/postgresql`.

4. **DBOS bootstrap accepts either `POSTGRES_URL` or `DBOS_DATABASE_URL`**
   - Local Docker workflows can set either secret name without failing validation.

5. **The app container keeps source mounted and the venv outside the mount**
   - This preserves a stable editable install during local development.

6. **The app container runs as a non-root user with a Docker healthcheck**
   - The image creates an `agent` user for local runtime commands.
   - The Dockerfile includes a lightweight import healthcheck so local container health is visible without adding a production supervisor.

## Risks

- The Compose stack introduces a new local workflow that must be kept aligned with docs and tests.
- If the pinned base images drift, the local dev Docker assets must be updated together.

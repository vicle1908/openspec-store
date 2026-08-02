## Why

agent-core can run locally with uv today, but it lacks a first-class Docker Compose setup for developers who want a pinned app + Postgres stack with durable execution enabled from the start.

## What Changes

- Add a local Docker development stack for agent-core with pinned base images.
- Use current official images for the local stack: `python:3.14.5-slim-trixie` and `postgres:18.4-trixie`.
- Add a Dockerfile, Compose file, and example env file for local development.
- Document the local Docker workflow in README and configuration docs.
- Add validation tests that assert the Docker assets stay pinned and aligned.

## Impact

- Affected code: Dockerfile, compose.yaml, .env.docker.example, helper script, settings validation.
- Affected docs: README.md, docs/configuration.md, examples/README.md.
- Affected specs: new local Docker development spec.

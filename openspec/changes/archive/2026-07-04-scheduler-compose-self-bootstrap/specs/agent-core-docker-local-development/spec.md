# agent-core-docker-local-development (Delta)

> **Capability:** `agent-core-docker-local-development`
> **Owning change:** `scheduler-compose-self-bootstrap`

## Why

This delta adds `ripgrep` to the `apt-get install` line of the scheduler `Dockerfile`. `ripgrep` is the canonical search tool used by `code_daily_scan` to grep Swift (iOS) and Kotlin (Android) source trees during the daily scan. Without it, the daily scan fails with `FileNotFoundError: 'rg'` after `code-daily-scan` source is updated to require it.

Earlier debugging in the TDT session discovered this gap via a manual `apt-get install ripgrep` inside the running container — an anti-pattern because ephemeral container installs are lost on the next `docker compose up --build`. The right fix is to bake the dependency into the image.

---

## ADDED Requirements

### Requirement: ripgrep is installed in the scheduler image

The scheduler `Dockerfile`'s `apt-get install` line MUST include `ripgrep` (the `rg` binary) alongside `ca-certificates curl gcc git libpq-dev tzdata`.

#### Scenario: ripgrep available on PATH inside container

- **WHEN** the scheduler container is running
- **THEN** `uv run rg --version` exits 0 and prints the `ripgrep` version
- **AND** `which rg` resolves to `/usr/bin/rg`

### Requirement: Test asserts ripgrep install is not regressed

The test `tests/test_docker_local_dev.py::test_dockerfile_matches_compose_versions` MUST assert that the `apt-get install` line contains the literal string `ripgrep`.

#### Scenario: Regression test catches Dockerfile change

- **WHEN** an operator removes `ripgrep` from the `apt-get install` list
- **THEN** `pytest tests/test_docker_local_dev.py::test_dockerfile_matches_compose_versions` fails
- **AND** the failure message identifies the missing dependency

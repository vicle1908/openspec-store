# Compose correction verification report

Date: 2026-08-23 (Asia/Ho_Chi_Minh)

## Result

Committed the immediate canonical Compose correction slice in commit
`4a1d25ff3861455094ada0535224e0fb9b033eb8` from clean canonical commit
`a41cfbe` in the fresh top-level worktree
`/Users/androidteam/Developer/tdt-observability-compose-correction`.

Committed source paths:

- `deploy/docker-compose.yaml`
- `tests/test_compose_models.py`

The top-level Compose `name: tdt-observability` override was removed. Project
identity is now controlled by an explicit `docker compose -p` invocation;
rendering with `-p tdt-observability-stack` produced project name
`tdt-observability-stack` and volume names
`tdt-observability-stack_lgtm-data` and
`tdt-observability-stack_postgres-data`.

## Ownership and preservation

Before editing, canonical root and nested candidate ownership was compared.
The canonical root owns an `otel-lgtm` + Postgres base profile; nested
foundation/integrated candidates own a separate `otel-gateway` model. Existing
canonical dirty source and generated Graphify files in
`/Users/androidteam/Developer/tdt-observability` were preserved. No nested
candidate worktree, other repository, or `openspec-store/tasks.md` was edited.

Existing canonical image pins were preserved, including
`grafana/otel-lgtm:0.29.0`, `postgres:18.6-alpine`, and the existing
Langfuse Redis default `redis:8.10.0-alpine`; no source-level inconsistency
justified a Redis change in this canonical slice.

## Collector readiness contract

The new focused model asserts the canonical root uses the supported in-image
`otel-lgtm` healthcheck (`CMD curl -f http://localhost:3000/api/health`).
It also documents and tests the nested distroless `otel-gateway` contract as
an explicit external disposable probe against `http://otel-gateway:13133/`,
forbidding exec healthchecks that require `wget` or `curl`. No wget/curl
healthcheck was added to a distroless Collector image, and the root profile has
no `otel-gateway` service to modify.

## Code intelligence

- Read repository `AGENTS.md` and `CLAUDE.md`.
- GitNexus canonical file impact before source edit:
  `gitnexus impact --repo /Users/androidteam/Developer/tdt-observability --uid File:deploy/docker-compose.yaml --direction upstream --depth 3 --include-tests`
  -> 0 upstream dependents, 0 affected processes/modules, LOW risk.
- GitNexus existing helper impact before test-helper edit consideration:
  `gitnexus impact --repo /Users/androidteam/Developer/tdt-observability --uid Function:tests/test_otel_spec.py:_load_module_from_path --direction upstream --depth 3 --include-tests`
  -> 2 direct test-factory callers, 0 affected processes, LOW risk. The helper
  was not modified; the new model is self-contained.
- Fresh worktree GitNexus index: 648 nodes, 1,222 edges, 39 flows.
- Pre-commit `detect_changes` with absolute fresh-worktree repo:
  `gitnexus detect-changes --repo /Users/androidteam/Developer/tdt-observability-compose-correction --scope staged --limit 200`
  -> 2 files, 27 symbols, 0 affected processes, LOW risk.
- Generated Graphify files were intentionally excluded from the commit after
  required `graphify update .`; they remain as unstaged generated changes.

## Verification commands and results

- `uv sync --locked` -> passed; installed locked project/dev environment.
- `uv lock --check` -> passed.
- `uv run --locked pytest tests/test_compose_models.py -q` -> 11 passed.
- `uv run --locked pytest tests -q` -> 136 passed.
- `uv run --locked ruff check src tests` -> passed.
- `uv run --locked mypy src` -> passed: no issues in 17 source files.
- `git diff --check` -> passed.
- `docker compose -p tdt-observability-stack -f ... config --quiet` for base,
  services, Langfuse, MLflow, and full profiles -> all passed (daemon-free
  structural rendering).
- Explicit JSON render -> passed; project and volume names matched the explicit
  `tdt-observability-stack` value.
- `graphify update .` -> passed; regenerated graph artifacts in
  `graphify-out/`.

## Runtime blocker

Docker CLI/Compose is installed (Compose v5.4.0, Docker client 29.7.2), but
`docker info` failed because the Docker daemon socket
`/Users/androidteam/.docker/run/docker.sock` was unavailable. Image builds,
container startup, in-image healthchecks, external disposable Collector probes,
network readiness, and telemetry delivery were not run and must remain reported
as runtime-blocked.

## Final worktree

The commit contains only the two source paths listed above. The worktree still
contains only generated Graphify changes from the required update:
`graphify-out/.graphify_labels.json`,
`graphify-out/.graphify_labels.json.sig`,
`graphify-out/GRAPH_REPORT.md`, `graphify-out/graph.json`,
`graphify-out/manifest.json`, and untracked `graphify-out/graph.html`.

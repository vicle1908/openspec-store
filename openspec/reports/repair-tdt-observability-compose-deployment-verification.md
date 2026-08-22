# repair-tdt-observability-compose-deployment verification

Date: 2026-08-22
Verdict: **partial / blocked for runtime execution**

This report records the current OpenSpec apply state for
`repair-tdt-observability-compose-deployment`. Structural validation and the
static implementation slices are green, but the Docker daemon is unavailable,
the observability candidate is isolated from the canonical dirty checkout, and
several runtime/migration/rollback tasks remain intentionally unchecked.

## OpenSpec state

```text
openspec status --change repair-tdt-observability-compose-deployment --json --store openspec-store
schema: spec-driven
planning artifacts: complete

openspec instructions apply --change repair-tdt-observability-compose-deployment --json --store openspec-store
41/89 tasks complete; 48 remain

openspec validate repair-tdt-observability-compose-deployment --strict --store openspec-store
valid

openspec validate --all --strict --store openspec-store
376 passed, 0 failed

openspec doctor --store openspec-store
root/store references healthy
```

The active change directory and the two corrected PostgreSQL Purpose specs are
uncommitted store work. The unrelated pre-existing report
`openspec/reports/openspec-store-verification-2026-08-21.md` remains untouched.

## Accepted repository evidence

### agent-core

- Canonical integrated commit: `d390ae0e281a139906b8c56af5eb8d4c4ea3a0c6`.
- Owner report: `docs/repair-compose-verification.md` in the owner worktree.
- 94 focused tests, Ruff, format, strict mypy, lock validation, and two
  daemon-free Compose renders passed.
- Runtime image build, PostgreSQL bootstrap, gateway delivery, and rollback
  liveness remain blocked by Docker.

### tdt-scheduler

- Canonical integrated commits: `310bf87`, `d54faf5`, `b1bd8de`, `05e38a2`;
  owner branch source was verified at `48080954c983611fa8bca6f9ad830e2bc8afd103`.
- Owner report: `docs/tdt-scheduler-compose-repair-report.md` in the scheduler
  worktree.
- Seven focused tests, shell/Python checks, two daemon-free Compose renders, and
  diff checks passed.
- Docker build, health, hosted workload, backup runtime, and rollback gates are
  blocked; `tdt-sheets` and `ai-review` remain read-only inputs.

### agent-harness and tdt-core

- agent-harness already used `postgres:18.6-trixie`; 44 checkpoint/bootstrap
  tests passed and no source change was needed.
- Canonical `tdt-core/tests/test_paths_typed.py` covers the kind-first runtime
  path, explicit absolute root, and relative-root rejection contract;
  `PYTHONPATH=src uv run --project /Users/androidteam/Developer/tdt-core
  pytest tests/test_paths_typed.py -q` passed 25 tests under Python 3.14.5.

### tdt-observability integrated candidate

Dedicated integration worktree:
`/Users/androidteam/Developer/tdt-observability/tdt-observability-integrated`.
The canonical checkout was not overwritten because it contains user-owned dirty
Docker edits and nested worker worktrees.

Accepted candidate commits:

- `a59e12e` foundation Compose/Dockerfile candidate.
- `dde2663` four OTel gateway configurations.
- `a9b0ded` coordinator lifecycle/evidence contract.
- `212c596` integration correction: base gateway, literal network keys,
  canonical Dockerfile paths, versioned volumes, MLflow local artifacts, and the
  dedicated full-profile gateway override.
- `ffe6131`, `bafeef4` image-manifest evidence and official source links.
- `768ed69` static-gap follow-up: locked-venv/build-context regressions,
  exact inventory/mount/volume assertions, value-free environment corrections,
  and the bounded static-gap report.
- `f376b69` MinIO completion gate: `langfuse-web`/`langfuse-worker` now gate on
  `minio-init` via `service_completed_successfully`; the fixed sleep is replaced
  by a bounded 30-attempt retry that fails closed; MinIO credentials are
  injected via the service `environment:` block and referenced as `$$` shell
  variables; `otel-gateway` receives `LANGFUSE_PUBLIC_KEY`/`LANGFUSE_SECRET_KEY`
  with empty defaults so the Collector `${env:...}` providers resolve; misleading
  `LANGFUSE_INIT_*` implemented-claims corrected (task 6.4 key initialization
  remains unimplemented).
- `beaf62c` observability runtime defect repair: self-contained venv, explicit
  external `tdt-core` context selection, no-cache image build, and non-root
  service smoke.
- `3cc856e` observability entrypoint supervision evidence: same image digest for
  both services and non-zero child-failure propagation.
- `b5975a1` agent-core runtime report: fresh/retained PostgreSQL, app imports,
  non-root health, and owner-only teardown.
- `dbc9938` scheduler external-worktree build/layout repair and runtime report.

Static evidence:

- Four `docker compose --env-file deploy/tools.env ... config --quiet` profile
  renders passed without a daemon.
- `PYTHONPATH=src uv run --no-sync pytest tests/test_compose_models.py -q`:
  67 passed after `768ed69`; 87 passed after `f376b69` (20 new MinIO-gate and
  gateway-credential regressions).
- Fresh ad-hoc verification against `f376b69` (temporary `hermes-verify-*.py`
  script under the system temp dir, removed after use; this is ad-hoc
  verification, not canonical suite green): 26/26 checks passed — commit and
  worktree state, MinIO completion-gate and bounded-entrypoint assertions,
  `$$` escaping preservation, credential-via-environment, gateway key
  injection, the focused suites (87 + 178 passed), Ruff clean, four daemon-free
  Compose renders, and Docker daemon confirmed unavailable so runtime
  acceptance (tasks 8–10) remains blocked.
- `PYTHONPATH=src uv run --no-sync pytest tests/test_dockerfile_paths.py
  tests/test_otel_gateway_configs.py tests/deployment -q`: 178 passed after
  `768ed69`.
- `uv run --no-sync ruff check src/tdt_observability/deployment`: clean.
- Repository-wide test Ruff still reports pre-existing worker-test lint drift;
  strict mypy was unavailable in the newly created disposable environment.
- The observability runtime repair reports 101 focused tests before the final
  entrypoint follow-up; the follow-up reports 107 focused tests, Ruff/mypy
  clean, and both child-failure probes exiting 23.

### OTel gateway evidence recovery

Pi source commit: `cbe6a788914611d1e2a400dfa028d4162bde28c9`.
Coordinator-recovered report commit: `a4ca11b` at
`tdt-observability-backends/deploy/evidence/tdt-observability-gateway-static-gates.md`.
The four profile configs passed 73 focused tests, Ruff/format/mypy evidence, and
exact Collector `0.159.0` validation; the frozen legacy fixture was rejected by
the same validator. The original dispatch could not deliver `worker_done` after
repeated HTTP 504 responses, so the report is explicitly marked as coordinator
recovery and contains no gateway source changes.

## Image re-resolution

On 2026-08-22, `docker buildx imagetools inspect` and official registry tag APIs
confirmed the selected tags remain current pullable releases with amd64/arm64
manifests. Redis is deliberately pinned to the latest Alpine Redis 8 tag rather
than the Debian `redis:latest` alias.

| Image | Tag | Manifest digest |
|---|---|---|
| Python | `python:3.14.7-slim-trixie` | `sha256:ce40764625a4ff50df3548277632e7f96c4e77fe75fa848aae9885476e7df5a4` |
| uv | `ghcr.io/astral-sh/uv:0.12.5` | `sha256:e85be844203885286c60ffad8a858d48afb6c5a5c237ca0e67f12e74b8f174b1` |
| PostgreSQL | `postgres:18.6-trixie` | `sha256:06cad38a5d9f5d24b4d83d86def30795d5e4b757fedbf5281172b576dedcd941` |
| Grafana LGTM | `grafana/otel-lgtm:0.31.0` | `sha256:f1e548c20c99d2678744be9d90955c0ab208ecc273db2a7a0b5dc5673d0b57fd` |
| OTel Collector | `otel/opentelemetry-collector-contrib:0.159.0` | `sha256:1f2c54a30e713fac6b3ae77a1ec84010c2007e29ced8ec666214fc2f6739c1cc` |
| Langfuse web | `langfuse/langfuse:4.16.0` | `sha256:e8459747001aa0da1bdecdc5d46c48d37c2e9b4c2c99743b27efeb2872e0583` |
| Langfuse worker | `langfuse/langfuse-worker:4.16.0` | `sha256:b4490170d5bc18e873f7ca7c3edad5af16022156487a5c47c328d571a9063dc1` |
| Redis | `redis:8.10.1-alpine` | `sha256:becdda6c7f4b3fb42e42fd7f120bbf5c54c4caaaf16f26da24e4563d2c1f0576` |
| ClickHouse | `clickhouse/clickhouse-server:26.7.5.10-alpine` | `sha256:0a45b864c73322d4360dea1973ee9b77f29c51af1242ad2d47409908071fa56e` |
| MinIO | `minio/minio:RELEASE.2025-09-07T16-13-09Z` | `sha256:14cea493d9a34af32f524e538b8346cf79f3321eff8e708c1e2960462bd8936e` |
| MinIO Client | `minio/mc:RELEASE.2025-08-13T08-35-41Z` | `sha256:a7fe349ef4bd8521fb8497f55c6042871b2ae640607cf99d9bede5e9bdf11727` |
| MLflow | `ghcr.io/mlflow/mlflow:v3.15.1` | `sha256:ea84a0b879f08b35a6f22f22b294024413e780b8fc978eecf5f760ac16cc9ce5` |

## Blockers and open worker evidence

Docker Compose is `v5.4.0`, but the Docker daemon is unavailable at
`unix:///Users/androidteam/.docker/run/docker.sock`. Image builds, database
bootstrap/migrations, health probes, Langfuse/MLflow ingestion, ClickHouse
queries, duplicate bounds, hosted workload, backup/restore, rollback liveness,
and cleanup runtime evidence remain blocked.

Agy’s preflight report is now present at
`openspec/reports/repair-tdt-observability-compose-deployment-preflight.md` and
tasks 1.1–1.6 have been reconciled. The canonical observability checkout still
contains unrelated dirty Docker edits and generated Graphify/worktree state;
these were preserved. No credentials, Docker resources, host volumes, launchd
services, or unrelated reports were changed.

## Docker Desktop diagnosis

Read-only Docker CLI, socket, process, launchd, recent-log, Orca UI, and
daemon-free Compose checks were completed in candidate commit
`1eaa3a09a6401130bc44e8eb995bfa063916bb21`:

[`docker-desktop-diagnostics.md`](/Users/androidteam/Developer/tdt-observability/docker-desktop-diagnostics/deploy/evidence/docker-desktop-diagnostics.md)

The selected `desktop-linux` context is coherent, Docker CLI 29.7.2 and Compose
5.4.0 are installed, and all Compose configuration merges return exit 0. The
operator subsequently started Docker Desktop, but the runtime flap follow-up
shows repeated five-minute Desktop/VM/Engine restarts with orderly terminated-
signal shutdowns, no OOM/fatal/dockerd-crash markers, and a strong correlation
with `autoPauseTimeoutSeconds=300`. The current host may run only supervised,
checkpointed, retryable Docker work until the session remains stable beyond the
observed timeout. See:

[`docker-desktop-runtime-flap.md`](/Users/androidteam/Developer/tdt-observability/docker-desktop-diagnostics/deploy/evidence/docker-desktop-runtime-flap.md)

## Disposition

Keep the active change open at `41/89`. The candidate observability commits are
ready for a controlled canonical integration once the dirty checkout owner
authorizes conflict reconciliation. Do not archive or claim global success until
Docker Desktop is available, the runtime gates are recaptured against the same
commit matrix, the Agy preflight/matrix evidence is recovered, and task 11.8
reviews and commits only the approved store paths.

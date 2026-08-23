# repair-tdt-observability-compose-deployment verification

Date: 2026-08-23 (updated)
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
49/90 tasks complete; 41 remain

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
- `56cc275` (2026-08-23) removed the broken `wget` healthcheck from the
  distroless `otel-gateway` service in both `docker-compose.yaml` (base,
  affects all 4 profiles) and `docker-compose.mlflow.yaml` (mlflow + full
  overlays). The `otel/opentelemetry-collector-contrib:0.159.0` image has no
  `/bin/sh`, `wget`, or `curl`, so the exec-based healthcheck could never
  succeed. Gateway readiness MUST be proven at runtime by an external probe of
  the Collector `health_check` extension on `0.0.0.0:13133`; the coordinator's
  bounded owner-health wait treats absent Docker health as passing, which is
  necessary but NOT sufficient. No service depends on `otel-gateway` via
  `service_healthy`. Post-fix evidence: 4/4 daemon-free Compose renders pass,
  89 model tests pass, 75 coordinator contract tests pass, `git diff --check`
  clean. GitNexus default `detect_changes`: no uncommitted tracked changes
  (untracked `graphify-out/graph.html` excluded). GitNexus `main...HEAD`
  compare: 35 files / 849 symbols / 29 processes / critical risk — expected
  branch-level impact for this broad candidate branch, not evidence that the
  two-file healthcheck fix itself is critical.
- `9f4c54e` (2026-08-23) adds the external gateway readiness contract. The
  coordinator runs a disposable pinned Alpine 3.20 probe on the run-scoped
  observability network and queries `http://otel-gateway:13133/` with bounded
  retries and explicit timeouts; readiness does not rely on Docker health
  status. `gateway_readiness` is recorded in the acceptance manifest with a
  closed JSON-schema contract and redacted structured evidence. The Alpine OCI
  index digest is `sha256:d9e853e87e55526f6b2917df91a2115c36dd7c696a35be12163d44e6e2a4b6bc`,
  with linux/amd64 and linux/arm64 manifests. Evidence: 79 deployment tests,
  deployment Ruff, owned test lint, schema parse, and four daemon-free Compose
  renders passed.

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
`1eaa3a09a6401130bc44e8eb995bfa063916bb21`. The diagnostic evidence is retained
on the `docker-desktop-diagnostics` branch (HEAD `2b5de12`) in the
tdt-observability repository:

- `git show docker-desktop-diagnostics:deploy/evidence/docker-desktop-diagnostics.md`
- `git show docker-desktop-diagnostics:deploy/evidence/docker-desktop-runtime-flap.md`

The selected `desktop-linux` context is coherent, Docker CLI 29.7.2 and Compose
5.4.0 are installed, and all Compose configuration merges return exit 0.

### 2026-08-23 flap follow-up

The operator started Docker Desktop multiple times. Each session lasted
approximately 4–5 minutes before an orderly terminated-signal shutdown. The
latest bounded snapshot (2026-08-23T03:30+07:00) shows:

- Docker daemon unavailable: socket absent, no Docker Desktop or backend
  processes running.
- Backend log: `engine linux/virtualization-framework shutdown requested
  (cancel cause: terminated signal received)` followed by `starting graceful
  shutdown` and `init POST /shutdown`.
- Electron log: `AbortError: Request aborted` in `createWindowManager`
  immediately preceding each backend shutdown.
- No OOM, fatal, or dockerd-crash markers found.
- The initiating component remains undetermined; neither daemon crash nor OOM
  is supported by the evidence.

Settings changes attempted during this session (autoPauseTimeoutSeconds,
UseResourceSaver, AllowBetaFeatures, AllowExperimentalFeatures) were all
restored to their original values. These raw-JSON edits are an unsupported
approach — Docker Desktop may ignore or overwrite them — and the flap persisted
identically across every combination tried, so they did not remediate the issue.
No persistent Docker Desktop remediation was retained. The flap root cause
remains unresolved.

**Runtime acceptance (tasks 8–10) remains blocked until Docker Desktop
maintains a stable session beyond the observed ~5-minute window.**

## 2026-08-23 coordinated worker wave

The bounded follow-up worker wave produced these additional, independently
verified results without changing OpenSpec task checkboxes:

- `tdt-observability`: isolated source commit
  `4a1d25ff3861455094ada0535224e0fb9b033eb8` is preserved on branch
  `obs-compose-correction`. It removes the root Compose `name:` override and
  adds 11 focused project-name/Collector-readiness tests; uv tests, Ruff,
  mypy, daemon-free profile renders, Graphify update, and low-risk GitNexus
  detection passed. The durable report is
  `openspec/reports/tdt-observability-compose-correction.md`. This narrow
  canonical-root slice intentionally retains its existing Redis
  `8.10.0-alpine`; the integrated candidate's approved latest inventory remains
  Redis `8.10.1-alpine` at `56cc275`, so latest-image promotion is still not
  complete for the canonical root.
- `tdt-scheduler`: source commit
  `54203800f29ab594223ea6546b0d8b870194f348` is preserved on branch
  `scheduler-pydantic-import`. Its Dockerfile now constrains
  `pydantic>=2.13.4,<2.14` and `pydantic-settings>=2.14.1,<2.15` after the
  `code_daily_scan.cli` serializer import failure; the seven-workload
  integrity gate and owner layout remain intact. Docker build/runtime evidence
  remains unavailable.
- `webhook-receiver`: source commit
  `f3f904ded6d14108227cb198967e3b85963be685` adds side-effect-free circuit
  breaker and session health snapshots with two focused tests. The launchd
  label `com.tdt.webhook-receiver` is running from the canonical
  `$HOME/.tdt/deployments/webhook-receiver` root, listens only on
  `127.0.0.1:8080`, and `/health` returned HTTP 200 healthy with ai-review
  reachable. Evidence is retained at
  `$HOME/.tdt/deployments/webhook-receiver/state/deployment-report.md`;
  pre-existing uv.lock/Graphify dirt remains uncommitted. The deployment
  report captured the pre-commit source identity `baa49981`; the current source
  commit is `f3f904ded6d14108227cb198967e3b85963be685`, so an exact-commit
  provenance acceptance run must redeploy this service after the source commit.
- `ai-review`: the launchd label `com.tdt.ai-review` is running on
  `127.0.0.1:8090` from the repository-documented
  `$HOME/Developer/tdt/deployments/ai-review` root. `/health/full` returned
  `status=degraded` because optional OmniRoute/Kimi providers are unavailable;
  the deployment manifest is retained at
  `$HOME/Developer/tdt/deployments/ai-review/state/deployment-manifest.json`.
  The deploy script also generated a broad TDT dependency workspace and
  unrelated lockfile dirt; those paths are preserved and are not treated as
  change-owned commits.

The temporary Orca worktrees were removed after preserving their source
commits/reports. No Docker resources, stateful volumes, unrelated launchd
labels, or unrelated OpenSpec reports were removed.

The current authoritative Docker settings store still reports
`UseResourceSaver=false`, `AutoPauseTimeoutSeconds=300`, and
`AutoPauseTimedActivitySeconds=30`, but the Docker socket remains absent and
`docker info` cannot connect. This is a current runtime blocker, not proof that
the Compose models or image inventory are invalid.

## 2026-08-23 static-readiness and Docker-diagnosis follow-up

The integrated candidate static readiness work is preserved on branch
`observability-static-readiness` through commits
`bef9a34f97129be252e1b8d3833fefb3ebf798ca`,
`c48a62f104b685d2bfb0f488d0bc47761c1bcbb5`, and
`f42b4c5d1872e792533acbe483a338f84b51ff2b`. The latest static slice adds
atomic poller/config-cycle readiness, idle-safe collector scan/flush heartbeats,
offset/inode rotation handling, explicit executable `/entrypoint.sh
--readiness` healthchecks, the supported `LANGFUSE_INIT_*` bootstrap/preflight
contract, Redis 8.10.1 documentation, and focused regressions. The worker
reported 224 focused tests, four daemon-free Compose renders, Ruff, and clean
diff checks; Docker image/runtime, authenticated Langfuse trace, and lock/mypy
environment gaps remain open. Generated Graphify output is intentionally
unstaged.

The scheduler static hardening was integrated into canonical `tdt-scheduler` as
`cb1746e0e6f3a54ab057e96a7db76b389912f746` from the integration-clean source
commit `d52375519e8bb1579aded35ec23f1392e39445d6`. It hardens bounded,
redacted PostgreSQL readiness before DBOS initialization and preserves the
Pydantic pin repair; static tests, nine lock checks, Compose renders, syntax,
and diff checks passed. Docker image build stopped during dependency download
with BuildKit `Unavailable/EOF`; live scheduler health/workload/backup remain
blocked.

The ai-review source health correction is canonical at
`706a46e21cbcf0b8ddf9caadd3ba9518532b00e5`; focused health tests and Ruff pass.
Disabled optional reviewers now report `not needed` and healthy, while enabled
but failing providers remain degraded through shared CLI/HTTP classification.
The launchd service still runs the old deployment source `033de308` because the
documented deploy script defaults to the separate `$HOME/Developer/tdt/ai-review`
checkout; exact post-commit redeploy remains blocked by that workspace-root
containment/provenance mismatch.

Docker Desktop recovered twice after transient Virtualization.framework storage
attachment failures and supplied the official diagnostic bundle
`/var/folders/zw/k5ybx0c55rs88r9d09kxly8w0000gp/T/6501AB09-CA89-4DF7-ADE9-9E13CCBC244B/20260823015935.zip`.
The Docker.raw sparse disk was inspected as structurally intact; no prune,
reset, volume deletion, or resource cleanup was performed. A live inventory
captured four existing integrated observability containers, 23 images, 8 CPUs,
and 16 GiB configured memory. Those containers auto-restarted from the stale
integrated Compose file and still carry the invalid `wget` gateway healthcheck
(`tdt-observability-otel-gateway-1`), so they are evidence of a previously
started stack, not acceptance of the corrected readiness contract. Do not
restart or remove them until the corrected candidate project identity,
healthcheck, and exact resource ownership are reviewed.

Official Docker documentation confirms `docker desktop diagnose` is the
supported CLI diagnostic path and warns that Docker.raw backup does not replace
separate named-volume backups; the documented macOS Docker.raw path is
`$HOME/Library/Containers/com.docker.docker/Data/vms/0/data/Docker.raw`.

The latest static/readiness commits are now reconciled as follows:

- tdt-observability integrated candidate: `120d769c32b79b4f2e66835a068b897da1c56d69`
  plus readiness-command/flush-error follow-up `8a9e73fe1095b517096a0e559ac97567586f6210`
  and evidence clarification `f42b4c5d1872e792533acbe483a338f84b51ff2b`. Static
  tests, Ruff, four renders, and diff checks pass; the integrated project-name
  correction and authoritative image-fallback/owner-startup wiring remain in
  the dependent coordinator task.
- tdt-scheduler canonical commit: `cb1746e0e6f3a54ab057e96a7db76b389912f746`,
  reproduced from allowlisted integration commit `d52375519e8bb1579aded35ec23f1392e39445d6`.
  This commit contains bounded redacted database readiness, DBOS ordering
  tests, Pydantic pins, scheduler documentation, and no Graphify paths. The
  Docker image build still failed with BuildKit `Unavailable/EOF` while Docker
  Desktop flapped.
- ai-review canonical commits: `bbceaa2`, `706a46e21cbcf0b8ddf9caadd3ba9518532b00e5`.
  Focused health tests pass and optional-provider semantics are now honest, but
  the launchd runtime still reflects old source `033de308`; exact post-commit
  redeploy remains blocked because the deployment script defaults to the
  separate `$HOME/Developer/tdt/ai-review` checkout.

The current live Docker inventory, when the engine briefly recovered, contained
four existing `tdt-observability` containers from the integrated candidate:
`otel-gateway`, `otel-lgtm`, `health-poller`, and `log-collector`; 23 images,
8 CPUs, and approximately 16 GiB configured memory. The gateway container was
still using the stale `wget` healthcheck from the old running Compose model,
while the corrected source contract now uses an explicit `/entrypoint.sh
--readiness` command for first-party daemons and an external probe for the
distroless gateway. This inventory is preserved evidence only; no container,
network, image, or volume was removed or restarted by the coordinator.

## Disposition

Keep the active change open at `50/90` (`40` remain). The candidate observability commits are
ready for a controlled canonical integration once the dirty checkout owner
authorizes conflict reconciliation. Do not archive or claim global success until
Docker Desktop is available, the runtime gates are recaptured against the same
commit matrix, the Agy preflight/matrix evidence is recovered, and task 11.8
reviews and commits only the approved store paths.

## 2026-08-23 post-restart static coordinator candidate

The preserved coordinator worktree
`/Users/androidteam/Developer/tdt-observability/observability-coordinator-readiness`
produced and independently rechecked the following owner commits:

- `bda825ba66ac3cc618cfc81f3234226ec41d5350` — fail-closed coordinator
  evidence, required image/credential interpolation, real Git dirt and
  read-only input file identities, scoped Compose commands, owner-project
  rendering, and manifest roots/resources/images/networks.
- `c5ef814a32970e8ceeabd651e77d39f22c89c651` — reject pre-existing runtime or
  observability networks whose Docker labels do not match the current owner and
  project.
- `456592f226ae09156f55b5c0473c7aa2f5347fda` — cleanup of changed-test Ruff
  diagnostics and import/style drift.

These commits were cherry-picked into the isolated integration candidate
`/Users/androidteam/Developer/tdt-observability/tdt-observability-integrated`,
whose current HEAD is `a3188df7c038472ec2484d7a753c36b98474b964`. The candidate
has exactly the expected source, Compose, and test commits plus preserved
unstaged Graphify output; no Graphify path was staged by the coordinator.

Fresh daemon-free verification against the integrated candidate:

```text
PYTHONPATH=src uv run --no-project pytest \
  tests/deployment/test_coordinator_evidence_contract.py \
  tests/test_compose_models.py -q
203 passed in 6.97s

PYTHONPATH=src uv run --no-project ruff check \
  src/tdt_observability/deployment/__main__.py \
  src/tdt_observability/deployment/evidence.py \
  src/tdt_observability/deployment/stack.py \
  tests/deployment/test_coordinator_evidence_contract.py \
  tests/test_compose_models.py
All checks passed

python3 -m compileall -q src
exit 0

env TDT_OBSERVABILITY_NETWORK=tdt-observability-static-verify \
  TDT_CORE_CONTEXT=/Users/androidteam/Developer/tdt-core \
  TDT_HOST_HOME=/Users/androidteam/.tdt \
  GRAFANA_ADMIN_USER=<redacted-test-user> \
  GRAFANA_ADMIN_PASSWORD=<redacted-test-password> \
  docker compose --env-file deploy/tools.env \
  -f deploy/docker-compose.yaml config --quiet
base_render_exit=0
```

After the report/task reconciliation, the selected change validated strictly,
the full store validated at `375 passed, 0 failed`, and `openspec doctor` reported
healthy root/store references. These are structural OpenSpec gates only and do
not promote the active implementation to runtime readiness.

The full profile render also passed in the worker’s explicit-scope verification;
its output contained no secret values. This is structural/static evidence only.
It does not satisfy p95/p99 resource measurement, Docker host-gateway HTTP
reachability, owner-project startup, rerun/partial-start recovery, image pull or
build, backend migration, authenticated Langfuse trace, duplicate-detection,
rollback, cleanup, or post-commit host-service provenance.

Current Docker recheck after the restart is `blocked`: `docker context show`
returns `desktop-linux`, but `$HOME/.docker/run/docker.sock` is absent,
`docker info`, `docker ps`, network/volume/image inventory calls fail with
daemon `ENOENT`, `docker desktop status` reports that Docker Desktop is not
running, no Docker backend process is present, and
`launchctl print gui/502/com.docker.helper` reports `state = not running`.
The prior stale `wget` gateway-healthcheck observation remains historical and
cannot be recaptured while the daemon is down. No Docker resource, network,
volume, image, launchd service, or credential was mutated.

The post-restart host-service read-only review also remains blocked for exact
post-commit provenance: webhook-receiver owner HEAD is
`f3f904ded6d14108227cb198967e3b85963be685` but its retained deployment report
records pre-commit `baa49981`; ai-review owner HEAD is
`706a46e21cbcf0b8ddf9caadd3ba9518532b00e5` while launchd still resolves the
separate legacy source tree at `033de308` and port `8090` has no listener (launchd
exit `126`). No redeploy was authorized or performed.

The active change therefore remains `50/90` with `40` open tasks and a
`partial / blocked` verdict. The static coordinator commit is not a runtime
acceptance or archive-readiness claim. Preserve the unrelated active
`repair-mcp-router-servers` state, untracked store worktrees, and Graphify dirt.

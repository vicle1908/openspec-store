## Context

See `proposal.md` for motivation and scope. The current deployment is split across independent repositories but the archived consolidation tried to materialize agent-core, scheduler, PostgreSQL, and observability backends in one tdt-observability Compose project.

That topology currently has these design constraints:

- `agent-core` already owns the shared runtime PostgreSQL service, its durable volume, and initializers for `agent_core`, `tdt_scheduler`, `tdt_scheduler_dbos_sys`, and `agent_harness`.
- `tdt-scheduler` has an owner-maintained image and Compose definition with a workspace-root build context and host-coupled workload inputs.
- `tdt-observability` owns health polling, log collection, dashboards, and the intended observability backend deployment, but its committed image context is not buildable and its current uncommitted repair mixes project-venv and system-Python installs.
- Host-native webhook-receiver and ai-review remain launchd-owned (`com.tdt.webhook-receiver` running on `127.0.0.1:8080` from `$HOME/.tdt/deployments/webhook-receiver` and `com.tdt.ai-review` running on `127.0.0.1:8090` from `$HOME/Developer/tdt/deployments/ai-review`); the containerized poller must cross the Docker host boundary via supported host gateway mappings.
- The canonical TDT filesystem layout is kind-first: `$TDT_HOME/<kind>/<app>/<name>`.
- Docker Compose cannot provide `depends_on` health ordering across independent projects.
- The repositories cannot be updated atomically by one PR, and unrelated dirty Graphify output plus current tdt-observability Docker edits must be preserved.
- The exact image baseline was resolved from primary upstream releases and registry manifests on 2026-08-22. Every selected tag except the unavailable newer MinIO source release has a pullable official image with both `linux/amd64` and `linux/arm64` manifests.
- Authoritative Docker Desktop settings confirm `UseResourceSaver=false`, `AutoPauseTimeoutSeconds=300`, and `AutoPauseTimedActivitySeconds=30`, but the Docker socket (`unix:///Users/androidteam/.docker/run/docker.sock`) remains absent due to observed ~4–5 minute session flap terminations; runtime acceptance remains blocked without invalidating static planning models.

The following main-spec patterns are reused rather than reinvented: agent-core ownership of runtime PostgreSQL, scheduler ownership of its image and service, exact stateful image pins, versioned PostgreSQL volumes, one authoritative trace route, canonical TDT home resolution, non-root Python images, one-shot initializer completion gates, and run-scoped readiness evidence.

## Goals / Non-Goals

**Goals:**

- Give operators one supported command while retaining owner-local Compose and Dockerfile definitions.
- Make every supported profile buildable and runnable from clean owner worktrees.
- Keep runtime PostgreSQL ownership and bootstrap in agent-core.
- Route all containerized producer telemetry through one stable OTel gateway.
- Make base, Langfuse, MLflow, and full profiles independently valid and explicitly evidenced.
- Use the user's selected latest-image policy, including Redis 8, with compatibility deviations visible and fail-closed.
- Preserve canonical host data paths and least-privilege mounts.
- Make multi-repository rollout additive, identity-bound, and independently reversible.

**Non-Goals:**

- One Compose project or one cross-repository PR.
- Production Kubernetes, GitOps, public ingress, or multi-host scheduling.
- Containerizing launchd-owned webhook-receiver or ai-review.
- Changing application telemetry semantics or capturing new sensitive content.
- Automatically deleting old volumes, images, networks, host data, or launchd jobs.
- Updating Go microservices images or deployment files.

## Decisions

### Decision 1: Federated owner projects behind one operator command

The deployment will consist of three owner-defined Compose projects coordinated by a tdt-observability command or script:

```text
coordinator
  ├── agent-core project        postgres + app
  ├── tdt-scheduler project     scheduler + postgres-backup
  └── tdt-observability project otel-gateway + LGTM + health/log + optional backends
```

The coordinator is the `tdt-observability-stack` console command implemented under `tdt-observability/src/tdt_observability/deployment/`. Its public operations are `up`, `verify`, `diagnostics`, and `down`, each requiring an explicit profile and accepting a run identity. It owns preflight, run identity, network creation, profile selection, ordered project startup, readiness, diagnostics, and run-owned teardown. It does not embed duplicate agent-core or scheduler service definitions.

The OpenSpec apply session rooted in `openspec-store` remains coordination-only because the CLI action context is repo-local to the store. It creates and supervises separately authorized owner worktrees for source changes; each worker reads this change but writes exactly one owning repository. Accepted owner reports and commit identities are the only authority for the integration owner to mark tasks complete.

**Why:** Owner files already contain non-trivial build contexts, mounts, initializers, and health behavior. The current duplicate scheduler definition has already lost required mobile mounts, demonstrating that central duplication drifts.

**Alternatives considered:**

- **Monolithic Compose:** rejected because it transfers generic database ownership, duplicates services, changes volume identity, broadens build contexts, and cannot be one atomic PR across repositories.
- **Compose `include`:** rejected for this change because top-level names, networks, volumes, and project identities still conflict; it adds merge complexity without removing the cross-project migration problem.
- **Manual multi-command runbook:** rejected because it leaves ordering, identity, and evidence inconsistent. One coordinator command is retained as the operator contract.

### Decision 2: Two configurable cross-project networks

The coordinator creates two external, run-scoped networks:

- `TDT_RUNTIME_NETWORK`: agent-core PostgreSQL, agent-core app, scheduler, and backup traffic.
- `TDT_OBSERVABILITY_NETWORK`: OTel gateway, LGTM, agent-core app, scheduler, health-poller, log-collector, and selected backends.

Owner Compose files declare the external network with an explicit `name: ${TDT_RUNTIME_NETWORK:?}` or `name: ${TDT_OBSERVABILITY_NETWORK:?}` contract. Agent-core PostgreSQL has the stable runtime-network alias `postgres`; scheduler and `postgres-backup` join the runtime network, while only scheduler joins the observability network. Langfuse and MLflow each receive a private backend network; the gateway and backend web/server service bridge to the appropriate private network, while PostgreSQL, Redis, ClickHouse, and MinIO do not join the shared observability network.

Defaults may be human-readable for normal local use, but acceptance always supplies collision-resistant names. Compose files use service DNS names and do not set `container_name`. Published ports bind to `127.0.0.1` and accept run-specific host-port overrides.

**Why:** Separating runtime data traffic from observability traffic makes ownership and least privilege visible while still allowing independent projects to communicate.

**Alternative considered:** One shared network was simpler but unnecessarily exposes PostgreSQL and backend-internal services to every observability container.

### Decision 3: Agent-core retains the single runtime PostgreSQL server

Agent-core continues to own the runtime PostgreSQL image, PostgreSQL-18-versioned volume, host port, init scripts, and rollback. The target logical databases are:

| Database | Consumer |
|---|---|
| `agent_core` | agent-core runtime, DBOS, and memory |
| `tdt_scheduler` | scheduler application connection |
| `tdt_scheduler_dbos_sys` | scheduler DBOS system state |
| `agent_harness` | harness checkpoints |

Langfuse and MLflow retain separate PostgreSQL services and versioned volumes inside their optional profiles. They share the approved `postgres:18.6-trixie` image baseline but not runtime ownership or credentials.

**Why:** This preserves the binding specifications, existing data identity, and required initializers. Tdt-observability should own observability infrastructure, not the ecosystem's generic durable database.

**Transaction boundary:** No legacy or candidate PostgreSQL volume is deleted or rewritten during startup. A retained-data migration records a per-database source-to-target map, captures the source image/config/restart recipe, quiesces every writer, creates an immutable dump plus checksum, restores into a disposable staged target, verifies schema/count checks and consumer probes, then performs one documented DSN or network-alias cutover under the same maintenance window. The source remains preserved. Partial dump, restore, probe, or cutover failure leaves the target rejected and returns consumers to the proven prior recipe without restoring in place.

### Decision 4: One always-present gateway with profile-specific configs

All containerized producers use `http://otel-gateway:4317`. Tdt-observability retains four complete, independently validated Collector configs:

| Profile | Exporters |
|---|---|
| `base` | LGTM |
| `langfuse` | LGTM, Langfuse |
| `mlflow` | LGTM, MLflow |
| `full` | LGTM, Langfuse, MLflow |

The coordinator selects exactly one configuration. Producers never switch between backend-specific endpoints, and a configuration never contains exporters for intentionally absent services. Agent-core coordinated profiles set `OTEL_LANGFUSE_MODE=collector` and `OTEL_MLFLOW_MODE=collector`; implementation removes the current Collector-mode fallbacks to direct Langfuse and disabled MLflow, validates the selected gateway, and fails closed instead of silently enabling a direct SDK/autolog route.

Langfuse uses the OTLP HTTP base `http://langfuse-web:3000/api/public/otel`, so the exporter resolves `/api/public/otel/v1/traces`. A Collector Basic-auth client extension receives `LANGFUSE_PUBLIC_KEY` and `LANGFUSE_SECRET_KEY` through canonical `${env:...}` providers. The key pair must belong to an initialized local Langfuse project before the profile is ready.

MLflow uses `http://mlflow-server:5000` as the OTLP HTTP base with `${env:MLFLOW_EXPERIMENT_ID:-0}`. MLflow 3.15.1 meets the upstream SQL-backend requirement for OTLP ingestion.

OTLP export is retrying and therefore at-least-once. The contract guarantees one configured route, not protocol-level exactly-once delivery. Acceptance uses a unique trace identity, a bounded observation window, gateway counters, and backend queries to reject any observed duplicate while documenting that transport retries can theoretically duplicate delivery.

**Why:** A stable gateway makes the one-route contract enforceable and testable. Profile-specific configs avoid noisy retry queues for absent optional backends.

**Alternative considered:** Keeping LGTM's built-in collector as the producer endpoint cannot cleanly add optional fan-out without modifying bundled configuration. Optional standalone collectors repeat the current disconnected-route defect.

**Alternative considered:** Relying on Docker container health status is insufficient for the distroless Collector image, which has no `/bin/sh`, `wget`, or `curl`. A completed normative external readiness probe (`9f4c54e`) runs a disposable pinned probe container (`alpine:3.20`, OCI index digest `sha256:d9e853e87e55526f6b2917df91a2115c36dd7c696a35be12163d44e6e2a4b6bc` with `linux/amd64` and `linux/arm64` manifests) on the run-scoped observability network to query the Collector's own `health_check` extension on `http://otel-gateway:13133/` with bounded retries and explicit per-attempt timeouts. The probe command, endpoint, retry count, and redacted structured result are recorded under `gateway_readiness` in the acceptance manifest without relying on Docker container health status.

### Decision 5: MLflow-only uses a local artifact volume

The MLflow profile uses its own PostgreSQL-18 volume and a versioned named `mlflow-artifacts-3-data` volume mounted at `/mlartifacts`. The server runs with `--artifacts-destination /mlartifacts --serve-artifacts`. It does not select MinIO or set an S3 endpoint.

The Langfuse profile retains its own MinIO service and one-shot bucket initialization for Langfuse event storage. The full profile therefore includes MinIO for Langfuse, but MLflow remains independent and continues using its local artifact volume.

**Why:** This preserves the advertised independent MLflow profile and removes an undeclared dependency on the Langfuse overlay.

**Alternative considered:** A common object-storage overlay would support shared remote artifacts but adds lifecycle, credential, and initialization coupling that is not required for local readiness.

### Decision 6: Exact latest image inventory is frozen in the change

The selected inventory is:

| Component | Exact image/tag | Upstream status on 2026-08-22 |
|---|---|---|
| Python | `python:3.14.7-slim-trixie` | latest CPython 3.14 patch and pullable image |
| uv | `ghcr.io/astral-sh/uv:0.12.5` | latest release |
| PostgreSQL | `postgres:18.6-trixie` | latest PostgreSQL 18 patch |
| LGTM | `grafana/otel-lgtm:0.31.0` | latest release |
| OTel Collector Contrib | `otel/opentelemetry-collector-contrib:0.159.0` | latest release |
| Langfuse web | `langfuse/langfuse:4.16.0` | latest release |
| Langfuse worker | `langfuse/langfuse-worker:4.16.0` | coupled latest release |
| Redis | `redis:8.10.1-alpine` | latest Redis release; user-selected Redis 8 |
| ClickHouse | `clickhouse/clickhouse-server:26.7.5.10-alpine` | latest stable release |
| MinIO server | `minio/minio:RELEASE.2025-09-07T16-13-09Z` | newest pullable official multi-arch image; newer source release lacks matching image |
| MinIO Client | `minio/mc:RELEASE.2025-08-13T08-35-41Z` | latest release |
| MLflow | `ghcr.io/mlflow/mlflow:v3.15.1` | latest release |

Every manifest was confirmed to expose both required architectures. Implementation evidence will additionally retain immutable digests rather than writing digests into planning artifacts that may be superseded before implementation.

**Redis 8.10.1 candidate vs canonical root baseline:** The approved latest inventory in the integrated candidate worktree (`/Users/androidteam/Developer/tdt-observability/tdt-observability-integrated` at `56cc275`/`9f4c54e`) specifies `redis:8.10.1-alpine` (digest `sha256:becdda6c7f4b3fb42e42fd7f120bbf5c54c4caaaf16f26da24e4563d2c1f0576`). Any older canonical root state retaining `redis:8.10.0-alpine` (e.g. on branch `obs-compose-correction`) is preserved dirty/historical implementation state that cannot be promoted or accepted until reconciled to the approved `redis:8.10.1-alpine` target baseline.

**Compatibility deviations:** Langfuse 4.16.0 ships Redis 7 and ClickHouse 25.12 in its upstream Compose baseline. The user's latest-image decision selects Redis 8.10.1 and ClickHouse 26.7.5.10. Langfuse 4.16 includes ClickHouse 26 compatibility logic, but both deviations remain promotion gates requiring exact runtime evidence. The profile keeps `LANGFUSE_BULLMQ_SKIP_REDIS_VERSION_CHECK=false` for the first Redis 8 run so acceptance tests the real BullMQ gate. Setting it to `true` is allowed only as a separately recorded compatibility exception after queue behavior passes and the manifest explains why the version gate alone is being bypassed.

### Decision 7: Owner-local builds use explicit dependency contexts and one venv

- Agent-core keeps a repository-local primary context and declares tdt-core as an explicit additional context; its Dockerfile no longer copies `../tdt-core` outside the context.
- Scheduler retains its canonical workspace-root context because it intentionally packages many hosted workloads; its Dockerfile and dependency-integrity gate remain owner-controlled. A Dockerfile-specific context allowlist MUST constrain that root to the exact recorded build inputs. The executable remains the current `agent-core-scheduler serve`; the scheduler delta corrects the stale main-spec command rather than introducing a new rename.
- Tdt-observability uses a repository-local context plus a declared tdt-core context, copies its own `uv.lock`, synchronizes with `--frozen`, places the project venv on `PATH`, and runs both health-poller and log-collector from one image as a non-root user.
- Dockerfile-specific ignore rules constrain any workspace-root context to approved build inputs.

**Why:** This separates image ownership from integration orchestration and prevents render-only success from hiding invalid Docker build paths or mismatched Python environments.

`agent-docker-local-dev` remains a reduced-scope compatibility mirror. `agent-core-docker-local-development` is authoritative for the richer shared scenarios until a separate capability-consolidation change retires the duplicate.

### Decision 8: Canonical TDT home is mapped by subtree

Host and container roots are distinct inputs. The coordinator resolves a host root (`TDT_HOST_HOME`) using the canonical TDT default or an explicit disposable test root. Container services use an explicit `TDT_HOME` such as `/data` or `/home/agent/tdt`.

For health-poller and log-collector:

| Host subtree | Container target | Access |
|---|---|---|
| `state/observability` | `/data/state/observability` | read-write |
| `config/observability` or a selected config file | `/data/config/observability` | read-only except generated test config |
| `logs` | `/data/logs` | read-only |
| approved `deployments/*/logs` view | `/data/deployments` | read-only |

The complete TDT root and `credentials` subtree are not mounted into those services. Scheduler credentials and workload mounts remain in the scheduler-owned Compose definition.

**Why:** The current `~/.tdt/observability:/data` mapping doubles the kind/app path and the current `/var/log/tdt` target is invisible to code that resolves `/data/logs`.

### Decision 9: Mixed host/container health targets use address-class-aware config

Health-poller configuration uses:

- a supported host-gateway address (e.g. `http://host.docker.internal:8080` and `http://host.docker.internal:8090`) for launchd-owned services:
  - `webhook-receiver`: `com.tdt.webhook-receiver` running from `$HOME/.tdt/deployments/webhook-receiver` on `127.0.0.1:8080`, returning HTTP 200 `/health`;
  - `ai-review`: `com.tdt.ai-review` running from `$HOME/Developer/tdt/deployments/ai-review` on `127.0.0.1:8090`, returning `status=degraded` on `/health/full` when optional OmniRoute/Kimi providers are absent;
- `scheduler:9100` on the observability network for the Docker scheduler.

Poller health means the intended configuration loaded and a cycle completed within a bounded freshness window. Target outages remain observed data and do not masquerade as poller process death.

Log-collector health means its last scan/flush heartbeat is current. Acceptance appends a run-owned host log record and proves one persisted event plus restart-safe offsets.

### Decision 10: Resource limits are profile budgets, not incidental hints

Every long-lived service and initializer receives reviewed CPU and memory limits and reservations. Before final budgets are accepted, implementation measures startup and steady-state CPU/memory for each profile, records p95/p99 values, sets reservations at no less than observed p95 plus 20%, and sets limits at no less than observed p99 plus 20% unless an owner documents a stricter safe ceiling. The coordinator computes the selected profile's aggregate reservation plus 20% host headroom and fails before startup when Docker resources are insufficient. Until this measurement artifact exists, runtime profile acceptance remains blocked rather than guessing arbitrary budgets.

Authoritative Docker settings confirm `UseResourceSaver=false`, `AutoPauseTimeoutSeconds=300`, and `AutoPauseTimedActivitySeconds=30`. However, because the Docker daemon socket remains absent after repeated ~4–5 minute runtime session flaps, runtime acceptance gates (tasks 8–10) remain strictly blocked until a persistent Docker session is available.

**Why:** Langfuse, ClickHouse, LGTM, and latest-image migration tests are memory intensive. Unchecked host exhaustion produces false compatibility failures and non-actionable restarts.

### Decision 11: Multi-repository migration is additive

Implementation uses separate worktrees and commits per repository. The compatibility sequence is:

1. Add validation, configurable networks, image-build fixes, and the new gateway in parallel target files without removing the old path.
2. Start the gateway and prove base LGTM export.
3. Attach agent-core and scheduler to both selected networks.
4. Switch one producer repository at a time to `otel-gateway`, retaining endpoint override rollback.
5. Prove optional profiles and latest-image deviations.
6. Classify and migrate any duplicate PostgreSQL data.
7. Promote the target files and remove duplicate tdt-observability runtime services and stale documentation only after exact-SHA acceptance and any authorized data handoff.
8. Leave old data resources preserved until separately authorized retirement.

**Transaction boundaries & redeploy-after-commit provenance:** A producer endpoint switch is complete only when the producer restart, gateway receipt, direct-route disablement, and old-route rollback liveness are evidenced. A data cutover is complete only when writer quiescence, dump checksum, staged restore, consumer probes, cutover, and rollback rehearsal states are retained and the source remains intact. For host-deployed services (e.g. `webhook-receiver` whose deployment report recorded pre-commit identity `baa49981` while source commit is `f3f904ded6d14108227cb198967e3b85963be685`) and container images, exact-commit provenance requires that services be redeployed after the source commit is finalized so that deployment reports and acceptance manifests reflect exact post-commit provenance. No cleanup is part of either transaction.

### Decision 12: One machine-readable readiness manifest gates archive

The coordinator validates and writes `artifacts/tdt-compose/<run-id>/manifest.json` against `tdt-observability/deploy/evidence/tdt-compose-acceptance-v1.schema.json`. The manifest contains writable repository identities, every read-only scheduler build/mount input path and identity, initial dirt, exact Compose inputs, profile, networks, ports, state root, image tags/digests/platforms, first-party build provenance, post-commit redeploy provenance, resource measurements/budgets, builds, Collector validation, external gateway readiness probe results, database migration phases, health/log/trace/artifact operations, duplicate-detection results, failure isolation, diagnostics, and cleanup.

Focused checks remain useful but cannot replace the profile integration run. The report presents structural, build, runtime, data, and cleanup results independently and derives `success`, `partial`, or `blocked` without promoting a structural-only pass.

## Risks / Trade-offs

- **[Risk] One coordinator command fronts several Compose projects, so cross-project `depends_on` is unavailable.** → Owner entrypoints use bounded readiness probes, and the coordinator waits on owner health before starting dependents.
- **[Risk] Redis 8 is newer than Langfuse's shipped Redis baseline.** → Run queue production/consumption, retries, scheduled work, ingestion, and no-error/restart acceptance under exact versions; block without it.
- **[Risk] ClickHouse 26.7 is newer than Langfuse's shipped ClickHouse baseline.** → Validate migrations, ingestion, analytics, detected-version compatibility settings, logs, and restarts; block on any analyzer or schema error.
- **[Risk] Latest tags can move again before implementation.** → This change freezes exact tags resolved on 2026-08-22; any later bump requires an explicit planning revision and recaptured manifests.
- **[Risk] MinIO's newest source release is not an available official image.** → Pin the newest pullable official multi-architecture image and retain the source/image exception in evidence.
- **[Risk] Existing tdt-observability and agent-core PostgreSQL volumes may contain divergent state.** → Inspect with Docker available, classify each exact volume, dump/restore when required, preserve sources, and keep cleanup outside cutover.
- **[Risk] Host-gateway naming differs by platform.** → Preflight the supported macOS Docker Desktop mapping and include an explicit host-gateway entry for compatible Linux engines; fail with a platform diagnostic otherwise.
- **[Risk] Removing fixed container names may break scripts that address container names.** → Migrate supported automation to Compose service selection and network DNS; search for ambient-name consumers before removal.
- **[Risk] Collector route selection currently falls back to direct or disabled backend modes.** → Implement and test real Collector modes, require explicit profile environment, and fail closed when the gateway is invalid.
- **[Risk] Full profile resource demand may exceed local Docker allocation.** → Enforce aggregate preflight and document base or single-backend profiles as lower-cost alternatives.
- **[Trade-off] MLflow local artifacts are not shared with MinIO.** → Independence and reliable local acceptance are prioritized; a remote-artifact profile can be proposed separately.

## Migration Plan

### Phase 0: Freeze and preflight

1. Create separate implementation worktrees for agent-core, tdt-scheduler, tdt-observability, and openspec-store ownership as applicable.
2. Record HEADs, branches, dirty paths, Docker/Compose versions, available resources, container/network/volume/image inventories, active schedules, and launchd state without printing credential values.
3. Classify current tdt-observability Dockerfile/Compose edits as preserve, supersede, or integrate; do not overwrite them implicitly.
4. Resolve exact image digests and rerun architecture checks immediately before implementation.

### Phase 1: Additive owner-local foundations

1. Add failing render/build/path tests before source changes.
2. Repair agent-core and tdt-observability build contexts and locked venvs.
3. Add versioned PostgreSQL volumes, shared-network variables, port variables, and no-fixed-name checks.
4. Add the coordinator, profile model validation, resource measurement/preflight, and versioned evidence-manifest schema in parallel target files without removing old services.

### Phase 2: Gateway and base profile

1. Add the four Collector configs and validate each with Collector `0.159.0`.
2. Start run-scoped networks, agent-core PostgreSQL/app, scheduler, gateway, and LGTM.
3. Verify databases, owner health, and LGTM trace/metric/log flow.
4. Retain endpoint overrides so each producer can roll back independently.

### Phase 3: Optional profiles and latest-image evidence

1. Bring up Langfuse `4.16.0` with PostgreSQL 18.6, Redis 8.10.1, ClickHouse 26.7.5.10, MinIO, and initialized OTLP credentials.
2. Retain migration, queue, ingestion, analytics, logs, versions, and restart evidence.
3. Bring up MLflow 3.15.1 with PostgreSQL and its local artifact volume; verify OTLP and artifact round trips without MinIO.
4. Exercise full-profile one-route delivery, bounded duplicate detection, and backend failure isolation.

### Phase 4: Canonical host integration

1. Replace old observability subtree mounts with canonical least-privilege mappings.
2. Verify mixed host/container polling, real host-log ingestion, state persistence, and restart-safe offsets.
3. Update owner runbooks and remove stale agent-core observability service inventories.

### Phase 5: Cutover and cleanup handoff

1. Switch producers one repository at a time to `otel-gateway`, prove direct backend routes are disabled, verify old-route rollback liveness, and retain exact commit/result pairs.
2. Inspect duplicate PostgreSQL data and stop at an explicit operator authorization gate before any retained-data migration or fresh-start decision.
3. For an authorized retained-data migration, quiesce writers, checksum the dump, restore to a staged target, verify it, perform the bounded cutover, and rehearse rollback while preserving the source.
4. Remove duplicate service definitions and deprecated endpoint/network defaults only after the candidate manifest and data handoff pass.
5. Produce a separate, exact allowlist of legacy resources eligible for later retirement; do not delete them during normal apply or verification.
6. Validate the OpenSpec change and store, review the multi-repository commit matrix, and archive only after the full acceptance manifest reports success.

### Rollback

- Revert or redeploy only the affected owner repository commit; do not require all repositories to roll back together.
- Restore the prior producer endpoint through its compatibility override and verify receipt before stopping the new route.
- Reattach the preserved prior PostgreSQL image/volume if database acceptance fails.
- Keep the new gateway and optional backends stopped but diagnostically available until rollback verification completes.
- Treat rollback as blocked if the required prior data or exact image identity was retired without a verified backup.

## Open Questions

None. Exact resource numbers are implementation measurements constrained by the resource-budget requirements; they do not change the selected architecture, profile surface, or task sequence.

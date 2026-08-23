## Why

The archived observability consolidation cannot produce a clean, reproducible TDT Docker deployment because it duplicates repository-owned services, disconnects optional telemetry exporters, drops PostgreSQL bootstrap contracts, and maps host runtime state inconsistently.

This correction is needed now because the archived tasks claim completion while the current committed topology is not buildable from a clean checkout, the implementation worktree contains uncommitted repairs, and the approved image baseline has advanced since the archive.

## What Changes

- Replace the attempted monolithic cross-repository Compose project with a federated deployment: `agent-core`, `tdt-scheduler`, and `tdt-observability` retain their own image and service definitions, while one tdt-observability-owned operator command coordinates build, startup, verification, diagnostics, and teardown.
- Keep the shared runtime PostgreSQL server and its logical-database initializers owned by `agent-core`; connect scheduler and observability components through configurable, run-scoped `tdt-runtime` and `tdt-observability` networks.
- Introduce one stable application-facing `otel-gateway:4317` endpoint with separately validated base, Langfuse, MLflow, and full exporter profiles, each enforcing one authoritative ingestion route per backend.
- Remove the impossible Docker healthcheck from the distroless `otel-gateway` service and add a normative external readiness probe that runs a disposable pinned container on the run-scoped observability network to query the Collector `health_check` extension at `http://otel-gateway:13133/` with bounded retries; runtime readiness is NOT established by removing the broken healthcheck alone.
- Make agent-core Collector route modes real and fail-closed: coordinated profiles select Collector mode for Langfuse and MLflow, disable their direct SDK/autolog routes, and MUST NOT fall back from Collector mode to a direct backend route.
- Correct Langfuse OTLP endpoint and Basic-auth handling, and make MLflow independently runnable with persistent local artifact storage rather than an implicit dependency on Langfuse's MinIO service.
- Preserve the canonical `$TDT_HOME/<kind>/<app>/<name>` layout through least-privilege host bind mounts for observability state, configuration, logs, and deployment logs; distinguish host-source paths from container paths.
- Monitor host-native launchd services (`webhook-receiver` on `127.0.0.1:8080` from canonical root `$HOME/.tdt/deployments/webhook-receiver` and `ai-review` on `127.0.0.1:8090` from `$HOME/Developer/tdt/deployments/ai-review`) via supported host gateway mappings; enforce redeploy-after-commit provenance so deployed host services and acceptance manifests reflect post-commit source revisions.
- Repair owner-local Python image construction so builds use locked uv environments, non-root users, pinned build tooling, and declared sibling-repository build contexts.
- Remove fixed container names, make project/network/port identities overridable for concurrent verification, and prohibit automatic deletion of ambient networks, images, volumes, or runtime data.
- Upgrade every image in this change to the exact latest release verified on 2026-08-22 with both `linux/amd64` and `linux/arm64` manifests: Python `3.14.7-slim-trixie`, uv `0.12.5`, PostgreSQL `18.6-trixie`, Grafana LGTM `0.31.0`, OTel Collector Contrib `0.159.0`, Langfuse server/worker `4.16.0`, Redis `8.10.1-alpine`, ClickHouse `26.7.5.10-alpine`, MinIO server `RELEASE.2025-09-07T16-13-09Z`, MinIO Client `RELEASE.2025-08-13T08-35-41Z`, and MLflow `v3.15.1`. Treat older canonical root checkouts retaining Redis `8.10.0-alpine` as preserved dirty/historical implementation state that cannot be promoted or accepted until reconciled to the approved Redis `8.10.1-alpine` target.
- Treat Redis 8 and ClickHouse 26.7 as explicit Langfuse upstream-baseline deviations that require fresh web/worker, migration, queue, and no-error runtime evidence before promotion.
- Acknowledge Docker daemon runtime history: a GUI crash loop (unhandled RxJS `AbortError` on SSE streams in `createWindowManager.main.js`) was resolved via factory reset on 2026-08-23, which wiped the 35GB VM (all images/containers) and all tuned settings. The authoritative settings were restored the same day to `UseResourceSaver=false`, `AutoPauseTimeoutSeconds=0`, `MemoryMiB=6144`, `Cpus=8`, and `UseContainerdSnapshotter=false` (classic `overlay2`). Docker Desktop is now running and stable (context `desktop-linux`, Server 29.7.2). All runtime acceptance gates (§8–§10) are now unblocked; images must be re-pulled/re-built from clean worktrees, and preflight must re-verify these settings before any runtime gate.
- Replace the impossible "one atomic PR" migration with an additive, multi-repository compatibility sequence bound to exact writable-repository commits, every read-only scheduler build/mount input identity, and a retained machine-readable acceptance manifest.
- **BREAKING**: producers use `otel-gateway:4317` instead of `otel-lgtm:4317` or the removed `otel-collector:4317` endpoint after the compatibility window closes.
- **BREAKING**: legacy unversioned PostgreSQL volumes and the duplicate tdt-observability runtime PostgreSQL service are not selected by the target model; existing data must be classified and explicitly migrated or preserved before removal.

### Non-Goals

- Changing agent runtime tracing semantics, span schemas, evaluation behavior, or privacy defaults.
- Moving launchd-owned `webhook-receiver` or `ai-review` into Docker.
- Changing the Go microservices Compose, Kubernetes, Argo CD, or cloud-delivery topology.
- Turning this local workstation deployment into a production orchestration platform.
- Deleting old Docker resources, unloading host services, or migrating data without separate operator authorization and retained preflight evidence.
- Implementing application source features unrelated to image construction, deployment readiness, or observability routing.

## Capabilities

### New Capabilities

- `tdt-observability-docker-deployment`: Defines federated ownership, supported Compose profiles, exact image pins, stable telemetry routing, networks, persistence, secrets, local ports, and lifecycle behavior for the TDT observability deployment.
- `tdt-compose-operational-readiness`: Defines run-scoped, evidence-backed acceptance for owner-local builds, PostgreSQL bootstrap, telemetry fan-out, health polling, log ingestion, MLflow artifacts, failure isolation, and ownership-safe cleanup.

### Modified Capabilities

- `scheduler-docker-deployment`: Reconciles repository-owned scheduler construction, shared runtime and observability networks, bounded cross-project database readiness, and removal of duplicated integration definitions.
- `agent-core-docker-local-development`: Updates the Python image pin, preserves agent-core PostgreSQL/bootstrap ownership, and exposes the owner-managed app and database on configurable shared networks.
- `agent-docker-local-dev`: Keeps the duplicate agent-core local-Docker contract coherent with the new Python pin, versioned PostgreSQL volume, and federated network model pending later capability consolidation.
- `tdt-env-loader-tdt-home`: Requires Docker bind sources and container targets to preserve the canonical TDT home layout when the host root is explicit, absent, or isolated for verification.
- `infrastructure-postgresql`: Applies the PostgreSQL 18.6 trixie and versioned-volume baseline across the coordinated federated deployment rather than assuming one Compose project.
- `postgresql-18-migration`: Replaces unconditional old-volume deletion with explicit disposable-data classification, preservation, migration, and operator-authorized retirement.

## Impact

- **`tdt-observability`** owns the orchestration command, LGTM/gateway deployment, health-poller and log-collector image, Langfuse/MLflow overlays, exact image registry, canonical mounts, and operator documentation.
- **`agent-core`** owns its app image, shared runtime PostgreSQL service, versioned volume, logical-database initializers, shared-network attachment, and current Docker runbook.
- **`tdt-scheduler`** owns its image, scheduler and backup services, workload source mounts, database readiness, shared-network attachment, and scheduler verification override.
- **`tdt-core`** remains the provider of TDT path/environment semantics; source changes are expected only if verification proves a missing public adapter.
- **`agent-harness`** is a PostgreSQL-bootstrap consumer and must verify its `agent_harness` checkpoint database remains available; it does not become a Compose owner.
- **`openspec-store`** owns the capability deltas, multi-repository ownership matrix, validation, acceptance evidence contract, and archive decision.
- **Read-only scheduler inputs** (`tdt-core`, `jira-daily-reports`, `jira-skill`, `webhook-receiver`, `ai-review`, `code-daily-scan`, `tdt-sheets`, `jira-epic-report`, and the configured Android/iOS repositories) contribute source or mounts but receive no write ownership; their exact paths, revisions, and dirt classifications are acceptance inputs.
- The OpenSpec store's repo-local apply context remains the planning/integration boundary. Source edits are dispatched to separately authorized owner worktrees, and only the integration owner updates OpenSpec task state from accepted owner evidence.
- The implementation spans independent Git repositories and therefore produces an ordered commit matrix rather than one cross-repository atomic commit or PR.

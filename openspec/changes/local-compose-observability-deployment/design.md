## Context

This design provides the operational architecture, runbook specifications, and validation procedures for local Docker Compose deployments of `tdt-scheduler` and `agent-core` observability services. See `proposal.md` for background and problem motivation.

Operational audits (`/tmp/local-compose-observability-openspec-audit.md` and `/tmp/tdt-scheduler-compose-grok-audit.md`) and direct empirical evidence established the following operational baseline:
- **Verified Isolated Runtime**: `tdt-scheduler-verification` successfully executed on `127.0.0.1:19100:9100` using project `-p tdt-scheduler-verification` and disposable `TDT_HOME=/tmp/tdt-scheduler-verification-home`.
- **Health Verification**: `/scheduler/health` returned healthy JSON status (`enabled: true`, `dbos_connected: true`, `schedule_count: 20`, `schedules_applied: 19`, 3 manifests loaded) with startup reload duration ~87ms.
- **Healthcheck Precedence**: The `compose.yaml` HTTP curl healthcheck against `/scheduler/health` effectively overrides the Dockerfile Python import check.
- **Warning Classification**: Identifies expected log events (Tailscale webhook self-test timeout, sprint switch unconfigured spreadsheet ID, unconfigured telemetry sinks) resulting from container network isolation and test environments.

## Goals / Non-Goals

**Goals:**
- Provide clear, reproducible Docker Compose runbooks for `tdt-scheduler` and `agent-core` verification.
- Establish strict isolation standards: dedicated Compose project names, unique non-default loopback port bindings (`127.0.0.1:19100`), and disposable host directories (`/tmp/...`).
- Document non-disturbing, bounded monitoring procedures (`curl /scheduler/health`, `docker inspect`, `docker logs --tail`).
- Define the warning triage matrix to prevent false alarms on benign local development logs.
- Formalize a decision gate protocol for defect remediation: runtime bugs must be reproduced in isolation and fixed under separate OpenSpec changes.
- Provide safe teardown and cleanup command templates.

**Non-Goals:**
- Modifying production runtime logic or default container network topologies.
- Creating delta specification files (`skip_specs: true`).
- Fixing discovered application source bugs directly within this documentation/verification change.

## Decisions

### Decision 1: Project and Port Isolation via Compose Overrides
- **Choice**: Use dedicated Compose project name (`-p tdt-scheduler-verification`), dedicated loopback port mapping (`127.0.0.1:19100:9100`), and temporary storage root (`TDT_HOME=/tmp/tdt-scheduler-verification-home`).
- **Rationale**: Ensures zero collision with running developer daemons or default port 9100 services; guarantees all disk writes stay in ephemeral directories.
- **Alternatives Considered**:
  - Running directly on port 9100: Rejected due to immediate conflict with ambient long-running scheduler containers.
  - Host networking mode (`network_mode: host`): Rejected because it bypasses container network isolation and introduces port collisions.

### Decision 2: Documentation and Operational Runbook Scope (`skip_specs: true`)
- **Choice**: Track this change with `skip_specs: true` and produce runbook documentation and verification tasks.
- **Rationale**: The change establishes operational procedures and documentation; it introduces no new product capabilities or normative contract deltas.
- **Alternatives Considered**: Modifying main capability specs: Rejected because runtime interfaces and system behaviors remain unchanged.

### Decision 3: Warning Classification Taxonomy
- **Choice**: Standardize the categorization of known startup and background warnings:
  - `Tailscale / Webhook Self-Test`: Classified as **Network Isolation Artifact** (benign background timeout; container lacks Tailscale interface).
  - `Sprint Switch / No Spreadsheet ID`: Classified as **Configurable Integration Notice** (benign warning when Google Sheets integration is unconfigured).
  - `Langfuse / MLflow Absence`: Classified as **Optional Telemetry Sink Notice** (benign notices when local tracking endpoints are unconfigured).
- **Rationale**: Prevents engineers and automated agents from mistaking expected test-sandbox warnings for service health failures.
- **Alternatives Considered**: Suppressing container log output: Rejected because log suppression masks legitimate runtime errors.

### Decision 4: Mandatory Decision Gate for Source Defect Remediation
- **Choice**: Enforce a strict decision gate: any source-level defect discovered during operational verification (e.g., startup reloader sequence or handler defects) must be recorded as an isolated finding and addressed in a dedicated implementation change.
- **Rationale**: Preserves change boundaries, prevents scope creep, and adheres to GitNexus blast-radius and impact-analysis requirements.
- **Alternatives Considered**: Immediate in-tree bug patching: Rejected because it bypasses isolated worktree verification and strict spec governance.

## Risks / Trade-offs

- **[Risk] Accidental modification or termination of ambient developer containers** → **Mitigation**: All runbook CLI commands mandate explicit `-p <project>` and container name qualifiers.
- **[Risk] Confusion over "unhealthy" status in stopped container inspection** → **Mitigation**: Runbook explicitly documents that Docker inspect reports post-exit snapshots, and instructs verification against active runtime HTTP endpoints.
- **[Risk] Ephemeral test data lingering on host filesystem** → **Mitigation**: Provide automated cleanup commands targeting `/tmp/tdt-scheduler-verification*` and Docker volume pruning.

## Migration & Operational Runbook Structure

### 1. Unique-Project Deployment Execution
```bash
# 1. Prepare disposable environment and schedules directory
mkdir -p /tmp/tdt-scheduler-verification-home/schedules /tmp/tdt-scheduler-verification-home/credentials

# 2. Start container in dedicated verification project
docker compose -p tdt-scheduler-verification -f compose.yaml -f /tmp/tdt-scheduler-verification.override.yaml up -d scheduler

# 3. Verify runtime health via bounded HTTP check
curl -fsS http://127.0.0.1:19100/scheduler/health | python3 -m json.tool
```

### 2. Bounded Non-Disturbing Monitoring
```bash
# Check container state and health streak
docker inspect tdt-scheduler-verification --format 'Status={{.State.Status}} Health={{.State.Health.Status}} FailingStreak={{.State.Health.FailingStreak}}'

# Inspect bounded recent logs (no streaming/hanging)
docker logs tdt-scheduler-verification --tail 30
```

### 3. Clean Teardown
```bash
# Stop and dismantle verification project without touching other containers
docker compose -p tdt-scheduler-verification -f compose.yaml -f /tmp/tdt-scheduler-verification.override.yaml down -v

# Clean disposable temporary home
rm -rf /tmp/tdt-scheduler-verification-home
```

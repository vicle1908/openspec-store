## Why

Local Docker Compose deployment and verification for `tdt-scheduler` and `agent-core` observability services require standardized operational procedures, isolated project execution patterns, and clear warning classifications to ensure reliable testing without disrupting running workloads. This change establishes the runbook updates, verification workflows, and diagnostic taxonomies needed for safe, non-colliding Compose operations across local developer environments.

## What Changes

- Document standardized Docker Compose verification procedures for `tdt-scheduler` and `agent-core` observability stacks.
- Define isolated execution patterns leveraging unique Compose project names (e.g., `-p tdt-scheduler-verification`), dedicated loopback port mappings (e.g., `127.0.0.1:19100:9100`), and disposable configuration directories (`TDT_HOME=/tmp/...`).
- Document bounded, non-disturbing health check and monitoring commands (`curl http://127.0.0.1:19100/scheduler/health`, formatted `docker inspect`, and bounded log inspection).
- Establish formal classification and triage guide for expected local-environment warnings:
  - `Tailscale / Webhook Self-Test Timeout`: Network isolation artifact (bridge network lacks host Tailscale interface); expected one-shot background event that does not impair scheduler execution.
  - `Sprint Switch / No Spreadsheet ID`: Configurable integration warning when Google Sheets ID is not configured; expected in local test environments.
  - `Langfuse / MLflow Credential Warnings`: Optional OTel / tracking sink notices when credentials are unset in local test sandboxes.
- Document explicit cleanup and teardown procedures to safely dismantle verification containers without affecting ambient developer services.
- Establish an explicit decision gate: any source-code defect identified during Compose verification must be documented, reproduced in isolation, and remediated under a separate implementation change.

### Non-Goals

- Modifying core application source code or runtime logic in `tdt-core`, `agent-core`, or `tdt-scheduler` within this change.
- Creating or synchronizing normative OpenSpec capability specifications (`skip_specs: true`).
- Changing default production port assignments or modifying live production compose networks.
- Storing unencrypted production credentials or API tokens in versioned runbooks.

## Capabilities

### New Capabilities
None. This change focuses on operational verification, runbooks, and documentation without introducing new system capabilities.

### Modified Capabilities
None. System behavior and normative specifications remain unchanged (`skip_specs: true`).

## Impact

- **Affected Systems**: `tdt-scheduler` deployment configs and runbooks, `agent-core` local compose documentation, developer verification environments.
- **Ownership Boundaries**:
  - `openspec-store`: Planning governance and verification task tracking.
  - `tdt-scheduler`: Compose definitions (`compose.yaml`, override templates) and local operations runbooks.
  - `agent-core`: Observability integration runbooks and multi-service Docker networking guides.
- **Operational Risk**: Zero. Verification is conducted in isolated projects with non-overlapping port bindings and disposable storage volumes.

## Why

Local Compose verification crosses three repositories, so an operational plan must make the deployment owner, integration owner, and library dependency explicit. The verified isolated scheduler stack shows that a unique project, loopback mapping, and disposable state can exercise the runtime without disturbing ambient services, while a separate reproduction found that the `webhook-selftest` workflow is unregistered; neither result authorizes source changes in this documentation-only change.

## What Changes

- Define the `tdt-scheduler` deployment/runbook scope: its scheduler Dockerfile and entrypoint, container port `9100`, `/scheduler/health`, Compose runtime, isolated-stack verification procedure, and scheduler runbook.
- Define the `agent-core` integration scope: its observability Compose integration runbook and environment guidance for PostgreSQL, the OTel Collector, Langfuse, and MLflow.
- Record `tdt-observability` as the owner of its library and dashboard source and as an integration dependency; it is not the deployment Compose owner for this change.
- Record `openspec-store` as the owner of planning, validation, and later archive governance only.
- Retain the unique-stack evidence: project `tdt-scheduler-verification`, loopback `127.0.0.1:19100:9100`, disposable `TDT_HOME=/tmp/tdt-scheduler-verification-home`, and a healthy `/scheduler/health` response.
- Distinguish expected configuration/network-isolation notices from the reproduced `webhook-selftest` registration defect. The latter must be carried by a separate implementation OpenSpec change after its minimal reproduction is attached; this change only records and defers it.
- Limit each documentation writer to documentation in its own repository: `tdt-scheduler` for the scheduler runbook and `agent-core` for the observability integration runbook. No documentation writer edits `tdt-observability` or `openspec-store` implementation content.

### Non-Goals

- Modifying application, library, dashboard, scheduler, Dockerfile, entrypoint, Compose, or runtime source in `tdt-scheduler`, `agent-core`, `tdt-observability`, or any other repository.
- Fixing the unregistered `webhook-selftest` workflow within this change; that requires a distinct implementation OpenSpec change.
- Creating or synchronizing normative OpenSpec capability specifications (`skip_specs: true` remains in effect).
- Changing default production ports, live production networks, or storing production credentials in runbooks.

## Capabilities

### New Capabilities

None. This change clarifies ownership and operational documentation; it does not change normative system behavior.

### Modified Capabilities

None. Specifications remain skipped (`skip_specs: true`), because any source repair is deliberately deferred to a separately scoped implementation change.

## Impact

- **Affected systems:** `tdt-scheduler` local deployment/runbook, `agent-core` observability integration documentation/environment, and isolated developer verification environments.
- **Ownership boundaries:**
  - `tdt-scheduler` owns the scheduler Dockerfile, entrypoint, port `9100`, `/scheduler/health`, Compose runtime, and scheduler runbook.
  - `agent-core` owns the observability Compose integration runbook/environment, including PostgreSQL, OTel Collector, Langfuse, and MLflow integration guidance.
  - `tdt-observability` owns library/dashboard source and remains an integration dependency, not the current deployment Compose owner.
  - `openspec-store` owns this plan, its validation, and archive governance.
- **Operational risk:** Verification stays bounded and isolated by an explicit Compose project, loopback port, and disposable state. The separate source-defect change must establish its own impact analysis and acceptance evidence.

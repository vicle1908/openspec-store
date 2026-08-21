## Context

This is a documentation and operational-planning change for a multi-repository local Compose deployment. It does not grant this store or either documentation writer authority to edit runtime source. The change keeps `skip_specs: true`; its existing proposal, design, and task artifacts are the complete planning surface.

The audited isolated runtime provides reusable evidence, not an instruction to reuse a stack name blindly:

- Project `tdt-scheduler-verification` ran with `-p tdt-scheduler-verification`, loopback mapping `127.0.0.1:19100:9100`, and disposable `TDT_HOME=/tmp/tdt-scheduler-verification-home`.
- `/scheduler/health` returned healthy JSON, including `enabled: true`, `dbos_connected: true`, `schedule_count: 20`, `schedules_applied: 19`, and three loaded manifests; the observed startup reload was about 87 ms.
- The Compose HTTP healthcheck for `/scheduler/health` took precedence over the Dockerfile Python import check.
- A minimal scheduler inspection reproduced that `webhook-selftest` is absent from the registered workflow/run list. This is a source-level defect, not a completed deployment finding or an allowed patch in this change.

## Goals / Non-Goals

**Goals:**

- Make the repository and documentation-writer boundary mechanically reviewable.
- Preserve the unique-stack proof pattern: a collision-resistant project identity, its exact resource inventory, loopback port, disposable state root, bounded checks, and owned-only teardown.
- Provide `tdt-scheduler` with a runbook scope for its scheduler runtime and provide `agent-core` with a distinct observability-integration runbook scope.
- Record a reproducible handoff for the unregistered `webhook-selftest` workflow without obscuring it among benign warning classes.

**Non-Goals:**

- Reassigning `tdt-observability` from its library/dashboard ownership or making it a Compose deployment owner.
- Editing Docker, Compose, application, scheduler, library, dashboard, or documentation files in this planning change.
- Treating structural OpenSpec validation as proof that an isolated Compose runtime or a source-defect fix works.

## Decisions

### Decision 1: Explicit runtime and documentation ownership

- **Choice:** `tdt-scheduler` owns the scheduler Dockerfile, entrypoint, port `9100`, `/scheduler/health`, Compose runtime, and scheduler runbook. Its documentation writer may change only `tdt-scheduler` documentation.
- **Choice:** `agent-core` owns the observability Compose integration runbook/environment, including guidance for PostgreSQL, OTel Collector, Langfuse, and MLflow. Its documentation writer may change only `agent-core` documentation.
- **Choice:** `tdt-observability` owns library/dashboard source and is an integration dependency; it is not the owner of the current deployment Compose work.
- **Choice:** `openspec-store` owns planning, validation, and archive governance; it does not own implementation or cross-repository documentation writes.
- **Rationale:** A separate owner for each mutable surface prevents one deployment result from silently becoming authority to change another repository.
- **Alternative rejected:** A shared “observability stack” owner. This is ambiguous about Docker runtime, service environment, and library/dashboard source ownership.

### Decision 2: Unique-stack verification is an owned-resource protocol

- **Choice:** A verification run creates a collision-resistant Compose project name, records the initial resource inventory and source/image identities, binds only a non-default loopback port (the reproduced example is `127.0.0.1:19100:9100`), and uses a run-scoped temporary `TDT_HOME`. It uses bounded health, inspect, and log commands, then removes only resources bearing that run identity.
- **Rationale:** The existing `tdt-scheduler-verification` result proves the pattern is viable; a future run must prove it owns its resources rather than relying on an ambient container, volume, or network.
- **Alternatives rejected:** Port `9100` directly and host networking, because both create ambient collision and attribution risk.

### Decision 3: Warning taxonomy must not hide the reproduced defect

- **Choice:** Keep Tailscale/bridge-network reachability timeouts, absent spreadsheet configuration, and unset optional Langfuse/MLflow credentials as separately documented diagnostic classes when their expected preconditions hold.
- **Choice:** Treat the reproduced absence of `webhook-selftest` from the registered scheduler workflow/run list as a source defect. Capture the minimal reproduction, expected registration, actual registration result, source identity, and diagnostics for a new implementation OpenSpec change.
- **Rationale:** A network timeout and an unregistered workflow have different causes and remediations. Calling both “expected local warnings” would wrongly mask a scheduling defect.
- **Alternative rejected:** Repairing registration, the Dockerfile, entrypoint, or scheduler source in this change. It exceeds the documentation/planning scope and lacks a separately approved implementation change.

### Decision 4: Validation remains structural and repository-scoped

- **Choice:** `openspec-store` runs `openspec doctor --store openspec-store` and strict validation for this change, stages only these three existing planning artifacts, and archives only after separate implementation/acceptance evidence is complete. The `.openspec.yaml` setting remains untouched with `skip_specs: true`.
- **Rationale:** Doctor and strict validation prove store/change structure and coherence, not source repair, Compose reachability, or other repositories’ worktree state.
- **Alternative rejected:** Treating checked planning tasks or a successful validator as end-to-end operational acceptance.

## Risks / Trade-offs

- **Ambient-resource collision or accidental teardown** — Require a unique project identity, before/after resource inventory, loopback-only port, and cleanup filtered to that identity.
- **Cross-repository writer overreach** — Keep scheduler documentation in `tdt-scheduler` and observability integration documentation in `agent-core`; do not dispatch either writer into another repository.
- **Masked defect** — The unregistered `webhook-selftest` result is a blocker for a claim that the self-test workflow is deployed; it must be carried into a separate source implementation change.
- **False completion from planning validation** — Report strict validation and doctor separately from the later isolated runtime acceptance and source-defect repair.

## Operational Runbook Structure

### 1. Scheduler-owned isolated deployment

The `tdt-scheduler` runbook shall describe its Dockerfile/entrypoint/Compose runtime and its public local contract: container port `9100` and `GET /scheduler/health`. A verification invocation shall use a new run identity rather than copying an existing one verbatim. The previously verified shape was:

```bash
TDT_HOME=/tmp/tdt-scheduler-verification-home \
  docker compose -p tdt-scheduler-verification -f compose.yaml \
  -f /tmp/tdt-scheduler-verification.override.yaml up -d scheduler
curl -fsS http://127.0.0.1:19100/scheduler/health | python3 -m json.tool
```

The runbook shall use bounded inspection such as `docker logs --tail 30`, record the named project/container identities, and perform a project-filtered teardown only after diagnostics have been captured.

### 2. Agent-core-owned observability integration

The `agent-core` runbook shall document how its local Compose integration environment connects to PostgreSQL, the OTel Collector, Langfuse, and MLflow. It shall state the required service/network/environment names from the `agent-core` Compose configuration at implementation time, and it shall identify `tdt-observability` as a dependency without transferring Compose deployment ownership to it.

### 3. Deferred source-defect handoff

The separate implementation change begins from the captured minimal reproduction of the unregistered `webhook-selftest` workflow. It must identify the implementation owner, run GitNexus impact analysis before source edits, add a regression that proves the workflow is registered, and distinguish successful registration from any independent public-edge/Tailscale timeout. This planning change neither creates that change nor patches its source.

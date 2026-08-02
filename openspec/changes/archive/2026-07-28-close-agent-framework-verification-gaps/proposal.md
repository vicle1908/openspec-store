## Why

The archived `converge-agent-framework-upstream` change records full completion, but its own implementation evidence and current code show unresolved lifecycle, memory, canonical-routing, gate, checkpoint, topology, and verification gaps. A corrective change is needed now so the archive remains immutable historical evidence while the active specifications, task state, implementation, and release gates converge on one truthful result.

## What Changes

- Create an evidence-backed corrective follow-up rather than rewriting the archived change.
- Reconcile `agent-harness-stage-modules` task completion with the verified implementation state and assign each remaining harness behavior to exactly one active change.
- Complete official lifecycle-hook composition, including callback-return propagation and exactly-once dispatch, and remove legacy hook projections.
- Converge memory composition on the public Harness `Memory` and `MemoryStore` contracts and remove the legacy capability and tool surface.
- Route every `agent-docs-sync` CLI through one canonical implementation and remove legacy workflow entry points.
- Complete `agent-harness` stage toolset composition, topology validation, gate identity and authorization, stable expiry, checkpoint-schema checks, bounded history, and restart-safe resume behavior.
- **BREAKING** Require an explicit approver allowlist for protected harness gates and resolve the acting principal at the trusted CLI/service boundary; self-asserted actor or decision timestamps are not authorization evidence.
- Add cross-repository compatibility, characterization, deployment-bundle, rollback, and strict quality evidence before any corrective task or change is marked complete.
- Reopen completion and archive gates whenever later source/spec changes or a missing required backend invalidate recorded evidence; keep implementation ownership in the overlapping active change.
- Preserve composition over inheritance and avoid new dependencies or cloned upstream abstractions.

### Non-Goals

- Reopening or editing the archived convergence record as if it were still active.
- Moving docs-specific stages or harness-specific topology into `agent-core`.
- Replacing public Pydantic AI, Pydantic AI Harness, or LangGraph contracts with TDT-owned semantic mirrors.
- Broad feature development unrelated to the verified convergence gaps.
- Upgrading framework dependency versions as part of this correction.

## Capabilities

### New Capabilities

- `agent-framework-verification`: Defines evidence, compatibility, archive-correction, and completion gates shared by `agent-core`, `agent-docs-sync`, and `agent-harness`.

### Modified Capabilities

- `agent-harness-workflow`: Clarifies immutable gate issuance identity, authorized-actor validation, and stable expiry across native interrupt re-execution.
- `stage-module-protocol`: Requires whole-graph validation of native edges, reachability, fan-out/fan-in safety, and concurrent write/reducer compatibility.

## Impact

- **Repositories:** `tdt-meta`, `agent-core`, `agent-docs-sync`, and `agent-harness`.
- **Primary code:** lifecycle adapters and SDK composition in `agent-core`; CLI/workflow routing and builders in `agent-docs-sync`; gate models/nodes, runner, stage contracts, and factory composition in `agent-harness`.
- **Compatibility:** caller census and full-suite evidence authorize deletion of legacy hook, memory, builder, and workflow surfaces; no parallel compatibility implementation remains. Protected gates require explicit approver configuration.
- **Dependencies:** no new external dependency is proposed.
- **Verified framework baseline:** Pydantic AI 2.18.0, Pydantic AI Harness 0.11.0, LangGraph 1.2.9, LangGraph checkpoint 4.1.1, and LangGraph Postgres checkpoint 3.1.0. A disposable fresh resolution within the existing declared bounds is the candidate matrix row; committed dependency bounds and lockfiles are not changed by this correction.
- **Risk:** GitNexus reports CRITICAL blast radius for `run_canonical_pipeline`, `_make_gate_node`, and `validate_stage_topology`; HIGH for `run_full_audit` and `build_doc_sync_agent`; the affected processes include docs `check`, `sync`, `audit`, `discover`, and `update`, plus harness `approve`, `reject`, `status`, `astream`, and `report`. Implementation therefore requires characterization tests, incremental edits, and per-repository change detection before commit.
- **Remaining ownership:** `agent-harness-stage-modules` owns scalar reducer reconciliation, checkpoint compatibility, canonical durable configuration, local harness-database bootstrap, and real Postgres restart/resume tests. This corrective change owns only refreshed cross-repository evidence and the final archive gate for that work.
- **Other consumers:** no direct iOS or Android behavior changes are expected; their shared workspace gates benefit from more reliable framework compatibility evidence.

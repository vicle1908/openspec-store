## Why

A 2026-07-28 end-to-end verification of `agent-core`, `agent-docs-sync`, and
`agent-harness` found that all 896 executable tests, lint, formatting, strict
typing, and frozen dependency checks pass, but the documented harness CLI
lifecycle cannot survive a process boundary, two repositories remain below
the 80% coverage gate, skill diagnostics are dominated by duplicate noise, and
docs-sync reports compliance despite material documentation gaps. These gaps
must be closed before the three repositories can be called end-to-end ready.

## What Changes

- Make protected, CLI-driven harness runs fail fast unless an explicit
  approver policy and durable checkpoint backend are configured.
- Make `run`, `status`, `report`, `approve`, and `reject` resolve the same
  configuration, checkpoint backend, and thread identity across processes.
- Return concise actionable CLI errors, including structured JSON errors, for
  missing policy, missing persistence, unknown runs, and backend mismatches.
- Add a Testcontainers-backed disposable real-PostgreSQL test, with an explicit
  external test-DSN override, that proves `run -> restart -> status ->
  approve/reject -> report` without rerunning completed stages or recording
  invalid decisions.
- De-duplicate skill diagnostics by canonical source identity, distinguish
  non-skill catalog documents from malformed skills, and fail diagnostics when
  an explicitly included profile skill cannot be loaded.
- Restrict docs-sync discovery and audit defaults to production source while
  deriving actionable documentation obligations from exported APIs, CLI
  entrypoints, deployment/config artifacts, and explicit mappings. Tests,
  caches, and generated files are excluded; internal production findings are
  informational unless explicitly mapped.
- Separate successful audit execution from documentation compliance and add a
  strict mode that fails on actionable gaps or Diataxis violations.
- Remove tracked Python bytecode artifacts and prevent future cache files from
  entering verification diffs.
- Extend the shared quality-gate inventory to `agent-docs-sync` and
  `agent-harness`, enforce at least 80% coverage in all three repositories, and
  eliminate zero-coverage supported production modules.
- Record one reproducible cross-repository verification manifest containing
  source identity, commands, environment classification, coverage, skipped
  gates, and end-to-end results.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `agent-harness-runner`: Require a recoverable, configuration-consistent CLI
  lifecycle for protected gated runs and define actionable process-level errors.
- `agent-framework-verification`: Require live feature-matrix and real
  PostgreSQL evidence for the three repositories before readiness is claimed.
- `skill-scope-profiles`: Make doctor output canonical, de-duplicated, and
  fail-closed for explicitly requested skills that cannot load.
- `agent-docs-sync`: Define production-source discovery boundaries, truthful
  audit compliance, strict audit behavior, and cache-artifact exclusion.
- `agent-core-quality-gate`: Add `agent-docs-sync` and `agent-harness` to the
  enforced Python repository inventory and coverage/security gates.

## Impact

- **Repositories:** `agent-harness`, `agent-core`, `agent-docs-sync`, plus
  `tdt-meta` for OpenSpec artifacts and verification evidence.
- **Harness APIs:** CLI configuration and error contracts change. Protected
  gated runs continue to fail closed; no implicit approver is introduced.
- **Persistence:** Uses the existing `agent_core.sdk` Postgres checkpointer and
  `TDT_POSTGRES_URL`; Testcontainers supplies only an isolated test backend and
  does not add a second persistence implementation.
- **Docs-sync output:** Audit JSON gains an explicit execution/compliance split;
  strict audit mode may return non-zero for repositories with actionable gaps.
- **Repository hygiene:** Tracked `.pyc` files are removed and cache directories
  remain ignored.
- **Dependencies:** No new runtime dependency is planned. `agent-harness` gains
  `testcontainers[postgres]` as a test-only dependency, managed with `uv`, and
  the PostgreSQL CI gate requires Docker-daemon access or an explicitly
  supplied `TDT_POSTGRES_TEST_URL`. Existing Ruff security rules and
  repository-native test tooling remain the enforcement mechanism.
- **Mobile:** No direct impact on iOS or Android repositories.

### GitNexus blast radius

Pre-proposal analysis followed the `gitnexus-impact-analysis` workflow.

| Area | Risk | Evidence |
|---|---|---|
| `agent_harness.workflow.graph.build_graph` | **CRITICAL** | 8 symbols, 9 processes, 2 modules after fresh indexing; affects run, stream, resume, history, status, report, approve, and reject paths |
| `agent_harness.cli.run` | **HIGH** | 4 direct CLI lifecycle processes |
| `WorkflowRunner` and `GateConfig` | LOW | 1 and 3 direct dependants respectively |
| `agent-core` skill diagnostics/loader | LOW | doctor path plus 13 loader dependants, no indexed execution-flow expansion |
| `agent-docs-sync.tools.ScannerTool` | LOW | 10 dependants across discovery, canonical pipeline, multi-repo, and CLI surfaces; no indexed critical process |

The finalized framework baseline is `langgraph==1.2.9` with
`langgraph-checkpoint-postgres==3.1.0`. The installed public `Command` contract
supports both a single resume value and an interrupt-ID-to-value mapping, and
the shared `agent-core` async checkpointer boundary invokes `setup()` before it
yields the saver.

Implementation of the HIGH/CRITICAL harness paths SHALL begin with
characterization tests and require confirmation before symbol edits.

## Non-goals

- Provisioning developer gateway credentials or changing the expected degraded
  health result when gateway/Postgres services are intentionally unconfigured.
- Implementing `agent-core-scheduler-setup`; that remains owned by the active
  `scheduler-stale-workflow-hardening` change.
- Exercising write-capable LLM generation against production repositories or
  external services during deterministic verification.
- Automatically trusting the current OS user as a gate approver.
- Replacing LangGraph, the shared `agent-core` checkpointer boundary, or the
  canonical `TDT_HOME` configuration contract.

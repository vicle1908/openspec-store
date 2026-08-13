# Proposal: integrate-canonical-cli-projections-v1

## Motivation

Phase 6 of `standardize-agent-llm-environment-resolution-v2` requires wiring the
canonical TDT profile projection into the CLI adapter runtime for `ai-harness-skills`
and `ai-review`. This work crosses two independent repositories and introduces
runtime dependency/package changes. It is isolated into a dedicated successor
change.

## What this change does

1. Establishes a public canonical provider-neutral projection contract in `tdt-core`
   that consumers can rely on without inspecting private `_NewSchemaProjection`.
2. Wires the projection into `ai-harness-skills` `build_runtime()` for Claude and
   Codex adapters.
3. Wires the projection into `ai-review` reviewer launch for Claude, Codex, Kimi,
   and Pi adapters.
4. Proves end-to-end with real CLI invocation and nonce verification.
5. Adds isolated `TDT_HOME` contract tests covering precedence, isolation,
   credentials, provenance, and cache behavior.

## Scope boundaries

| In scope | Out of scope |
|---|---|
| `ai-harness-skills` runtime wiring | `tdt-core` schema changes (already complete) |
| `ai-review` reviewer launch wiring | Registry retirement decision (Phase 5) |
| Canonical projection contract API | OmniRoute or other adapters |
| Dependency strategy documentation | Agent-core/harness/docs-sync changes |
| Real CLI acceptance proofs | |
| Isolated TDT_HOME contract tests | |

## Relationship to v2

This change depends on the completed tdt-core v2 implementation (`75cd519`) being on main. The parent change (`standardize-agent-llm-environment-resolution-v2`) remains linked until this successor is archived and its deltas are synchronized into canonical specs.

## Historical foundation

The initial bridge experiment was developed on the Phase 6 worktree at `b160709`. It was intentionally not treated as implementation evidence. The final consumer wiring superseded it with `ai-harness-skills` main `02d0410` and ai-review main `bd27767`.

## Implementation plan

### Phase A: Canonical projection contract in tdt-core
1. Add public `CanonicalCLISelection` dataclass
2. Add `select_canonical_cli_provider()` and `project_canonical_cli_profile()`
3. Add focused tests
4. Commit as `75cd519`

### Phase B: ai-harness-skills integration (complete)
1. Refresh GitNexus and run impact on `build_runtime()`
2. Write RED integration tests
3. Wire projection into `build_runtime()`
4. Run Ruff, mypy, full suite, diff-check
5. Merge final Phase 6A state at `02d0410`

### Phase C: ai-review integration (complete)
1. Run GitNexus impact on reviewer launch function
2. Write RED/contract tests for Claude, Codex, Kimi, Pi
3. Wire projection at launch boundary, including model and supported reasoning effort
4. Make local review-context fixtures network-independent
5. Run full suite and merge final state at `bd27767`

### Phase D: Acceptance and reconciliation (complete)
1. Run real dual-consumer Codex acceptance with nonce and redaction checks
2. Verify downstream suites and clean-install editable dependency paths
3. Reconcile OpenSpec tasks/evidence and stale references
4. Archive parent and successor changes, then synchronize canonical specs

## Risks

1. `build_runtime()` is CRITICAL risk (16 impacted symbols) — mitigated by RED/GREEN TDD
2. Dependency path non-portability — mitigated by documented workspace convention
3. `ai-review` pre-existing session error — must be classified before claiming green
4. Local consumer field assumptions — mitigated by explicit contract API

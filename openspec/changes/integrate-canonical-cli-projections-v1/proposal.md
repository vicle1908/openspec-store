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

This change depends on `tdt-core` v2 (`21dcd5b`) being on main. The v2 change
(`standardize-agent-llm-environment-resolution-v2`) will remain active until this
successor is validated and integrated, at which point v2 may be archived with an
explicit link to this successor.

## Pre-existing foundation

`ai-harness-skills-phase6` branch contains bridge foundation at `b160709`:
- `tdt_projection.py`: bridge module (9/9 focused GREEN)
- `tdt-core` editable dependency
- NOT wired into `build_runtime()`
- Bridge field assumptions need correction before wiring

## Implementation plan

### Phase A: Canonical projection contract in tdt-core
1. Add public `CanonicalProviderSelection` dataclass
2. Add `select_canonical_provider()` function
3. Add focused tests
4. Commit

### Phase B: ai-harness-skills integration (CRITICAL risk)
1. Refresh GitNexus, run impact on `build_runtime()`
2. Write RED integration tests (8+ minimum)
3. Wire projection into `build_runtime()`
4. Full gate sequence (ruff, mypy, full suite, diff-check)
5. Separate RED/GREEN commits per AGENTS.md

### Phase C: ai-review integration
1. Run GitNexus impact on reviewer launch function
2. Write RED tests for Claude, Codex, Kimi, Pi
3. Wire projection at launch boundary
4. Full gate sequence
5. Separate RED/GREEN commits

### Phase D: Acceptance and reconciliation
1. Real CLI acceptance for each provider/consumer
2. Clean-install downstream verification
3. OpenSpec tasks/evidence update
4. Archive decision

## Risks

1. `build_runtime()` is CRITICAL risk (16 impacted symbols) — mitigated by RED/GREEN TDD
2. Dependency path non-portability — mitigated by documented workspace convention
3. `ai-review` pre-existing session error — must be classified before claiming green
4. `model_settings` field assumptions — mitigated by explicit contract API

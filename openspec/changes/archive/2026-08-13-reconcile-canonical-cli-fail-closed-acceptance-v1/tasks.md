# Tasks: reconcile-canonical-cli-fail-closed-acceptance-v1

## Phase 1: Fail-closed correction

- [x] 1.1 Remove `ProfileResolutionError` catch from ai-review `resolve_canonical_overrides()` — only `OSError` fallback remains for missing config.
  - Commit: `26ed9f9`
  - File: `ai-review/src/ai_review/providers/tdt_projection.py`
- [x] 1.2 Audit ai-harness-skills `tdt_projection.py` — confirmed already propagates `ProfileResolutionError` without catching it. No change needed.
  - Evidence: `ai-harness-skills/src/ai_harness/providers/tdt_projection.py` lines 15-19, no try/except around `project_canonical_cli_profile`

## Phase 2: Durable acceptance artifact

- [x] 2.1 Persist and harden live acceptance script under `ai-review/scripts/verify_phase6_live_acceptance.py`.
  - Final commit: `f1b6e0f` (cleanup verification + no assert control flow + cleanup ordering fix)
  - Earlier commits: `26ed9f9` (initial), `51b55b1` (formatting)

## Phase 3: Verification

- [x] 3.1 Full battery: py_compile, ruff format, ruff check, mypy, pytest — all pass on `f1b6e0f`.
  - ai-review: 200 tests collected, all pass
- [x] 3.2 Live dual-consumer acceptance from committed `f1b6e0f`:
  - Command: `PYTHONPATH="$PWD/src:$HOME/Developer/ai-harness-skills/src:$HOME/Developer/tdt-core/src" uv run python scripts/verify_phase6_live_acceptance.py`
  - Result: `LIVE_ACCEPTANCE_PASS`, EXIT=0
  - nonce: `TDT_PHASE6_AI_REVIEW_18243507`
  - ai-review elapsed: 30.51s, ai-harness elapsed: 7.49s
  - credential leak: none
- [x] 3.3 Cleanup verification: no leftover `/private/tmp/tdt-phase6-acceptance-*` directories after `finally` block.

## Phase 4: Closure

- [x] 4.1 Corrective evidence reconciled with accurate SHAs and test counts.
- [x] 4.2 Validate corrective change with `openspec validate`.
- [x] 4.3 Archive corrective change with `--skip-specs`.
- [x] 4.4 Post-archive full-store validation and scoped commit.

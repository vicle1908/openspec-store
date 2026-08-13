# Tasks: integrate-canonical-cli-projections-v1

## Phase 1: Canonical provider-selection design (COMPLETE)

- [x] 1.1 Write `design.md` with field-source matrix, selection algorithm, multi-provider scenario.
- [x] 1.2 Write `proposal.md` with scope boundaries and risks.

## Phase 2: Public tdt-core selection API (COMPLETE — `75cd519`)

- [x] 2.1 Write RED tests for selector behavior: independent CLI selection, aliases, ambiguity, unsupported settings, credential non-disclosure, immutability, provenance, and legacy compatibility.
  - Evidence: RED checkpoints `99db939` and `dbf6af0`.
- [x] 2.2 Implement `CanonicalCLISelection` dataclass.
- [x] 2.3 Implement `select_canonical_cli_provider()`.
- [x] 2.4 Run focused/full tests, Ruff, mypy, diff-check, and change-scope checks.
  - Evidence: tdt-core `75cd519`; 721 collected, 715 passed, 0 failed, 6 skipped; ad-hoc 21/21.
- [x] 2.5 Commit public contract separately.
  - Evidence: `4ad85f0`, `f165d4d`, `75cd519`.

## Phase 3: ai-harness-skills bridge (COMPLETE — `02d0410`)

- [x] 3.1 Rebase consumer onto the tdt-core contract.
- [x] 3.2 Replace local field guessing with canonical projection.
- [x] 3.3 Write RED runtime-composition tests.
- [x] 3.4 Wire `build_runtime()`.
- [x] 3.5 Run repository gates.
  - Evidence: ai-harness-skills `02d0410`; 606 collected, 602 passed, 0 failed, 4 skipped; focused wiring 25/25.
- [x] 3.6 Keep generated metadata out of product commits.

## Phase 4: ai-review integration (COMPLETE — `bd27767`)

- [x] 4.1 Fresh GitNexus analysis and impact assessment.
  - Evidence: `_build_reviewers` LOW/1; each native reviewer constructor LOW/6; staged scope LOW.
- [x] 4.2 Integrate canonical projection at reviewer construction boundary.
  - Evidence: `ReviewOrchestrator._build_reviewers()` resolves canonical profile once and applies per-CLI projection.
- [x] 4.3 Add RED/contract tests for Claude, Codex, Kimi/Pi capability handling and local fallback.
- [x] 4.4 Preserve model and supported reasoning-effort flags for Claude/Codex; retain capability-safe defaults for Kimi/Pi.
- [x] 4.5 Classify and fix the existing concurrency timing flake and unmocked local-fixture network calls.
- [x] 4.6 Run gates and merge.
  - Evidence: ai-review main `bd27767`; 183 passed, 0 failed; Ruff, mypy, and direct source compilation pass.

## Phase 5: Registry retirement decision (COMPLETE — retained)

- [x] 5.1 Retain registry for legacy aliases and CLI capability metadata.
- [x] 5.2 Keep new-schema `auth_env` provider-local.
- [x] 5.3 Defer removal until all legacy consumers migrate.

## Phase 6: Downstream + live CLI matrix (COMPLETE)

- [x] 6.1 tdt-core: 721 collected, 715 passed, 0 failed, 6 skipped.
- [x] 6.2 ai-harness-skills: 606 collected, 602 passed, 0 failed, 4 skipped.
- [x] 6.3 ai-review: 183 passed, 0 failed.
- [x] 6.4 Existing consumers: agent-core 746/746, agent-harness 343/343, agent-docs-sync 245/245.
- [x] 6.5 Workspace-relative editable tdt-core dependency verified in both consumers.
- [x] 6.6 Real native CLI calls through both consumer boundaries.
  - Evidence harness: `~/Developer/tdt-cli-acceptance/verify_phase6_live.py`.
  - Latest nonce: `TDT_PHASE6_AI_REVIEW_4cbec67f`; ai-review 15.71s; ai-harness 7.76s; both nonce and redaction checks passed.
- [x] 6.7 Record provider, canonical alias, wire model, duration, command, and SHA.
  - Provider: `codex-native` / CLI `codex`; alias `codex-default`; wire model `gpt-5.6-sol`; effort `low`.
  - SHAs: tdt-core `75cd519`, ai-harness-skills `02d0410`, ai-review `bd27767`.

## Phase 7: OpenSpec closure + archive (READY)

- [x] 7.1 Reconcile parent v2 Phase 5/6/9 tasks and README/evidence.
- [x] 7.2 Replace stale deferred/current implementation claims with final evidence.
- [x] 7.3 Update exact SHAs, test counts, live nonce, and durations.
- [x] 7.4 Focused successor validation passes.
  - Evidence: `openspec validate integrate-canonical-cli-projections-v1`.
- [x] 7.5 Full-store validation run.
  - Result: 362 passed, 1 unrelated pre-existing failure in `standardize-omp-homebrew-installation`.
- [x] 7.6 Implementation and store diffs pass `git diff --check`.
- [ ] 7.7 Archive successor, then parent v2, using the normal OpenSpec workflow.
- [ ] 7.8 Validate post-archive canonical specs and synchronize the store.

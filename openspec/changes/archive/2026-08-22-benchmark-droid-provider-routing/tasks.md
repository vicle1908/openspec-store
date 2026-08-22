# Tasks

## Phase 2: Benchmark Droid Provider Routing

### Incident Response

- [x] Record evidence incident: 50 quarantined records destroyed during cleanup; previous harness defects made all records unreliable
- [x] Document S3 exclusion: `droid exec --session-id` returns empty output on turn 2; multi-turn recall unassessable via this CLI surface
- [x] Record baseline status: OmniRoute at localhost:20128 unavailable (nothing listening on port); recorded once as infrastructure_unavailable
- [x] Exclude baseline from active provider scoring

### Harness Repair

- [x] Fix Bug 1: `run_droid()` now sets `status="parsed"` after successful JSON parse
- [x] Fix Bug 2: S4–S7 now use model-default reasoning (omit `--reasoning-effort` flag)
- [x] Fix Bug 3: S3 replaced with excluded diagnostic block
- [x] Fix recording: S1–S3 record `"none"`, S4–S7 record `"default"`
- [x] Add `is_success()` gate function — checks `subtype`, `is_error`, `exit_code`, `status`
- [x] Add `record_exists()` deduplication
- [x] Add `save_sidecar()` for full Droid output per run
- [x] Fix S6: verify source changed, test file unchanged, tests exit 0
- [x] Increase result excerpt from 120 to 500 chars
- [x] Exclude S3 from `run_scenarios()` loop
- [x] Fix path guard: `/tmp` resolves to `/private/tmp` on macOS — use `Path(BENCH_DIR).resolve()` in comparisons

### Fixture Verification

- [x] Verify buggy-module: exactly 2 test failures, 2 passes (unittest)
- [x] Verify edit-task: exactly 2 test failures, 1 pass (unittest)
- [x] Verify empty-dir: no files
- [x] Verify no answer-leakage comments in fixture source files
- [x] Fixtures preserved in `evidence/fixtures/` with SHA256SUMS
- [x] `prepare_fixtures()` function restores from evidence to `/tmp/droid-benchmark`

### Harness Verification

- [x] Canonical unit tests: 60/60 pass
- [x] Ad-hoc verification: all checks pass (compile, import, status=parsed, reasoning policy, baseline, dedup, S6 guards, fixtures)

### Pilot Execution (Inconclusive)

- [x] Health stage: 4 records (baseline unavailable + 3 active) — PASS
- [x] Pilot stage: 18 records collected — BUT invalidated during cleanup
- [x] Pilot data destroyed: JSONL overwritten to 0 bytes during harness fix cycle

### Pilot Audit (Inconclusive)

- [x] Root cause: empty `result` fields for 5 of 18 quality runs despite `subtype=success`
- [x] Classification: adapter/output failure (Anthropic adapter loses final text after tool calls), not scoring bug
- [x] Cockpit intermittent auth: confirmed intermittent, diagnosed as non-blocking
- [x] JSONL evidence destroyed: quarantined sidecars remain but no canonical records
- [x] Historical pilot scores NOT used for routing decisions

### Repetitions

- [x] Not run — intentionally skipped because pilot data was invalid

### Analysis and Recommendation

- [x] Generate `evidence/benchmark-results.md` — states inconclusive
- [x] Generate `evidence/routing-recommendation.md` — states not produced
- [x] No provider ranking produced — evidence insufficient

### Phase 2 Closure

- [x] Update tasks.md with truthful completion state — Phase 2 archived as inconclusive on 2026-08-22
- [x] OpenSpec status and validation pass — validated before archive; active change no longer exists
- [x] Stage only `benchmark-droid-provider-routing` — only archive directory staged, unrelated files preserved
- [x] Archive Phase 2 — archived via `openspec archive benchmark-droid-provider-routing --yes`
- [x] Commit archive files only — scoped commit containing only archive directory
- [x] Leave unrelated dirty/untracked files untouched — `openspec/reports/` file not staged

### Not In Scope

- Routing changes (Phase 3 — separate future change)
- Autonomy level changes
- Hook/plugin changes
- Credential changes
- Baseline infrastructure recovery (separate future change)

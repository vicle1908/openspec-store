# Benchmark Evidence Incident Record

## Status

This archive is **intentionally inconclusive**. No routing recommendation was produced.

## What happened

Phase 1 (provider registration) completed successfully. Phase 2 attempted to benchmark
3 active providers against 6 deterministic scenarios to assign roles (session, spec, worker,
validator, orchestrator). The benchmark was **not completed** due to:

1. **Harness instability**: `run_benchmark.py` was edited 15+ times during this change.
   Evidence was destroyed and recreated multiple times. The harness can no longer be
   considered a stable, reviewable artifact.

2. **Quality scenario output loss**: 5 of 18 quality runs returned `subtype=success`
   with `result=""`. The Claude-Fable adapter loses final text output after tool calls.
   This is an adapter-level limitation, not a model capability issue.

3. **Intermittent provider behavior**: During final verification, `custom:fable-5`
   succeeded once then timed out on retry. `custom:gpt-5.6-sol` timed out on both
   attempts. `custom:Advance` succeeded once. This demonstrates endpoint instability
   that would invalidate any benchmark dataset.

4. **Baseline unavailable**: OmniRoute at `localhost:20128` has nothing listening on
   the port. Recorded as `infrastructure_unavailable`.

5. **S3 multi-turn unassessable**: `droid exec --session-id` returns empty output on
   turn 2. The Factory CLI does not support multi-turn continuation via this surface.

## Evidence state

| Artifact | Status |
|---|---|
| `raw-results.jsonl` | 0 bytes — canonical records destroyed during cleanup |
| `raw-results-pilot-pre-final-harness.jsonl` | 0 bytes — same |
| `evidence/sidecars/` | 21 quarantined JSON files — retained for incident analysis only |
| `evidence/benchmark-results.md` | States inconclusive; no routing produced |
| `evidence/routing-recommendation.md` | States not produced |
| `evidence/provider-health.md` | Records real CLI probes; shows intermittent behavior |
| `evidence/session-continuation.md` | Documents S3 exclusion |
| `evidence/fixtures/` | Deterministic test fixtures with SHA256 checksums |
| `scripts/run_benchmark.py` | 666-line harness; compiles, 60/60 unit tests pass, but was edited too many times to trust |
| `tests/test_harness.py` | Canonical unit tests |

## What was NOT done

- No routing changes were made to any provider, model, or role assignment
- No live `~/.factory/settings.json` was mutated
- No provider was promoted, demoted, or excluded from availability
- No credential rotation was performed
- No baseline was re-enabled

## Why quarantined sidecars are retained

The 21 JSON sidecar files under `evidence/quarantine/pilot-pre-final-harness-sidecars/`
are retained solely for incident analysis. They show what the Claude-Fable adapter
returns when tool calls succeed but the final text answer is lost. This is useful
diagnostic evidence for a future harness revision.

## What must happen next

A future benchmark must:

1. Use **new** OpenSpec change (not this one)
2. Use **inline fixture content** in prompts (not file paths that trigger tool-use)
3. Classify empty output as `adapter_output_unavailable`, not score 0
4. Run one health probe per selector before the pilot, with fresh sessions
5. Run one pilot, audit it manually, then run repetitions only if the pilot passes
6. Use `--no-session` flag for all independent runs to prevent session carryover
7. Record provider/adapter terminology from the live `settings.json` at execution time

## Provider selector reference (from live settings as of 2026-08-22)

| Selector | Model | Provider value | Endpoint |
|---|---|---|---|
| `custom:fable-5` | `fable-5` | `anthropic` | `api.phanmemvip.shop/v1` |
| `custom:Advance` | `Advance` | `anthropic` | `api.giaoduc.online` |
| `custom:gpt-5.6-sol` | `gpt-5.6-sol` | `openai` | `localhost:51006` |
| `custom:dlg/deepseek-v4-pro-0` | `dlg/deepseek-v4-pro` | `generic-chat-completion-api` | `localhost:20128` (unavailable) |

Note: The live `settings.json` uses `anthropic` and `openai` as provider values.
Earlier harness references used "Claude-Fable" — this was the Droid CLI's adapter
enum, not the settings.json provider value. Both refer to the same adapters.

# Proposal: Benchmark Droid Provider Routing

## Why

Phase 1 registered 3 new BYOK models alongside the existing OmniRoute model. All 3 active providers are available in Droid, but no role assignment exists. Without benchmark evidence, any routing change is a guess. The baseline (OmniRoute) is confirmed unavailable and excluded from comparative scoring.

## What Changes

Run identical benchmark workloads against 3 active providers, measure results, and propose role assignments based on evidence. No routing changes are applied during this change.

## Providers Under Test

| Selector | Provider adapter | Model | Notes |
|---|---|---|---|
| `custom:fable-5` | `anthropic` | `fable-5` | Candidate |
| `custom:Advance` | `anthropic` | `Advance` | Candidate |
| `custom:gpt-5.6-sol` | `openai` | `gpt-5.6-sol` | Candidate |

## Baseline

`custom:dlg/deepseek-v4-pro-0` (OmniRoute, `localhost:20128`) is **unavailable**. Port 20128 has no listener. Recorded once as infrastructure_unavailable; excluded from comparative scoring.

## Scored Scenarios (6)

| # | Scenario | Measures | Profile |
|---|---|---|---|
| S1 | Exact response | Protocol and instruction reliability | Reliability (reasoning=none) |
| S2 | Tool round-trip | Tool-call compatibility | Reliability (reasoning=none) |
| S4 | Planning task | Planning quality and constraint coverage | Quality (model default) |
| S5 | Bug diagnosis | Validation and reasoning quality | Quality (model default) |
| S6 | Code edit + test | Worker effectiveness | Quality (model default) |
| S7 | Patch review | Validator effectiveness | Quality (model default) |

## S3: Multi-turn Recall — Unassessable

A real probe confirmed: `droid exec --session-id` returns empty output with exit code 1 on turn 2. This is a Droid CLI limitation, not a model failure. S3 is excluded from scoring, pass-rate denominators, and routing calculations. See `evidence/session-continuation.md`.

## Run Arithmetic

| Stage | Records |
|---|---|
| Health (4: baseline unavailable + 3 active) | 4 |
| Pilot (3 providers × 6 scenarios) | 18 |
| Repeat 2 (3 × 6) | 18 |
| Repeat 3 (3 × 6) | 18 |
| **Total maximum** | **58** |

## What Is NOT Changed During This Change

- No routing changes
- No autonomy level changes
- No hook/plugin changes
- No credential changes

## Acceptance Criteria

1. All 3 active providers tested across 6 scenarios (3 reps each = 54 scored runs)
2. Raw results in `evidence/raw-results.jsonl`
3. Sidecar files for every active run in `evidence/sidecars/`
4. Scoring summary in `evidence/benchmark-results.md`
5. Routing recommendation in `evidence/routing-recommendation.md`
6. No live configuration changes

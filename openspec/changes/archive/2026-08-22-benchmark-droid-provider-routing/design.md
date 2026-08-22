# Design: Benchmark Droid Provider Routing

## Scope

Run identical benchmark workloads against 3 active providers using the live Droid configuration. Propose role assignments based on evidence. No live settings mutation during this change.

## Verified Provider Matrix

| Selector | Provider adapter | Model | Notes |
|---|---|---|---|
| `custom:fable-5` | `anthropic` | `fable-5` | Candidate |
| `custom:Advance` | `anthropic` | `Advance` | Candidate |
| `custom:gpt-5.6-sol` | `openai` | `gpt-5.6-sol` | Candidate |

## Baseline

`custom:dlg/deepseek-v4-pro-0` (OmniRoute, `localhost:20128`) is **unavailable**. Recorded once as infrastructure_unavailable; excluded from comparative scoring.

## Scored Scenarios (6)

| # | Scenario | Measures | Reasoning | Profile |
|---|---|---|---|---|
| S1 | Exact response | Protocol and instruction reliability | `none` | Reliability |
| S2 | Tool round-trip | Tool-call compatibility | `none` | Reliability |
| S4 | Planning task | Planning quality and constraint coverage | default | Quality |
| S5 | Bug diagnosis | Validation and reasoning quality | default | Quality |
| S6 | Code edit + test | Worker effectiveness | default | Quality |
| S7 | Patch review | Validator effectiveness | default | Quality |

## S3: Excluded

Multi-turn session continuation through `droid exec --session-id` is not functional. See `evidence/session-continuation.md`. Excluded from all scoring, pass-rate denominators, and routing calculations.

## Run Arithmetic

| Stage | Records |
|---|---|
| Health (baseline unavailable + 3 active) | 4 |
| Pilot (3 providers × 6 scenarios) | 18 |
| Repeat 2 (3 × 6) | 18 |
| Repeat 3 (3 × 6) | 18 |
| **Total maximum** | **58** |
| **Scored active-provider runs** | **54** |

## Evidence Artifacts

| File | Purpose |
|---|---|
| `evidence/raw-results.jsonl` | Non-secret metadata per run (JSON lines) |
| `evidence/sidecars/<run_id>.json` | Full Droid output per active-provider run |
| `evidence/session-continuation.md` | S3 diagnostic — unassessable |
| `evidence/benchmark-results.md` | Aggregated scoring summary |
| `evidence/routing-recommendation.md` | Evidence-based role assignment proposal |
| `evidence/fixtures/` | Verified test fixtures with SHA256 |

## What Is NOT Changed During This Change

- No routing changes (session default, spec, mission, worker, orchestrator)
- No autonomy level changes
- No hook/plugin changes
- No credential changes
- Existing model retains all current assignments

## Known Risks

- Three repetitions may not capture all variance
- Cockpit streaming was intermittent in Phase 1
- Scoring functions use broad keyword matching — manual audit required before routing
- S4/S5/S7 scoring may produce false positives (model outputs with different vocabulary)

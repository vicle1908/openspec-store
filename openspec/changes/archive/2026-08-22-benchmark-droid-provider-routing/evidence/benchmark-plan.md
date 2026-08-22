# Benchmark Plan: Droid Provider Routing (Revised)

## Fixture Commit SHA

`a02714a866b01454f71f7abaa1eca39509f489f2`

## Providers Under Test

| # | Selector | Provider adapter | Model |
|---|---|---|---|
| 1 | `custom:fable-5` | `anthropic` | `fable-5` |
| 2 | `custom:Advance` | `anthropic` | `Advance` |
| 3 | `custom:gpt-5.6-sol` | `openai` | `gpt-5.6-sol` |

## Baseline

`custom:dlg/deepseek-v4-pro-0` (OmniRoute, `localhost:20128`) is **unavailable**.
Recorded once as infrastructure_unavailable in the health stage.
Excluded from comparative scoring.

## Scored Scenarios (6)

### Reliability Profile (`--reasoning-effort none`)

| # | Scenario | Measures | Scoring |
|---|---|---|---|
| S1 | Exact response | Protocol and instruction reliability | 1/1 exact match |
| S2 | Tool round-trip | Tool-call compatibility | 1/1 ≥2 turns + empty dir confirmed |

### Quality Profile (model-default reasoning, recorded)

| # | Scenario | Measures | Scoring |
|---|---|---|---|
| S4 | Planning task | Planning quality and constraint coverage | 0–3 (steps + health + FastAPI) |
| S5 | Bug diagnosis | Validation and reasoning quality | 0–3 (divide reversal + accumulate overwrite + no false positive on normalize) |
| S6 | Code edit + test | Worker effectiveness | 0/1 (source changed + test unchanged + tests pass) |
| S7 | Patch review | Validator effectiveness | 0–3 (hardcoded credential + MD5 + SQL injection) |

## S3: Multi-turn Recall — EXCLUDED

`droid exec --session-id` returns empty output with exit code 1 on turn 2.
This is a Droid CLI limitation, not provider failure evidence.
Recorded in `evidence/session-continuation.md`.

## Run Arithmetic

| Stage | Records | Notes |
|---|---|---|
| Health | 4 | 1 baseline unavailable + 3 active S1 |
| Pilot | 18 | 3 providers × 6 scenarios |
| Repeat 2 | 18 | 3 providers × 6 scenarios |
| Repeat 3 | 18 | 3 providers × 6 scenarios |
| **Total maximum** | **58** | |
| **Scored active-provider runs** | **54** | Excludes baseline + excludes S3 |

## Execution Rules

- All tests use the live configuration (no `--settings` flag).
- Fixed working directory: `/tmp/droid-benchmark/` (restored from evidence fixtures).
- Fixed autonomy: `--auto low`.
- S1–S3: `--reasoning-effort none`. S4–S7: omit flag (model default).
- Timeout: 120 seconds per run.
- Fresh session for every independent run.
- No credentials or complete settings in evidence.
- Sidecar files preserved for every active-provider run.

## Evidence Files

| File | Purpose |
|---|---|
| `evidence/raw-results.jsonl` | One JSON object per run |
| `evidence/sidecars/<run_id>.json` | Full Droid output per run |
| `evidence/benchmark-results.md` | Aggregated scoring summary |
| `evidence/routing-recommendation.md` | Evidence-based role assignments |
| `evidence/session-continuation.md` | S3 diagnostic |
| `evidence/fixtures/` | Verified test fixtures with SHA256 |

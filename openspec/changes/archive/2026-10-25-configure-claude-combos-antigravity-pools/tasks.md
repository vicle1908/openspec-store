# Tasks

## 1. Configure Combos via OmniRoute REST API

- [x] 1.1 Update `claude-opus-5.5` combo (ID: `4b2430da-0b3b-4b0e-9773-ec0f97adc252`) via `GET /api/combos/{id}` -> merge existing `config` -> `PUT /api/combos/{id}` with 15 explicit model steps for `agy/claude-opus-4-6-thinking` across all 15 active `agy` accounts, verifying `strategy: "auto"`, `candidatePool: ["agy"]`, and `context_cache_protection: false`
- [x] 1.2 Create `claude-sonnet-5.5` combo (ID: `9447399c-856b-4f52-8820-b3bf3dc3f132`) via `POST /api/combos` with 15 explicit model steps for `agy/claude-sonnet-4-6` across all 15 active `agy` accounts, configuring `strategy: "auto"`, `candidatePool: ["agy"]`, `context_cache_protection: false`, and `predictiveTtftMs: 25000`

## 2. Verify Live Routing & Record Evidence

- [x] 2.1 Test live inference across both combos via `POST /v1/chat/completions` with `model: "claude-opus-5.5"` and `model: "claude-sonnet-5.5"`, confirming HTTP 200, authentic routed models (`claude-opus-4-6-thinking` and `claude-sonnet-4-6` in `call_logs`), valid text responses (`CLAUDE-OPUS-5.5_OK` and `CLAUDE-SONNET-5.5_OK`), and record results in `evidence.md`

# Tasks

## 1. Audit & Update Combos

- [x] 1.1 Audit `provider_connections` for `tier: "g1-ultra-tier"` / `subscriptionTier: "Google AI Ultra"` and identify the 3 Ultra connectionIds
- [x] 1.2 Update `gemini-4-argon`, `gemini-4-argon-high`, `gemini-4-argon-medium`, and `gemini-4-argon-low` combos with all 3 Ultra accounts via `GET /api/combos/{id}` -> merge config -> `PUT /api/combos/{id}`, verifying `context_cache_protection: false` and preserved `auto` config

## 2. Verify Live Inference & Record Evidence

- [x] 2.1 Run `POST /v1/chat/completions` with `model: "gemini-4-argon"` and verify HTTP 200 (`"ARGON_3_ULTRA_OK"`) and all 3 Ultra steps across the 4 combos, recording results in `evidence.md`

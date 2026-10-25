# Spec Delta

## ADDED Requirements

### Requirement: Three-Ultra-Account Gemini-4-Argon Combo Routing

OmniRoute SHALL configure `gemini-4-argon`, `gemini-4-argon-high`, `gemini-4-argon-medium`, and `gemini-4-argon-low` combos with explicit connection-scoped model steps for all 3 active Google AI Ultra Antigravity accounts (`62af823b-f3d7-4e6b-87a9-98069167d4f6`, `0532bad4-2486-4286-8f06-510e9c678620`, `338764b8-1cd7-4946-b789-ee5dad4c5073`), preserving `strategy: "auto"` and setting `context_cache_protection: false`.

#### Scenario: All three Ultra accounts present in every gemini-4-argon* combo
- **WHEN** `GET /api/combos/{id}` is queried for `gemini-4-argon`, `gemini-4-argon-high`, `gemini-4-argon-medium`, or `gemini-4-argon-low`
- **THEN** each combo SHALL contain exactly 3 model steps, one for each of `62af823b-f3d7-4e6b-87a9-98069167d4f6`, `0532bad4-2486-4286-8f06-510e9c678620`, and `338764b8-1cd7-4946-b789-ee5dad4c5073`, with `context_cache_protection: false`

#### Scenario: Live gemini-4-argon inference succeeds with 3 Ultra accounts
- **WHEN** `POST /v1/chat/completions` is called with `model: "gemini-4-argon"`
- **THEN** OmniRoute SHALL return HTTP 200 with a successful model response routed through one of the 3 Ultra accounts

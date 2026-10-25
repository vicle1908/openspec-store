## ADDED Requirements

### Requirement: 15-Account Antigravity Auto Pools for `claude-opus-5.5` and `claude-sonnet-5.5` Without Unentitled Custom 5.5 Model IDs

OmniRoute SHALL configure `claude-opus-5.5` (`15` `agy/claude-opus-4-6-thinking` steps, `targetTimeoutMs: 180000`, `predictiveTtftMs: 60000`) and `claude-sonnet-5.5` (`15` `agy/claude-sonnet-4-6` steps, `targetTimeoutMs: 120000`, `predictiveTtftMs: 45000`) with `strategy: "auto"` and `context_cache_protection: false`, and SHALL remove unentitled custom `claude-*-5-5-high` entries from `/api/provider-models` and unstable providers from `auto/*` `candidatePool` lists.

#### Scenario: `claude-opus-5.5` and `claude-sonnet-5.5` route across 15 `agy` accounts with tier-matched timeouts
- **WHEN** `GET /api/combos` is queried for `claude-opus-5.5` (`4b2430da-0b3b-4b0e-9773-ec0f97adc252`) and `claude-sonnet-5.5` (`9447399c-856b-4f52-8820-b3bf3dc3f132`)
- **THEN** `claude-opus-5.5` SHALL contain 15 `kind: "model"` steps targeting `agy/claude-opus-4-6-thinking` with `strategy: "auto"`, `context_cache_protection: false`, `config.targetTimeoutMs: 180000`, and `config.predictiveTtftMs: 60000`
- **AND** `claude-sonnet-5.5` SHALL contain 15 `kind: "model"` steps targeting `agy/claude-sonnet-4-6` with `strategy: "auto"`, `context_cache_protection: false`, `config.targetTimeoutMs: 120000`, and `config.predictiveTtftMs: 45000`

#### Scenario: Unentitled `claude-*-5-5-high` custom models and unstable auto-pool providers are excluded without breaking dedicated combos
- **WHEN** `GET /api/provider-models`, `GET /api/models/alias`, `GET /api/providers`, and `GET /api/combos` are queried
- **THEN** `/api/provider-models` SHALL NOT contain custom `claude-opus-5-5-high` or `claude-sonnet-5-5-high` overrides under `agy` or `antigravity`, and `/api/models/alias` SHALL NOT contain `test-opus-55-high`
- **AND** expired connection `6fb701a5-d060-422c-bc34-0cca543d0eda` (`ollama-cloud`) SHALL have `isActive: false`, while `auto/*` combos SHALL restrict `config.candidatePool` to `["agy", "codex", "github"]` so dedicated combos (`phanmemvip` and `muse-spark-1.3`) remain intact

# omp-provider-routing Specification Delta

## MODIFIED Requirements

### Requirement: Default Role Allocation to Gemini 4 Argon Combo

In `~/.omp/agent/config.yml`, `modelRoles.default` SHALL be assigned to `omniroute/gemini-4-argon`, `modelRoles.plan` to `google-antigravity/gemini-4-argon:high`, `modelRoles.advisor` to `google-antigravity/gemini-3.8-flash:high`, and `modelRoles.tiny` to `google-antigravity/gemini-3.8-flash:low`, while `modelRoles.smol`, `vision`, `slow`, `commit`, and `task` SHALL resolve to `omniroute/gemini-3.8-flash-high:high`.

#### Scenario: Default turn execution via combo
- **WHEN** OMP executes a turn without an explicit `--model` flag under `default` role selection
- **THEN** the request SHALL route to `omniroute/gemini-4-argon` with `retry.fallbackChains` preserving failover to `omniroute/gemini-3.8-flash-high:high` and `google-antigravity/gemini-3.8-flash:high`
- **AND** the response SHALL be served without unmonitored fallback errors

#### Scenario: Live config role alignment with specification
- **WHEN** `~/.omp/agent/config.yml` is inspected
- **THEN** `modelRoles.default` SHALL equal `'omniroute/gemini-4-argon'`, `modelRoles.plan` SHALL equal `'google-antigravity/gemini-4-argon:high'`, `modelRoles.advisor` SHALL equal `'google-antigravity/gemini-3.8-flash:high'`, `modelRoles.tiny` SHALL equal `'google-antigravity/gemini-3.8-flash:low'`, and `modelRoles.smol` SHALL equal `'omniroute/gemini-3.8-flash-high:high'`
- **AND** `retry.fallbackChains['omniroute/gemini-3.8-flash-high']` and `retry.fallbackChains.smol` SHALL both equal `['google-antigravity/gemini-3.8-flash:high', 'google-antigravity/gemini-4-argon:high']`

### Requirement: OMP OmniRoute Catalog SHALL Declare Tiered Gemini 4 Argon Combo Models

The `providers.omniroute.models` list in `~/.omp/agent/models.yml` SHALL declare top-level combo entries `gemini-4-argon-high`, `gemini-4-argon-medium`, and `gemini-4-argon-low` alongside `gemini-4-argon` and `nx/gemini-4-argon`. Each entry SHALL configure `reasoning: true`, `thinking` effort mode (`efforts: [low, medium, high]` with tier-matched `defaultLevel`), `supportsTools: true`, `input: [text, image]`, `contextWindow: 1000000`, `maxTokens: 65536`, and `imageCountBudget: 20`.

#### Scenario: Tiered Gemini 4 Argon combo selectors registered in OMP catalog
- **WHEN** `omp models --json` and `~/.omp/agent/models.yml` are inspected
- **THEN** selectors `omniroute/gemini-4-argon-high`, `omniroute/gemini-4-argon-medium`, `omniroute/gemini-4-argon-low`, `omniroute/gemini-4-argon`, and `omniroute/nx/gemini-4-argon` SHALL be present
- **AND** each entry SHALL report `reasoning: true`, `contextWindow: 1000000`, and `maxTokens: 65536` matching OmniRoute's Antigravity Argon output cap
- **AND** `thinking.defaultLevel` SHALL equal `high` for `gemini-4-argon-high`, `gemini-4-argon`, and `nx/gemini-4-argon`, `medium` for `gemini-4-argon-medium`, and `low` for `gemini-4-argon-low`

#### Scenario: Isolated-profile and live attribution probes succeed without fallback masquerade
- **WHEN** `omp --mode json --no-session --model "<selector>" -p "reply only: pong"` is executed for `omniroute/gemini-4-argon-high`, `omniroute/gemini-4-argon-medium`, `omniroute/gemini-4-argon-low`, and `omniroute/gemini-4-argon`
- **THEN** each invocation SHALL exit with code `0` and emit `"pong"`
- **AND** assistant event metadata SHALL report `provider: "omniroute"` with zero `retry_fallback_applied` or `retry_fallback_succeeded` events

### Requirement: OMP v18.14.1 Background Concurrency, Compaction, and Resilience Tuning

`~/.omp/agent/config.yml` SHALL configure `title.generator: tiny`, `memories.stage1Concurrency: 2`, `contextPromotion.enabled: true`, `compaction` (`reserveTokens: 65536`, `keepRecentTokens: 40000`, `idleEnabled: true`, `asyncEnabled: true`, `dropUseless: true`, `modelThresholds['cockpit/*']: 220000`), `bash` (`gitGuard: true`, `allowCompoundCommands: true`), `lsp` (`enabled: true`, `diagnosticsOnWrite: true`, `diagnosticsOnEdit: true`, `formatOnWrite: true`), and `retry` resilience flags.

#### Scenario: Background settings and compaction prevent Ultra pool starvation
- **WHEN** `~/.omp/agent/config.yml` is parsed with a YAML loader
- **THEN** `title.generator` SHALL equal `'tiny'`, `memories.stage1Concurrency` SHALL equal `2`, `contextPromotion.enabled` SHALL equal `true`, and `lsp` SHALL equal `{ enabled: true, diagnosticsOnWrite: true, diagnosticsOnEdit: true, formatOnWrite: true }`
- **AND** `compaction.reserveTokens` SHALL equal `65536`, `compaction.keepRecentTokens` SHALL equal `40000`, `compaction.idleEnabled` SHALL equal `true`, `compaction.asyncEnabled` SHALL equal `true`, `compaction.dropUseless` SHALL equal `true`, `compaction.modelThresholds['cockpit/*']` SHALL equal `220000`, `bash.gitGuard` SHALL equal `true`, and `bash.allowCompoundCommands` SHALL equal `true`

#### Scenario: Resilience flags and role/wildcard fallback chains are active
- **WHEN** `retry` in `~/.omp/agent/config.yml` is inspected
- **THEN** `retry.rateLimitWalksChain` SHALL equal `true`, `retry.usageAwareFallback` SHALL equal `true`, and `retry.usageReservePolicy` SHALL equal `'auto'`
- **AND** `retry.fallbackChains.advisor`, `retry.fallbackChains.smol`, and `retry.fallbackChains['omniroute/*']` SHALL be defined with validated failover targets

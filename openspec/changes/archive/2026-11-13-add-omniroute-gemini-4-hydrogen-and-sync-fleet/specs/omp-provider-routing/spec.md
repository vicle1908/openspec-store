# Spec Delta

## ADDED Requirements

### Requirement: OMP OmniRoute Catalog SHALL Declare Tiered Gemini 4 Hydrogen Combo Models
The `providers.omniroute.models` list in `~/.omp/agent/models.yml` SHALL declare top-level combo entries `gemini-4-hydrogen`, `gemini-4-hydrogen-xhigh`, `gemini-4-hydrogen-high`, `gemini-4-hydrogen-medium`, and `gemini-4-hydrogen-low` with `1,000,000`-token context windows, `262,144`-token output limits, multimodal tool support, and effort-based thinking tiers.

#### Scenario: Five Gemini 4 Hydrogen combo selectors resolve in OMP catalog with tier-matched thinking defaults
- **WHEN** `omp models omniroute --json` and `~/.omp/agent/models.yml` are inspected
- **THEN** selectors `omniroute/gemini-4-hydrogen`, `omniroute/gemini-4-hydrogen-xhigh`, `omniroute/gemini-4-hydrogen-high`, `omniroute/gemini-4-hydrogen-medium`, and `omniroute/gemini-4-hydrogen-low` SHALL each be present with `reasoning: true`, `supportsTools: true`, `input: ["text", "image"]`, `contextWindow: 1000000`, `maxTokens: 262144`, and `imageCountBudget: 20`
- **AND** `gemini-4-hydrogen` and `gemini-4-hydrogen-xhigh` SHALL declare `thinking.efforts: ["low", "medium", "high", "xhigh"]` (`defaultLevel: "high"` on `gemini-4-hydrogen` and `"xhigh"` on `gemini-4-hydrogen-xhigh`), while `gemini-4-hydrogen-{high,medium,low}` SHALL declare tier-matched `defaultLevel` (`"high"`, `"medium"`, `"low"`)

#### Scenario: Isolated-profile smoke probe verifies Hydrogen routing without fallback masquerade
- **WHEN** an isolated OMP profile (`OMP_CODING_AGENT_DIR`) with empty fallback chains executes `omp --mode json --no-session --model "omniroute/gemini-4-hydrogen:high" -p "reply only: HYDROGEN_OK"`
- **THEN** the invocation SHALL exit with code `0`, emit `"HYDROGEN_OK"`, and report `provider: "omniroute"` with zero `retry_fallback_applied` or `retry_fallback_succeeded` events

### Requirement: OMP Fallback Chains SHALL Cover Gemini 4 Hydrogen Combos and Cross-Family Failover
The `retry.fallbackChains` map in `~/.omp/agent/config.yml` SHALL define explicit tier-matched fail-closed fallback chains for all five `omniroute/gemini-4-hydrogen*` selectors and SHALL insert tier-matched `omniroute/gemini-4-hydrogen*` plus `google-antigravity/gemini-4-hydrogen*` failover legs across `default`, all four `omniroute/gemini-4-carbon*` chains, and all four `omniroute/gemini-4-argon*` chains.

#### Scenario: Hydrogen fallback chains and endpoint-exact google-antigravity selectors resolve cleanly
- **WHEN** `~/.omp/agent/config.yml` and `omp models --kind all --json` are inspected
- **THEN** `retry.fallbackChains['omniroute/gemini-4-hydrogen']` and `retry.fallbackChains['omniroute/gemini-4-hydrogen-high']` SHALL equal `['google-antigravity/gemini-4-hydrogen-high:high', 'omniroute/gemini-3.8-flash-high:high', 'google-antigravity/gemini-3.8-flash:high']`, while `['omniroute/gemini-4-hydrogen-xhigh']`, `['omniroute/gemini-4-hydrogen-medium']`, and `['omniroute/gemini-4-hydrogen-low']` SHALL set their first fallback to `'google-antigravity/gemini-4-hydrogen-xhigh:high'`, `'google-antigravity/gemini-4-hydrogen-medium:medium'`, and `'google-antigravity/gemini-4-hydrogen-low:low'` ahead of `'omniroute/gemini-3.8-flash-high:high'` and `'google-antigravity/gemini-3.8-flash:high'`
- **AND** `retry.fallbackChains.default`, `retry.fallbackChains['omniroute/gemini-4-carbon']`, `retry.fallbackChains['omniroute/gemini-4-carbon-high']`, `retry.fallbackChains['omniroute/gemini-4-carbon-medium']`, and `retry.fallbackChains['omniroute/gemini-4-carbon-low']` SHALL include tier-matched `omniroute/gemini-4-hydrogen-{high:high,high:high,medium:medium,low:low}` and `google-antigravity/gemini-4-hydrogen-{high:high,high:high,medium:medium,low:low}` ahead of `omniroute/gemini-3.8-flash-high:high` with zero unresolvable bare `google-antigravity/gemini-4-hydrogen` references

## MODIFIED Requirements

### Requirement: Default Role Allocation to Gemini 4 Argon Combo
In `~/.omp/agent/config.yml`, `modelRoles.default` SHALL be assigned to `omniroute/gemini-4-carbon`, `modelRoles.task` to `omniroute/gemini-4-hydrogen:high`, `modelRoles.plan` to `google-antigravity/gemini-4-argon:high`, `modelRoles.advisor` to `google-antigravity/gemini-3.8-flash:high`, and `modelRoles.tiny` to `google-antigravity/gemini-3.8-flash:low`, while `modelRoles.smol`, `vision`, `slow`, and `commit` SHALL resolve to `omniroute/gemini-3.8-flash-high:high`.

#### Scenario: Default turn execution via combo
- **WHEN** OMP executes a primary turn under `default` role selection or spawns delegated subagents under `task` role selection
- **THEN** primary `default` turns SHALL route to `omniroute/gemini-4-carbon` and `task` subagents SHALL route to `omniroute/gemini-4-hydrogen:high` with `retry.fallbackChains` preserving failover across Hydrogen and `gemini-3.8-flash-high`
- **AND** responses SHALL be served without unmonitored fallback errors

#### Scenario: Live config role alignment with specification
- **WHEN** `~/.omp/agent/config.yml` is inspected
- **THEN** `modelRoles.default` SHALL equal `'omniroute/gemini-4-carbon'`, `modelRoles.task` SHALL equal `'omniroute/gemini-4-hydrogen:high'`, `modelRoles.plan` SHALL equal `'google-antigravity/gemini-4-argon:high'`, `modelRoles.advisor` SHALL equal `'google-antigravity/gemini-3.8-flash:high'`, `modelRoles.tiny` SHALL equal `'google-antigravity/gemini-3.8-flash:low'`, and `modelRoles.smol` SHALL equal `'omniroute/gemini-3.8-flash-high:high'`
- **AND** `retry.fallbackChains['omniroute/gemini-3.8-flash-high']` and `retry.fallbackChains.smol` SHALL both equal `['google-antigravity/gemini-3.8-flash:high', 'google-antigravity/gemini-4-argon:high']`

### Requirement: Explicit Fail-Closed Fallback for Gemini 4 Argon Combo
The `retry.fallbackChains` configuration in `~/.omp/agent/config.yml` SHALL define an explicit fallback chain for `omniroute/gemini-4-argon` routing through `google-antigravity/gemini-4-argon:high`, `omniroute/gemini-4-hydrogen:high`, and `google-antigravity/gemini-4-hydrogen-high:high` ahead of `omniroute/gemini-3.8-flash-high:high` and `google-antigravity/gemini-3.8-flash:high`.

#### Scenario: Fallback chain configuration
- **WHEN** `~/.omp/agent/config.yml` is inspected programmatically
- **THEN** `retry.fallbackChains['omniroute/gemini-4-argon']` SHALL equal `['google-antigravity/gemini-4-argon:high', 'omniroute/gemini-4-hydrogen:high', 'google-antigravity/gemini-4-hydrogen-high:high', 'omniroute/gemini-3.8-flash-high:high', 'google-antigravity/gemini-3.8-flash:high']`

### Requirement: OMP Fallback Chains SHALL Cover All Gemini 4 Argon Tier Combo Selectors
The `retry.fallbackChains` map in `~/.omp/agent/config.yml` SHALL define explicit tier-matched fail-closed fallback chains for `omniroute/gemini-4-argon-high`, `omniroute/gemini-4-argon-medium`, `omniroute/gemini-4-argon-low`, and `omniroute/gemini-4-argon`, routing through native `google-antigravity/gemini-4-argon*` and tier-matched Hydrogen failover legs ahead of `omniroute/gemini-3.8-flash-high:high` and `google-antigravity/gemini-3.8-flash:high`.

#### Scenario: Tiered Gemini 4 Argon fallback chains configured in config.yml
- **WHEN** `~/.omp/agent/config.yml` is parsed with a YAML loader
- **THEN** `retry.fallbackChains['omniroute/gemini-4-argon-high']`, `retry.fallbackChains['omniroute/gemini-4-argon-medium']`, and `retry.fallbackChains['omniroute/gemini-4-argon-low']` SHALL route through `google-antigravity/gemini-4-argon:{high,medium,low}`, `omniroute/gemini-4-hydrogen-{high:high,medium:medium,low:low}`, and `google-antigravity/gemini-4-hydrogen-{high:high,medium:medium,low:low}` ahead of `'omniroute/gemini-3.8-flash-high:high'` and `'google-antigravity/gemini-3.8-flash:high'`
- **AND** existing `modelRoles` assignments SHALL remain aligned with `omp-provider-routing`

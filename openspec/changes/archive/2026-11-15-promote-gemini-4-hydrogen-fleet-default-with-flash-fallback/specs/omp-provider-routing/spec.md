# Spec Delta: omp-provider-routing

## MODIFIED Requirements

### Requirement: Default Role Allocation to Gemini 4 Argon Combo

In `~/.omp/agent/config.yml`, `modelRoles.default` SHALL be assigned to `omniroute/gemini-4-carbon`, `modelRoles.plan` to `google-antigravity/gemini-4-argon:high`, `modelRoles.advisor` to `google-antigravity/gemini-3.8-flash:high` (retaining native `google-antigravity` multi-turn `thoughtSignature`/`functionResponse` preservation across active Flash-entitled Pro OAuth accounts after pruning banned rows from `~/.omp/agent/agent.db`), `modelRoles.task`, `modelRoles.smol`, `modelRoles.vision`, and `modelRoles.slow` to `omniroute/gemini-4-hydrogen:high`, `modelRoles.commit` to `omniroute/gemini-4-hydrogen:low`, and `modelRoles.tiny` to `omniroute/gemini-4-hydrogen-low:low`.

#### Scenario: Default turn execution via combo
- **WHEN** OMP executes turns under `default`, `task`, `smol`, `vision`, `slow`, `commit`, `advisor`, or `tiny` role selection
- **THEN** `default` SHALL route to `omniroute/gemini-4-carbon`, `smol`/`vision`/`slow`/`task` to `omniroute/gemini-4-hydrogen:high`, `commit` to `omniroute/gemini-4-hydrogen:low`, `tiny` to `omniroute/gemini-4-hydrogen-low:low`, and `advisor` to `google-antigravity/gemini-3.8-flash:high`
- **AND** `~/.omp/agent/agent.db` (`auth_credentials` where `provider = 'google-antigravity'`) SHALL exclude the 7 banned OAuth accounts (`vicgnome19096`, `vicgnome19088`, `ghtkmobile`, `vicgnome19095`, `vicgnome19092`, `vicle1908`, `hongsonle19081952`)
- **AND** `retry.fallbackChains` SHALL preserve failover to `omniroute/gemini-3.8-flash-high:high` and `google-antigravity/gemini-3.8-flash:high` without unmonitored fallback errors

#### Scenario: Live config role alignment with specification
- **WHEN** `~/.omp/agent/config.yml` is inspected
- **THEN** `modelRoles.default` SHALL equal `'omniroute/gemini-4-carbon'`, `modelRoles.plan` SHALL equal `'google-antigravity/gemini-4-argon:high'`, `modelRoles.judge` SHALL equal `'typesafe/jev-1.14.0'`, `modelRoles.advisor` SHALL equal `'google-antigravity/gemini-3.8-flash:high'`, `modelRoles.task`/`smol`/`vision`/`slow` SHALL equal `'omniroute/gemini-4-hydrogen:high'`, `modelRoles.commit` SHALL equal `'omniroute/gemini-4-hydrogen:low'`, and `modelRoles.tiny` SHALL equal `'omniroute/gemini-4-hydrogen-low:low'`
- **AND** `retry.fallbackChains.advisor` SHALL equal `['omniroute/gemini-4-hydrogen:high', 'omniroute/gemini-3.8-flash-high:high']`
- **AND** `retry.fallbackChains.smol` SHALL equal `['google-antigravity/gemini-4-hydrogen-high:high', 'omniroute/gemini-3.8-flash-high:high', 'google-antigravity/gemini-3.8-flash:high']`

### Requirement: OMP OmniRoute Catalog and Fallback Chains SHALL Include Multi-Account Claude 5.5 and Muse Spark 1.3 Combos

In `~/.omp/agent/models.yml`, `providers.omniroute.models` SHALL declare top-level combo entries `claude-opus-5.5`, `claude-sonnet-5.5`, and `muse-spark-1.3` alongside `gemini-4-hydrogen*`, `gemini-4-carbon*`, `gemini-4-argon*`, and `gemini-3.8-flash-high`, and `~/.omp/agent/config.yml` SHALL define explicit `retry.fallbackChains` entries routing those combos plus `phanmemvip/codex-x`, `omniroute/nx/*`, and `cockpit/*` through `omniroute/gemini-4-hydrogen:high` and `google-antigravity/gemini-4-hydrogen-high:high` ahead of `omniroute/gemini-3.8-flash-high:high` and `google-antigravity/gemini-3.8-flash:high`.

#### Scenario: Multi-account Claude 5.5 and Muse Spark 1.3 combos registered in OMP catalog
- **WHEN** `~/.omp/agent/models.yml` and `omp models --json` are inspected
- **THEN** `providers.omniroute.models` SHALL include `claude-opus-5.5` (`maxTokens: 65536`), `claude-sonnet-5.5` (`maxTokens: 65536`), `deepseek-v4.1-flash`, `kimi-k3.1-pro`, `muse-spark-1.3` (`maxTokens: 65536`), `gemini-4-hydrogen{,-xhigh,-high,-medium,-low}` (`maxTokens: 262144`), `gemini-3.8-flash-high`, `gemini-4-carbon{,-high,-medium,-low}`, and `gemini-4-argon{,-high,-medium,-low}` with `reasoning: true`, `supportsTools: true`, and `contextWindow: 1000000`
- **AND** single-connection `agy/claude-opus-4-6-thinking` and broken `mc/muse-spark-1.3` SHALL be absent from `providers.omniroute.models`

#### Scenario: Fail-closed fallback chains cover Claude 5.5, DeepSeek, Kimi, and Muse combos
- **WHEN** `~/.omp/agent/config.yml` is parsed with a YAML loader
- **THEN** `retry.fallbackChains['omniroute/claude-opus-5.5']`, `retry.fallbackChains['omniroute/claude-sonnet-5.5']`, `retry.fallbackChains['omniroute/deepseek-v4.1-flash']`, `retry.fallbackChains['omniroute/kimi-k3.1-pro']`, `retry.fallbackChains['omniroute/muse-spark-1.3']`, `retry.fallbackChains['phanmemvip/codex-x']`, `retry.fallbackChains['omniroute/nx/deepseek-v4.1-flash']`, `retry.fallbackChains['omniroute/nx/deepseek-v4-pro']`, `retry.fallbackChains['omniroute/nx/gemini-4-argon']`, `retry.fallbackChains['omniroute/nx/*']`, and `retry.fallbackChains['omniroute/*']` SHALL each route failover to `['omniroute/gemini-4-hydrogen:high', 'google-antigravity/gemini-4-hydrogen-high:high', 'omniroute/gemini-3.8-flash-high:high', 'google-antigravity/gemini-3.8-flash:high']`
- **AND** `retry.fallbackChains['cockpit/*']` SHALL equal `['google-antigravity/gemini-4-argon:high', 'omniroute/gemini-4-hydrogen:high', 'omniroute/gemini-3.8-flash-high:high', 'google-antigravity/gemini-3.8-flash:high']`
- **AND** `retry.fallbackChains['google-antigravity/*']` SHALL equal `['omniroute/gemini-4-hydrogen:high', 'omniroute/gemini-3.8-flash-high:high', 'google-antigravity/gemini-3.8-flash:high']`
- **AND** `retry.fallbackChains['omniroute/gemini-3.8-flash-high']` SHALL equal `['google-antigravity/gemini-3.8-flash:high', 'omniroute/gemini-4-hydrogen:high']` while `default` and `omniroute/gemini-4-hydrogen{,-xhigh,-high,-medium,-low}` chains remain preserved

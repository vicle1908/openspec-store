# omp-provider-routing Spec Delta

## ADDED Requirements

### Requirement: OMP OmniRoute Catalog and Fallback Chains SHALL Include Multi-Account Claude 5.5 and Muse Spark 1.3 Combos

In `~/.omp/agent/models.yml`, `providers.omniroute.models` SHALL declare top-level combo entries `claude-opus-5.5`, `claude-sonnet-5.5`, and `muse-spark-1.3` in place of single-connection `agy/claude-opus-4-6-thinking` and broken OAuth `mc/muse-spark-1.3`, and `~/.omp/agent/config.yml` SHALL define explicit `retry.fallbackChains` entries for those combos plus `deepseek-v4.1-flash` and `kimi-k3.1-pro`.

#### Scenario: Multi-account Claude 5.5 and Muse Spark 1.3 combos registered in OMP catalog
- **WHEN** `~/.omp/agent/models.yml` and `omp models --json` are inspected
- **THEN** `providers.omniroute.models` SHALL include `claude-opus-5.5` (`maxTokens: 65536`), `claude-sonnet-5.5` (`maxTokens: 65536`), `deepseek-v4.1-flash`, `kimi-k3.1-pro`, `muse-spark-1.3` (`maxTokens: 65536`), `gemini-3.8-flash-high`, and `gemini-4-argon{,-high,-medium,-low}` with `reasoning: true`, `thinking: ["low", "medium", "high"]`, `supportsTools: true`, and `contextWindow: 1000000`
- **AND** single-connection `agy/claude-opus-4-6-thinking` and broken `mc/muse-spark-1.3` SHALL be absent from `providers.omniroute.models`

#### Scenario: Fail-closed fallback chains cover Claude 5.5, DeepSeek, Kimi, and Muse combos
- **WHEN** `~/.omp/agent/config.yml` is parsed with a YAML loader
- **THEN** `retry.fallbackChains['omniroute/claude-opus-5.5']`, `retry.fallbackChains['omniroute/claude-sonnet-5.5']`, `retry.fallbackChains['omniroute/deepseek-v4.1-flash']`, `retry.fallbackChains['omniroute/kimi-k3.1-pro']`, and `retry.fallbackChains['omniroute/muse-spark-1.3']` SHALL each route failover to `['omniroute/gemini-3.8-flash-high:high', 'google-antigravity/gemini-3.8-flash:high']`

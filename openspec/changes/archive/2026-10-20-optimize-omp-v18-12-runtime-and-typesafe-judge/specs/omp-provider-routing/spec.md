# Spec Delta

## ADDED Requirements

### Requirement: Native TypeSafe Jev Judge Role Routing and Fallback Chain

`~/.omp/agent/config.yml` SHALL bind `modelRoles.judge` to `typesafe/jev-1.14.0` and define `retry.fallbackChains.judge` as `['typesafe/jev-latest', 'typesafe/jev-preview']`, while adding `openrouter`, `lm-studio`, `llama.cpp`, and `vscode` to `disabledProviders` so judgment consumers (`find`, `prewalk.auto`, `ttsr.judge`, and `eval` `judge()`) never route to an unfunded `openrouter` credential or fail on local discovery probes.

#### Scenario: Judge role and fallback chain configured in config.yml
- **WHEN** `~/.omp/agent/config.yml` is parsed with a YAML loader
- **THEN** `modelRoles.judge` SHALL equal `'typesafe/jev-1.14.0'`
- **AND** `retry.fallbackChains.judge` SHALL equal `['typesafe/jev-latest', 'typesafe/jev-preview']`
- **AND** `disabledProviders` SHALL include `'openrouter'`, `'lm-studio'`, `'llama.cpp'`, and `'vscode'`

#### Scenario: Live OMP judge catalog and uncached find execution succeed without HTTP 402
- **WHEN** `omp models --kind judge --json` and an uncached `omp find` judgment probe (`OMP_JUDGMENT_CACHE_DB` pointed to a fresh temporary path) are executed
- **THEN** available judge models SHALL resolve exclusively under provider `typesafe` (`typesafe/jev-1.14.0`, `typesafe/jev-latest`, `typesafe/jev-preview`)
- **AND** the judgment probe SHALL complete with `coverage: "complete"`, `stats.requests > 0`, and `stats.failed == 0` with zero `HTTP 402` errors

### Requirement: OMP v18.12.2 Runtime Settings and Legacy Key Hygiene

`~/.omp/agent/config.yml` SHALL configure `isolation.backend: apfs`, `externalThinking: false`, `providers.tinyModelDevice: mlx`, and `tui.renderMermaid: true`, and SHALL omit the superseded top-level keys `memories`, `renderMermaid`, `calc`, and `bashInterceptor.redirects` while preserving `memory.backend: local` and `bashInterceptor.enabled: true`.

#### Scenario: Runtime optimization settings and clean schema in config.yml
- **WHEN** `~/.omp/agent/config.yml` and `omp config` are inspected on `omp v18.12.2`
- **THEN** `isolation.backend` SHALL equal `'apfs'`, `externalThinking` SHALL equal `false`, and `providers.tinyModelDevice` SHALL equal `'mlx'`
- **AND** top-level keys `memories`, `renderMermaid`, `calc`, and `bashInterceptor.redirects` SHALL be absent while `memory.backend: local` and `bashInterceptor.enabled: true` remain active

### Requirement: Cockpit Reasoning Metadata and Wildcard Fallback Chain Coverage

`~/.omp/agent/models.yml` SHALL declare `reasoning: true`, `thinking` effort mode (`efforts: [low, medium, high, xhigh]`), `supportsTools: true`, and `imageCountBudget: 20` on all `providers.cockpit.models` entries, and `~/.omp/agent/config.yml` SHALL use `retry.fallbackChains['cockpit/*']` and replace `google/*` and `google-vertex/*` in `retry.fallbackChains['google-antigravity/*']` with `google-antigravity/gemini-3.8-flash:high`.

#### Scenario: Cockpit models declare reasoning efforts and wildcard fallback chain
- **WHEN** `~/.omp/agent/models.yml` and `~/.omp/agent/config.yml` are inspected
- **THEN** every model under `providers.cockpit.models` SHALL declare `reasoning: true`, `supportsTools: true`, `imageCountBudget: 20`, and `thinking.efforts` containing `['low', 'medium', 'high', 'xhigh']`
- **AND** `retry.fallbackChains['cockpit/*']` SHALL equal `['google-antigravity/gemini-4-argon:high', 'omniroute/gemini-3.8-flash-high', 'google-antigravity/gemini-3.8-flash:high']` without duplicate `cockpit/gpt-6-astra` or `cockpit/gpt-6.1-sol` keys
- **AND** `retry.fallbackChains['google-antigravity/*']` SHALL equal `['omniroute/gemini-3.8-flash-high', 'google-antigravity/gemini-3.8-flash:high']`

### Requirement: OmniRoute Retired Model Pruning and v18.12.0 Context Window Alignment

`~/.omp/agent/models.yml` SHALL omit all retired `sh/*` model entries under `providers.omniroute.models` and the retired `omniroute-chat` provider block, and SHALL set `contextWindow: 128000` on `nx/deepseek-v4.1-flash` and `contextWindow: 200000` on `providers.omniroute-anthropic.models` (`pm/Claude-Fable`, `pm/Claude-Opus`, `pm/Claude-Sonnet`) to match live OmniRoute `/v1/models` limits under OMP `v18.12.0+` custom catalog precedence.

#### Scenario: Retired sh/* models removed and context windows aligned with live OmniRoute
- **WHEN** `~/.omp/agent/models.yml` and `omp models --json` are inspected against `http://127.0.0.1:20128/v1/models`
- **THEN** no `sh/*` model ID or `omniroute-chat` provider SHALL exist in `~/.omp/agent/models.yml`
- **AND** `omniroute/nx/deepseek-v4.1-flash` SHALL report `contextWindow: 128000` and `omniroute-anthropic/pm/Claude-*` SHALL report `contextWindow: 200000`

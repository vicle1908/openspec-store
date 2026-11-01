# omniroute-agent-cli-routing Spec Delta

## ADDED Requirements

### Requirement: Workstation Coding Agents and Editors SHALL Expose All Active High-Usage OmniRoute Combos and No-Memory Headers Under Existing Providers
All configurable workstation coding agents and editor integrations SHALL register the 10 active OmniRoute combos (`gemini-3.8-flash-high`, `gemini-4-argon*`, `claude-opus-5.5`, `claude-sonnet-5.5`, `deepseek-v4.1-flash`, `kimi-k3.1-pro`, and `muse-spark-1.3`) under their active OmniRoute provider blocks, set `x-omniroute-no-memory: "true"` where custom headers are supported, and remediate broken defaults on `kilo`, `zed`, and `cline`.

#### Scenario: All 10 active OmniRoute combos registered across OpenAI Responses, Anthropic Messages, and Chat Completions clients
- **WHEN** the active OmniRoute provider catalogs of `omp`, `pi`, `prime-agent`, `hermes`, `opencode`, `kilo`, `codex` (`~/.codex/cockpit-model-catalog.json`), `kimi` (`~/.kimi-code/config.toml`), `grok`, `goose`, `droid`, `claude` (`~/.claude/profiles/omniroute-pm.json`), `muse`, `qwen`, and `zed` are inspected
- **THEN** each surface SHALL declare `gemini-3.8-flash-high`, `gemini-4-argon`, `gemini-4-argon-high`, `gemini-4-argon-medium`, `gemini-4-argon-low`, `claude-opus-5.5`, `claude-sonnet-5.5`, `deepseek-v4.1-flash`, `kimi-k3.1-pro`, and `muse-spark-1.3` (`1,000,000` context window; `65,536` max output tokens matched to each client's protocol so `max_tokens`-sending clients stay within `65,536`)
- **AND** `~/.codex/cockpit-model-catalog.json` (`mode 0644`) SHALL include `"gemini-3.8-flash-high"` in `models[]` so interactive `/model` pickers can select or return to the default `gemini-3.8-flash-high` slug

#### Scenario: Custom-header-capable clients send `x-omniroute-no-memory: "true"` to protect prompt prefix caches
- **WHEN** `omp` (`~/.omp/agent/models.yml`), `pi` (`~/.pi/agent/models.json`), `prime-agent` (`~/.prime/agent/models.json`), `hermes` (`~/.hermes/config.yaml`), `opencode` (`~/.config/opencode/opencode.json`), `kilo` (`~/.config/kilo/kilo.jsonc`), `codex` (`~/.codex/config.toml`), `kimi` (`~/.kimi-code/config.toml`), and `goose` (`~/.config/goose/custom_providers/custom_omniroute.json`) are inspected
- **THEN** every active OmniRoute provider block in those configurations SHALL declare `"x-omniroute-no-memory": "true"` in its HTTP headers map (`headers`, `options.headers`, `http_headers`, or `custom_headers`) so OmniRoute does not inject `Memory context:` prefixes into coding prompts

#### Scenario: Broken default models in Kilo Code, Zed Editor, and Cline are remediated to `gemini-3.8-flash-high` while healthy defaults remain untouched
- **WHEN** `~/.config/kilo/kilo.jsonc`, `~/.config/zed/settings.json`, `~/.cline/data/settings/providers.json`, and `~/.claude/profiles/omniroute-pm.json` are inspected
- **THEN** `~/.config/kilo/kilo.jsonc` SHALL set `"model": "omniroute-responses/gemini-3.8-flash-high"` and `"small_model": "omniroute-responses/gemini-3.8-flash-high"`
- **AND** `~/.config/zed/settings.json` SHALL set `agent.default_model.model` to `"gemini-3.8-flash-high"` and omit retired `dlg/*`, `dlg1/*`, `ollamacloud/*`, `cx/*`, `gc/*`, and `mc/muse-spark-1.3` entries from `language_models.openai_compatible.omniroute.available_models`
- **AND** `~/.cline/data/settings/providers.json` (`mode 0600`) SHALL set `providers.openai-compatible.settings.model` to `"gemini-3.8-flash-high"`, `baseUrl` to `"http://localhost:20128/v1"`, and `reasoning.enabled` to `true`
- **AND** `~/.claude/profiles/omniroute-pm.json` SHALL map `env.ANTHROPIC_DEFAULT_OPUS_MODEL` to `"claude-opus-5.5"` and `env.ANTHROPIC_DEFAULT_SONNET_MODEL` to `"claude-sonnet-5.5"` while keeping `"model": "gemini-3.8-flash-high"` and `env.ANTHROPIC_MODEL: "gemini-3.8-flash-high"`
- **AND** startup defaults on `omp`, `pi`, `prime-agent`, `hermes`, `opencode`, `codex`, `kimi`, `grok`, `goose`, `droid`, `muse`, and `qwen` SHALL remain byte-identical

## MODIFIED Requirements

### Requirement: Encapsulated Nested Combo on `muse-spark-1.3`, Auto-Scored Opus Pool on `claude-opus-5.5`, and Loopback API Bridge Port `20129`
OmniRoute SHALL configure `muse-spark-1.3` (`strategy: "priority"`, `nestedComboMode: "execute"`, `targetTimeoutMs: 25000`, step `[1]` pinned to `ea0d6c23-85c0-42c8-abdf-8186effd3371`) and `claude-opus-5.5` (`strategy: "auto"`, `nestedComboMode: "flatten"`, `targetTimeoutMs: 180000`, `predictiveTtftMs: 60000`) with `context_cache_protection: false`, pin `gemini-4-argon*` to the three `Ultra` `agy` accounts, and set `API_HOST=0.0.0.0` for port `20129`.

#### Scenario: `muse-spark-1.3` executes `gemini-3.8-flash-high` sub-combo without model-pin warning
- **WHEN** a request targets `muse-spark-1.3`
- **THEN** OmniRoute SHALL match `muse-spark-1.3` (`context_cache_protection: false`, `nestedComboMode: "execute"`, `targetTimeoutMs: 25000`) and execute `gemini-3.8-flash-high` using its 16-factor `auto` strategy without logging false `provider durably unhealthy — dropping pin` warnings, while step `[1]` (`agy/gemini-3.8-flash-medium`) declares `connectionId: "ea0d6c23-85c0-42c8-abdf-8186effd3371"` and `label: "vicgnome19092@gmail.com"`

#### Scenario: `claude-opus-5.5` load-balances and pins across all 8 Opus accounts via `auto` strategy
- **WHEN** a request targets `claude-opus-5.5`
- **THEN** OmniRoute SHALL score all 14 active `agy` Opus accounts (`11` Pro and `3` Ultra, excluding banned `47f334b1-b801-41f6-a709-4ebabb7a86d6` and `d5c3465f-9797-4b4b-a937-c3e653e168fb`) using 16-factor `auto` routing (`tierPriority`, `health`, `quota`) and pin multi-turn sessions via `applySessionStickiness` without flattening `gemini-3.8-flash-high` into the `auto` candidate pool

#### Scenario: Host loopback port `20129` reaches container API bridge
- **WHEN** a request is sent to `http://127.0.0.1:20129/v1/models` or `http://127.0.0.1:20129/v1/responses`
- **THEN** `apiBridgeServer.ts` (`API_HOST=0.0.0.0` inside the container, mapped to `127.0.0.1:20129:20129` on the host) SHALL accept the connection and serve the response

### Requirement: 15-Account Antigravity Auto Pools for `claude-opus-5.5` and `claude-sonnet-5.5` Without Unentitled Custom 5.5 Model IDs
OmniRoute SHALL configure `claude-opus-5.5` (`targetTimeoutMs: 180000`, `predictiveTtftMs: 60000`) and `claude-sonnet-5.5` (`targetTimeoutMs: 120000`, `predictiveTtftMs: 45000`) with `14` active `agy` steps matching each connection's `syncedAvailableModels` entry (`0` `combo-ref` steps, `context_length: 1000000`, `strategy: "auto"`, `context_cache_protection: false`), excluding banned connections `47f334b1` and `d5c3465f`.

#### Scenario: `claude-opus-5.5` and `claude-sonnet-5.5` route across 15 `agy` accounts with tier-matched timeouts
- **WHEN** `GET /api/combos` is queried for `claude-opus-5.5` (`4b2430da-0b3b-4b0e-9773-ec0f97adc252`) and `claude-sonnet-5.5` (`9447399c-856b-4f52-8820-b3bf3dc3f132`)
- **THEN** `claude-opus-5.5` SHALL contain 14 `kind: "model"` steps matching each active connection's `syncedAvailableModels` catalog (`agy/claude-opus-5-5-high` on `38782750` and `agy/claude-opus-4-6-thinking` on the remaining 13 active `agy` accounts, excluding banned `47f334b1` and `d5c3465f`) with `context_length: 1000000`, `strategy: "auto"`, `context_cache_protection: false`, `config.targetTimeoutMs: 180000`, and `config.predictiveTtftMs: 60000`
- **AND** `claude-sonnet-5.5` SHALL contain 14 `kind: "model"` steps matching each active connection's `syncedAvailableModels` catalog (`agy/claude-sonnet-5-5-high` on `38782750` and `agy/claude-sonnet-4-6` on the remaining 13 active `agy` accounts, excluding banned `47f334b1` and `d5c3465f`) with `context_length: 1000000`, `strategy: "auto"`, `context_cache_protection: false`, `config.targetTimeoutMs: 120000`, and `config.predictiveTtftMs: 45000`

#### Scenario: Unentitled `claude-*-5-5-high` custom models and unstable auto-pool providers are excluded without breaking dedicated combos
- **WHEN** `GET /api/provider-models`, `GET /api/models/alias`, `GET /api/providers`, and `GET /api/combos` are queried
- **THEN** `/api/provider-models` SHALL NOT contain custom `claude-opus-5-5-high` or `claude-sonnet-5-5-high` overrides under `agy` or `antigravity`, and `/api/models/alias` SHALL NOT contain `test-opus-55-high`
- **AND** expired connection `6fb701a5-d060-422c-bc34-0cca543d0eda` (`ollama-cloud`) SHALL have `isActive: false`, while `auto/*` combos SHALL restrict `config.candidatePool` to `["agy", "codex", "github"]` so dedicated combos (`phanmemvip` and `muse-spark-1.3`) remain intact

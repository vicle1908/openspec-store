# Spec Delta: omniroute-agent-cli-routing

## MODIFIED Requirements

### Requirement: Gemini combo SHALL be configured as default across supported coding agents
Supported coding-agent CLIs and editors (`pi`, `omp`, `codex`, `opencode`, `kilo`, `grok`, `droid`, `prime-agent`, `goose`, `kimi-code`, `zed`, `cline`, `continue`, and Claude Code OmniRoute profile) SHALL configure `gemini-4-hydrogen` as their default model via OmniRoute (`/v1/responses` where supported, or OpenAI/Anthropic ingress for dialect-specific clients) with role-tiered thinking efforts, while retaining `gemini-3.8-flash-high` as explicit fallback and updating Hermes Agent's MoA OmniRoute slots to `omniroute:gemini-4-hydrogen`.

#### Scenario: Supported CLIs default to Gemini combo
- **WHEN** coding agents are invoked with default model selection
- **THEN** requests SHALL route through OmniRoute's `gemini-4-hydrogen` combo
- **AND** clients supporting the Responses API SHALL use `/v1/responses`
- **AND** all existing alternative providers and `gemini-3.8-flash-high` fallback entries SHALL remain preserved
- **AND** credentials SHALL resolve via environment indirection (`OMNIROUTE_API_KEY`) with zero literal secrets committed

#### Scenario: All supported coding agents default to OmniRoute Gemini 3.8 Flash High
- **WHEN** any supported coding agent CLI (`pi`, `prime-agent`, `hermes`, `opencode`, `kilo`, `codex`, `kimi-code`, `grok`, `goose`, `droid`, `muse`, `qwen`, `claude`), editor (`zed`, `cline`), or tool (`continue`) is launched without an explicit model override
- **THEN** it SHALL resolve `gemini-4-hydrogen` (or `muse-spark-1.3` backed by `gemini-4-hydrogen-high` on Muse; `omniroute-gemini-4-hydrogen` on Grok; `custom:OmniRoute-gemini-4-hydrogen` on Droid) via OmniRoute as its primary default
- **AND** fast/background slots (`claude` `ANTHROPIC_DEFAULT_HAIKU_MODEL` / `CLAUDE_CODE_SUBAGENT_MODEL`, `opencode` and `kilo` `small_model` and `explore`/`librarian`/`docwriter` agents, `zed` `commit_message_model`/`thread_summary_model`, `continue` `tabAutocompleteModel` with `completionOptions.reasoning: false`) SHALL use `gemini-4-hydrogen-low`, while Grok `~/.grok/config.toml` sets `[models].default = "omniroute-gemini-4-hydrogen"` without introducing unknown keys
- **AND** TUI state files (`~/.local/state/opencode/model.json` `recent`/`favorite` and `~/.local/state/kilo/model.json` `model.code.modelID`, without injecting a `recent` array into Kilo) plus pre-existing secondary providers and `gemini-3.8-flash-high` fallback entries SHALL align with `gemini-4-hydrogen` primary and retain `gemini-3.8-flash-high` accessible

#### Scenario: Hermes Agent default MoA is preserved
- **WHEN** `~/.hermes/config.yaml` (`mode 0600`) is inspected or loaded
- **THEN** `model.provider` SHALL remain `moa` and `model.default` SHALL remain `default`
- **AND** `providers.omniroute.model` SHALL equal `gemini-4-hydrogen`, `moa.presets.default` OmniRoute slots plus root `moa.{reference_models,aggregator}` SHALL target `omniroute` / `gemini-4-hydrogen` (`reasoning_effort: high` reference, `reasoning_effort: xhigh` aggregator), `moa.presets.deep` OmniRoute reference SHALL target `omniroute` / `gemini-4-hydrogen` (`reasoning_effort: high`), and `fallback_providers` SHALL equal `[{provider: omniroute, model: gemini-3.8-flash-high}]` (without adding dead `127.0.0.1:8045` `antigravity` entries)

#### Scenario: Kimi Code CLI defaults to OmniRoute Gemini 3.8 Flash High
- **WHEN** Kimi Code CLI (`kimi`) is launched without an explicit model override
- **THEN** it SHALL resolve `default_model = "gemini-4-hydrogen"` in `~/.kimi-code/config.toml` (`mode 0600`)
- **AND** model `gemini-4-hydrogen` SHALL route through provider `omniroute-anthropic` targeting `http://localhost:20128`
- **AND** `[models.gemini-4-hydrogen]` SHALL declare `max_context_size = 1000000`, `max_output_size = 65536`, `capabilities = ["thinking", "image_in", "tool_use"]`, `default_effort = "high"`, and `support_efforts = ["low", "medium", "high"]` (never `"xhigh"`)
- **AND** `[models.gemini-3-8-flash-high]` SHALL remain present as fallback

### Requirement: Goose provider declarations SHALL point to OmniRoute loopback without legacy port residue
The custom OmniRoute provider definition in `~/.config/goose/custom_providers/custom_omniroute.json` and Goose runtime configuration in `~/.config/goose/config.yaml` SHALL route default inference to `gemini-4-hydrogen` over OpenAI Chat Completions (`http://localhost:20128/v1`, `OPENAI_BASE_PATH: chat/completions`), retain `gemini-3.8-flash-high` (`context_limit: 1048576`, `supports_vision: true`) in `custom_omniroute.json`, and omit decommissioned model routes and legacy ports.

#### Scenario: Custom provider routes to canonical OmniRoute loopback
- **WHEN** `~/.config/goose/custom_providers/custom_omniroute.json` and `~/.config/goose/config.yaml` are inspected
- **THEN** `config.yaml` SHALL set `active_provider: custom_omniroute`, `providers.custom_omniroute.model: gemini-4-hydrogen`, `GOOSE_THINKING_EFFORT: high`, and `GEMINI3_THINKING_LEVEL: high`
- **AND** `custom_omniroute.json` `base_url` SHALL be `http://localhost:20128/v1`, `timeout_seconds` SHALL equal `600`, and both `gemini-4-hydrogen` and fallback `gemini-3.8-flash-high` SHALL declare `context_limit: 1048576` and `supports_vision: true`
- **AND** decommissioned model identifiers (`ollamacloud/*`, `sh/*`) SHALL be absent

#### Scenario: Legacy port residue eliminated from default configuration
- **WHEN** `~/.config/goose/config.yaml` is inspected
- **THEN** `OPENAI_BASE_URL` and `OPENAI_HOST` SHALL point to `http://localhost:20128/v1` or be cleared
- **AND** port `51006` SHALL NOT appear anywhere in `config.yaml`
- **AND** `OPENAI_BASE_PATH` SHALL point to `chat/completions`

### Requirement: Muse Code CLI SHALL route default inference through OmniRoute combo `muse-spark-1.3` with sanctioned bearer transport pinning
Meta Muse Code (`muse`) SHALL target local OmniRoute (`http://127.0.0.1:20128/v1`) using explicit `endpoint_transport` bearer pinning (`"auth": "bearer"`) and default model `"muse-spark-1.3"`, while OmniRoute SHALL define combo `muse-spark-1.3` (`nestedComboMode: "execute"`) referencing `gemini-4-hydrogen-high` ahead of `combo-ref: gemini-3.8-flash-high` fallback so `POST /v1/responses` requests execute Hydrogen cleanly without changing Muse's front-door model ID or failing onto banned accounts.

#### Scenario: Sanctioned front-door bearer transport prevents CLI auth withholding
- **WHEN** `~/.config/muse/settings.json` is loaded by Muse Code CLI (`v1.0.1+`)
- **THEN** `schema_version` SHALL equal `1`
- **AND** `endpoint_transport.base_url` SHALL equal `"http://127.0.0.1:20128/v1"` with `endpoint_transport.auth` set to `"bearer"`
- **AND** `provider` SHALL equal `"meta"` with `model` set to `"muse-spark-1.3"`
- **AND** Muse Code SHALL transmit the `Authorization: Bearer <OMNIROUTE_API_KEY>` header to `127.0.0.1:20128` without triggering front-door bearer withholding

#### Scenario: OmniRoute combo `muse-spark-1.3` intercepts bare model requests and preserves namespace tools
- **WHEN** Muse Code sends a streaming `POST /v1/responses` request with `"model": "muse-spark-1.3"` and `"type": "namespace"` tool definitions (such as `namespace: "muse"`)
- **THEN** OmniRoute's combo resolver SHALL match `muse-spark-1.3` (`context_length: 1000000`, `context_cache_protection: false`, `nestedComboMode: "execute"`) before static provider lookup and route inference to `combo-ref: gemini-4-hydrogen-high` with `combo-ref: gemini-3.8-flash-high` as fallback
- **AND** OmniRoute SHALL flatten incoming `namespace` tool groups for upstream execution and restore `{"namespace": "muse", "name": "<tool>"}` on returned `function_call` SSE items
- **AND** `GET /v1/muse-code/models` SHALL return HTTP 200 advertising `muse-spark-1.3`

#### Scenario: Unpinned `--base-url` override or missing combo fails closed
- **WHEN** a custom `--base-url` is invoked without matching `endpoint_transport` bearer configuration or when `OMNIROUTE_API_KEY` is absent from `~/.config/muse/auth.json`
- **THEN** the request SHALL be rejected with an explicit authentication error (`401`) or front-door withholding warning rather than falling back to unauthenticated external endpoints

#### Scenario: Pre-flight Responses keepalive and catalog compatibility with Rust SSE decoder
- **WHEN** `muse exec --disable-approval --no-session-log` executes prompt and tool-calling turns against `http://127.0.0.1:20128/v1`
- **THEN** the SSE stream and `/v1/muse-code/models` payload delivered to Muse Code SHALL NOT cause a Rust `serde` deserialization failure on synthetic `response.in_progress` frames or catalog metadata

### Requirement: Qwen Code CLI SHALL route default inference through OmniRoute and multiplex MCP via mcp-router
Qwen Code (`qwen` v0.25.2+) SHALL configure `~/.qwen/settings.json` (`$version: 4`, mode `0600`) with `modelProviders.openai` array entries for `gemini-4-hydrogen*` and fallback `gemini-3.8-flash-high` targeting `http://localhost:20128/v1` via `OMNIROUTE_API_KEY`, `security.auth.selectedType: "openai"`, `model.name: "gemini-4-hydrogen"`, and `mcpServers.mcp-router` while preserving existing Orca lifecycle hooks.

#### Scenario: Qwen Code resolves OmniRoute default model and mcp-router
- **WHEN** `~/.qwen/settings.json` is loaded by Qwen Code CLI (`qwen --safe-mode -p "reply only: pong" -y`)
- **THEN** `modelProviders.openai` SHALL be a `ModelConfig[]` array containing `"gemini-4-hydrogen"` (with tier entries) and `"gemini-3.8-flash-high"`, with `baseUrl: "http://localhost:20128/v1"` and `envKey: "OMNIROUTE_API_KEY"`
- **AND** `security.auth.selectedType` SHALL equal `"openai"` and `model.name` SHALL equal `"gemini-4-hydrogen"`
- **AND** `mcpServers.mcp-router` SHALL connect via `command: "npx"`, `args: ["-y", "@mcp_router/cli@latest", "connect"]`, `trust: true`
- **AND** `~/.qwen/settings.json` SHALL have permission mode `0600` while retaining all existing Orca lifecycle hook arrays

### Requirement: Encapsulated Nested Combo on `muse-spark-1.3`, Auto-Scored Opus Pool on `claude-opus-5.5`, and Loopback API Bridge Port `20129`
OmniRoute SHALL configure `muse-spark-1.3` (`strategy: "priority"`, `nestedComboMode: "execute"`, `targetTimeoutMs: 180000`, step `[0]` `combo-ref: gemini-4-hydrogen-high`, step `[1]` `combo-ref: gemini-3.8-flash-high`) and `claude-opus-5.5` (`strategy: "quota-weighted"`, `targetTimeoutMs: 180000`, `predictiveTtftMs: 0`) with `context_cache_protection: false`, and set `API_HOST=0.0.0.0` for port `20129`.

#### Scenario: `muse-spark-1.3` executes `gemini-3.8-flash-high` sub-combo without model-pin warning
- **WHEN** a request targets `muse-spark-1.3`
- **THEN** OmniRoute SHALL match `muse-spark-1.3` (`context_cache_protection: false`, `nestedComboMode: "execute"`, `targetTimeoutMs: 180000`), execute `combo-ref: gemini-4-hydrogen-high` as an encapsulated unit, and fall back to step `[1]` (`combo-ref: gemini-3.8-flash-high`, with banned `ea0d6c23` absent) without logging false `provider durably unhealthy — dropping pin` warnings

#### Scenario: `claude-opus-5.5` load-balances and pins across all 8 Opus accounts via `auto` strategy
- **WHEN** a request targets `claude-opus-5.5`
- **THEN** OmniRoute SHALL weight active non-banned Pro `agy` Opus accounts (excluding banned `38782750`, `47f334b1`, and `d5c3465f`) using `quota-weighted` routing and pin multi-turn sessions via `applySessionStickiness`

#### Scenario: Host loopback port `20129` reaches container API bridge
- **WHEN** a request is sent to `http://127.0.0.1:20129/v1/models` or `http://127.0.0.1:20129/v1/responses`
- **THEN** `apiBridgeServer.ts` (`API_HOST=0.0.0.0` inside the container, mapped to `127.0.0.1:20129:20129` on the host) SHALL accept the connection and serve the response

### Requirement: Workstation Coding Agents and Editors SHALL Expose Tiered Gemini 4 Hydrogen Combos Without Altering Companion Defaults
All configurable workstation coding agents and editor integrations on `iosteam-mac-mini` SHALL configure `gemini-4-hydrogen` as their primary default (retaining `gemini-3.8-flash-high` as fallback), register all 5 `gemini-4-hydrogen{,-xhigh,-high,-medium,-low}` combos under their active OmniRoute provider blocks, preserve `x-omniroute-no-memory: "true"` headers, and maintain byte-for-byte parity on `scripts/setup-macbook-omniroute-client.sh` (`--check` exit `0`) with `~/Developer/scripts/setup-macbook-omniroute-client.sh`.

#### Scenario: All 19 active OmniRoute combos registered across workstation CLIs and editors
- **WHEN** `omp`, `pi`, `prime-agent`, `hermes`, `opencode`, `kilo`, `codex`, `kimi`, `grok`, `goose`, `droid`, `claude`, `muse`, `qwen`, `zed`, `cline`, `continue`, `~/.shb/.env`, and `scripts/setup-macbook-omniroute-client.sh` are inspected
- **THEN** each surface SHALL declare all 5 `gemini-4-hydrogen*` combos alongside `gemini-3.8-flash-high`, default primary interactive slots to `gemini-4-hydrogen` (or `muse-spark-1.3` -> `gemini-4-hydrogen-high` on Muse; `omniroute/gemini-4-carbon` on OMP `default` with auxiliary roles on `gemini-4-hydrogen*`), and retain `gemini-3.8-flash-high` as fallback
- **AND** `~/.shb/.env` SHALL set `SHB_DEFAULT_MODEL=gemini-4-hydrogen` and `SHB_FALLBACK_MODEL=gemini-3.8-flash-high`
- **AND** `scripts/setup-macbook-omniroute-client.sh` and `~/Developer/scripts/setup-macbook-omniroute-client.sh` SHALL have identical SHA-256 digests and exit `0` under `--check` (validating all 19 `required_combos` against `/v1/models`)

## ADDED Requirements

### Requirement: Codex Catalog Tier Clamping and Fleet Fallback Selector Retention
Codex CLI (`~/.codex/{config.toml,omniroute.config.toml,cockpit-model-catalog.json}`) SHALL default to `gemini-4-hydrogen` at `"high"` reasoning effort, clamp tiered Hydrogen slugs to their matching effort level, and retain `gemini-3.8-flash-high` in its catalog.

#### Scenario: Selecting a tiered Codex Hydrogen slug respects its tier instead of global xhigh override
- **WHEN** `~/.codex/cockpit-model-catalog.json` (`mode 0644`, `ensure_ascii=False`), `~/.codex/omniroute.config.toml` (`mode 0600`), and `~/.codex/config.toml` (`mode 0600`) are inspected
- **THEN** `~/.codex/config.toml` and `~/.codex/omniroute.config.toml` SHALL both set `model = "gemini-4-hydrogen"` and `model_reasoning_effort = "high"`
- **AND** `cockpit-model-catalog.json` SHALL set `default_reasoning_level: "high"` on `gemini-4-hydrogen` and object-array `supported_reasoning_levels` entries (`[{"effort": "xhigh", "description": "Extra high"}]` on `gemini-4-hydrogen-xhigh`, `[{"effort": "high", "description": "High"}]` on `gemini-4-hydrogen-high`, `[{"effort": "medium", "description": "Medium"}]` on `gemini-4-hydrogen-medium`, and `[{"effort": "low", "description": "Low"}]` on `gemini-4-hydrogen-low`, each matching `default_reasoning_level`)
- **AND** `"gemini-3.8-flash-high"` SHALL remain present in `cockpit-model-catalog.json` (`models[]`) as fallback

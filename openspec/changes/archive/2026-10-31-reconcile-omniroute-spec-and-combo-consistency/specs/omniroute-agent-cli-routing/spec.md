# Spec Delta: omniroute-agent-cli-routing

## MODIFIED Requirements

### Requirement: OmniRoute registrations SHALL use the live `sh/*` namespace with credential indirection
Every OmniRoute model registration added or corrected by this change SHALL use `pm/Claude-Fable` (Anthropic Messages) or `sh/gpt-5.6-sol` (OpenAI Responses), verified in a fresh `GET http://localhost:20128/v1/models` response at apply time. Retired `dlg/*` routes SHALL NOT be added or retained. Credentials SHALL use `OMNIROUTE_API_KEY` indirection; literal credentials are prohibited except for the documented Kimi Code shell-variable limitation.

#### Scenario: Requested namespace IDs are validated against the live catalog

- **WHEN** an OmniRoute model entry is added or corrected
- **THEN** `pm/Claude-Fable` or `sh/gpt-5.6-sol` SHALL exist in the fresh live model response
- **AND** the entry SHALL preserve the exact namespace and punctuation
- **AND** no new `dlg/*` entry SHALL be written

#### Scenario: Credentials remain external

- **WHEN** a changed CLI supports environment-backed provider credentials
- **THEN** the configuration SHALL reference `OMNIROUTE_API_KEY` or an approved helper
- **AND** no literal credential value SHALL appear in the configuration, OpenSpec artifacts, logs, process arguments, or evidence
- **AND** the Kimi Code limitation SHALL be recorded if its mode-600 provider field must retain an existing literal value

#### Scenario: Model IDs validated against the live registry

- **WHEN** a `sh/*` model ID is written into a CLI configuration
- **THEN** that ID SHALL exist in a fresh `GET http://localhost:20128/v1/models` response captured during apply
- **AND** retired `dlg/*` inference routes SHALL NOT be added to any active configuration

#### Scenario: No literal credentials where env indirection exists

- **WHEN** a configuration file changed by this change supports environment indirection
- **THEN** it SHALL contain no literal API key value
- **AND** the OmniRoute credential SHALL be referenced only through `OMNIROUTE_API_KEY` or the CLI's documented environment indirection

### Requirement: Known OmniRoute SSE heartbeat defect SHALL be documented as a routing blocker
The goose runtime blocker SHALL be documented as a two-part strict-decoder incompatibility: (1) OmniRoute emits a build-inlined 15s `response.in_progress` SSE heartbeat on `/v1/responses` lacking `response` and `sequence_number` (ignoring `SSE_HEARTBEAT_INTERVAL_MS`), and (2) goose's decoder rejects upstream `response.created` events lacking `model`. Affected CLIs SHALL be documented as blocked while keeping catalog entries valid, without hotfixing vendor build artifacts.

#### Scenario: strict-decoder CLI registered but runtime-blocked

- **WHEN** a CLI with a strict Responses-API decoder (such as goose) is registered against OmniRoute
- **THEN** its catalog registration SHALL remain in place
- **AND** the evidence manifest SHALL record both blocker parts with their exact decoder errors
- **AND** the blocker SHALL be attributed to the goose decoder strictness combined with OmniRoute and upstream event shapes, not to the CLI registration

#### Scenario: heartbeat env var verified ineffective before workaround attempts

- **WHEN** a workaround for the malformed heartbeat is considered
- **THEN** `SSE_HEARTBEAT_INTERVAL_MS` SHALL first be tested at 0 and at a large value with per-event timestamp evidence
- **AND** if the build-inlined 15s interval is confirmed, env-var-based mitigation SHALL be recorded as ineffective

#### Scenario: vendor bundle hotfix is prohibited

- **WHEN** the malformed heartbeat frame is located in the built Next.js bundle chunks
- **THEN** in-container replacement of bundle files SHALL NOT be used as a durable fix
- **AND** any experimental bundle patch SHALL be reverted, with the container restored to its original state
- **AND** the resolution SHALL be pursued through upstream OmniRoute or goose fixes instead

#### Scenario: clean streaming path documented

- **WHEN** the `/v1/chat/completions` streaming path is tested with a slow prompt
- **THEN** it SHALL be recorded as emitting zero malformed heartbeat events
- **AND** CLIs able to use the chat-completions dialect SHALL be documented as unaffected by the heartbeat defect

#### Scenario: chat-completions route selected empirically

- **WHEN** a chat-completions route is selected to bypass the heartbeat defect for a strict-decoder CLI
- **THEN** the exact endpoint SHALL be selected from live per-model evidence rather than assumed, distinguishing SSE cleanliness from model availability: the versioned `/v1/chat/completions` path is SSE-clean but returned HTTP 502 for `sh/gpt-5.6-sol`, while the versionless `/chat/completions` path returned HTTP 200 with the expected sentinel
- **AND** the selected route SHALL pass the baseline-relative no-regression gate before any live configuration change

### Requirement: Chat Completions SHALL be an exception-only fallback
A CLI SHALL use the Chat Completions dialect for an OmniRoute model only when its native Messages or Responses implementation is unavailable or fails a compatibility gate. The fallback SHALL be selected from live endpoint evidence, preserve the exact requested model ID, and use the versionless `http://localhost:20128/chat/completions` target; the failing `http://localhost:20128/v1/chat/completions` route SHALL NOT be substituted for `sh/gpt-5.6-sol`.

#### Scenario: Native client incompatibility selects the proven fallback

- **WHEN** a bounded product-specific probe demonstrates that the installed client cannot decode the required native stream
- **THEN** the configuration MAY select a documented Chat Completions provider
- **AND** the provider SHALL target the empirically proven versionless route
- **AND** the evidence SHALL name the native decoder failure and the fallback route separately

#### Scenario: Native route passes

- **WHEN** the product-specific native probe returns the exact sentinel, supported thinking output, and required tool lifecycle
- **THEN** the native provider SHALL remain selected
- **AND** the change SHALL NOT downgrade it to Chat Completions merely for uniformity

### Requirement: Thinking configuration SHALL match the requested model and provider dialect
Each changed CLI SHALL declare reasoning/thinking only through fields supported by its native provider implementation: `pm/Claude-Fable` SHALL use Anthropic thinking controls or effort mapping, and `sh/gpt-5.6-sol` SHALL use OpenAI Responses `reasoning.effort` (`none`, `low`, `medium`, `high`, or `xhigh`). A client SHALL NOT send OpenAI `reasoning.effort` on Anthropic Messages or Anthropic `thinking` on Responses unless its adapter explicitly translates that field.

#### Scenario: PM thinking is separated from answer text

- **WHEN** a native Anthropic Messages client invokes `pm/Claude-Fable` with thinking enabled
- **THEN** the provider request SHALL use the client's Anthropic thinking control
- **AND** the response SHALL be parsed with thinking and answer content as separate semantic blocks where the client exposes them
- **AND** a successful final answer alone SHALL NOT be recorded as proof that thinking was enabled

#### Scenario: SH reasoning effort is accepted

- **WHEN** a native Responses client invokes `sh/gpt-5.6-sol` with `high` or `xhigh` effort
- **THEN** the request SHALL use the client's Responses reasoning control
- **AND** the response SHALL preserve reasoning/message separation or report the client's documented normalization
- **AND** an unsupported effort value SHALL be rejected or downgraded only according to the CLI's documented behavior

### Requirement: Live verification through credential-carrying configs SHALL be rotation-gated
When a configuration file carries literal credentials exposed in any session transcript, no live route verification SHALL run through that file until the owner confirms upstream rotation or authorizes proceeding without rotation. The gate, release condition, and decision SHALL be recorded in the active change; verification evidence SHALL remain at config level until release and SHALL NOT be reported as fully verified while blocked.

#### Scenario: rotation gate blocks live sentinel

- **WHEN** a routing change's closure requires a live sentinel through a config carrying exposed literal credentials
- **THEN** the sentinel SHALL be blocked pending the recorded release decision
- **AND** config-level route-contract evidence SHALL be recorded instead
- **AND** the surface SHALL NOT be reported as fully verified while blocked

#### Scenario: release decision is recorded, not assumed

- **WHEN** the rotation gate is to be released
- **THEN** the active change SHALL record an explicit user confirmation (rotation done upstream) or written authorization to proceed without rotation, with a timestamp
- **AND** the released live verification SHALL be executed and recorded before the surface is reported as fully verified

### Requirement: Gemini combo SHALL be configured as default across supported coding agents
Supported coding-agent CLIs and editors (`pi`, `omp`, `codex`, `opencode`, `grok`, `droid`, `prime-agent`, `goose`, `kimi-code`, `zed`, `continue`, and Claude Code OmniRoute profile) SHALL configure `gemini-3.8-flash-high` as their default model via OmniRoute (`/v1/responses` where supported, or OpenAI/Anthropic ingress for dialect-specific clients) while preserving existing providers and Hermes Agent's MoA `omniroute:gemini-3.8-flash-high` aggregator.

#### Scenario: Supported CLIs default to Gemini combo
- **WHEN** coding agents are invoked with default model selection
- **THEN** requests SHALL route through OmniRoute's `gemini-3.8-flash-high` combo
- **AND** clients supporting the Responses API SHALL use `/v1/responses`
- **AND** all existing alternative providers SHALL remain preserved
- **AND** credentials SHALL resolve via environment indirection (`OMNIROUTE_API_KEY`) with zero literal secrets committed

#### Scenario: All supported coding agents default to OmniRoute Gemini 3.8 Flash High
- **WHEN** any supported coding agent CLI (`pi`, `omp`, `codex`, `opencode`, `grok`, `droid`, `prime-agent`, `goose`, `kimi-code`), editor (`zed`), or tool (`continue`) is launched without an explicit model override
- **THEN** it SHALL resolve `gemini-3.8-flash-high` via OmniRoute as its default model
- **AND** pre-existing secondary providers and fallback chains SHALL remain preserved and accessible

#### Scenario: Hermes Agent default MoA is preserved
- **WHEN** Hermes Agent configuration is inspected or loaded
- **THEN** `model.provider` SHALL remain `moa`
- **AND** `model.default` SHALL remain `default`
- **AND** the primary aggregator model SHALL route to `omniroute:gemini-3.8-flash-high`

#### Scenario: Kimi Code CLI defaults to OmniRoute Gemini 3.8 Flash High
- **WHEN** Kimi Code CLI (`kimi`) is launched without an explicit model override
- **THEN** it SHALL resolve `default_model = "gemini-3.8-flash-high"` in `~/.kimi-code/config.toml`
- **AND** model `gemini-3.8-flash-high` SHALL route through provider `omniroute-anthropic` targeting `http://localhost:20128`
- **AND** the model definition SHALL declare `max_context_size = 1000000`, `capabilities = ["thinking", "tool_use"]`, and `default_effort = "high"`
- **AND** the configuration file SHALL maintain permission mode `0600`

### Requirement: OmniRoute Gemini 4 Argon Tier Combos SHALL Route Exclusively Through Entitled Ultra Antigravity CLI Connections
OmniRoute SHALL expose four top-level Gemini 4 Argon combos (`gemini-4-argon-high`, `gemini-4-argon-medium`, `gemini-4-argon-low`, and `gemini-4-argon`) using `strategy: "auto"`, `context_length: 1000000`, `context_cache_protection: false`, `config.targetTimeoutMs: 180000`, `config.predictiveTtftMs: 60000`, and `config.candidatePool: ["agy"]`, each containing three model steps pinned to the three Google AI `Ultra` `agy` connections (`62af823b`, `0532bad4`, `338764b8`).

#### Scenario: Tier combos resolve exclusively to the two Ultra agy CLI connections
- **WHEN** `GET http://127.0.0.1:20128/api/combos` is queried
- **THEN** combos `gemini-4-argon-high`, `gemini-4-argon-medium`, `gemini-4-argon-low`, and `gemini-4-argon` SHALL each be present with `strategy: "auto"`, `context_length: 1000000`, `context_cache_protection: false`, `config.targetTimeoutMs: 180000`, `config.candidatePool: ["agy"]`, `config.resetAwareQuotaCacheTtlMs: 300000`, `config.resetWindowQuotaCacheTtlMs: 300000`, and `config.resetAwareQuotaCacheMaxStaleMs: 3600000`
- **AND** `gemini-4-argon-high` and `gemini-4-argon` SHALL each define three `kind: "model"` steps with `model: "agy/gemini-4-argon-high"`, `providerId: "agy"`, and matching email `label` pinned to `connectionId: "62af823b-f3d7-4e6b-87a9-98069167d4f6"` (`vicgnome19094@gmail.com`), `connectionId: "0532bad4-2486-4286-8f06-510e9c678620"` (`vinhvumobile@gmail.com`), and `connectionId: "338764b8-1cd7-4946-b789-ee5dad4c5073"` (`vinhghtk1908@gmail.com`)
- **AND** `gemini-4-argon-medium` SHALL define three `kind: "model"` steps with `model: "agy/gemini-4-argon-medium"`, `providerId: "agy"`, and matching email `label` pinned to those same three `connectionId` values
- **AND** `gemini-4-argon-low` SHALL define three `kind: "model"` steps with `model: "agy/gemini-4-argon-low"`, `providerId: "agy"`, and matching email `label` pinned to those same three `connectionId` values

#### Scenario: Combo health check and dual-protocol inference succeed across all Argon combos
- **WHEN** `POST /api/combos/test`, `POST /v1/responses`, or `POST /v1/chat/completions` is invoked for `gemini-4-argon-high`, `gemini-4-argon-medium`, `gemini-4-argon-low`, or `gemini-4-argon`
- **THEN** OmniRoute SHALL dispatch to one of the three `Ultra` `agy` connections and return a valid `200 OK` completion

#### Scenario: Disabled sentinel or unentitled Pro connection fails closed without polluting Argon combos
- **WHEN** any of the 12 non-Ultra `agy` CLI connections is inspected or invoked for `gemini-4-argon*`
- **THEN** none of those 12 `connectionId` values SHALL appear in the `models[]` steps of `gemini-4-argon`, `gemini-4-argon-high`, `gemini-4-argon-medium`, or `gemini-4-argon-low`

### Requirement: Muse Code entrypoint compatibility SHALL use URL-prefix rewriting without chunk mutation or static catalog bypass
OmniRoute container startup (`/Users/androidteam/Omniroute/scripts/container-entrypoint-compat.sh`) SHALL inject `MUSE_CODE_REWRITE_V3` into `/app/peer-stamp.mjs` to rewrite `/muse-code` and `/api/provider` prefixes to `/v1/muse-code` and `/v1/api/provider` without Muse-specific chunk rewrites, while applying the 43 non-Muse runtime compatibility rules across 16 server chunk files.

#### Scenario: Entrypoint rewrites /muse-code paths without modifying Next.js server chunks
- **WHEN** `container-entrypoint-compat.sh` or `ensure-muse-wire-compat.sh` runs inside the `omniroute` container (`v3.8.52+`)
- **THEN** `/app/peer-stamp.mjs` SHALL strip any prior V1 or `MUSE_CODE_COMPAT_V2` block and contain the `MUSE_CODE_REWRITE_V3` URL prefix rewrite (`req.url = "/v1" + req.url` for `/muse-code`, `/muse-code/*`, and `/muse-code?*`) without injecting a static model catalog
- **AND** `/app/.build/next/server/chunks/*.js` SHALL contain zero Muse-specific rewrites while enforcing the 46 required fail-closed server chunk markers
- **AND** authenticated `GET /muse-code/models` and `GET /v1/muse-code/models` SHALL return HTTP `200` from upstream's native route advertising `muse-spark-1.3`, while anonymous `GET` returns HTTP `401` when catalog authentication is enabled

#### Scenario: Muse Code binary resolves via canonical Homebrew cask symlink
- **WHEN** `/opt/homebrew/bin/muse` is inspected by workstation toolchain inventory (`inventory-workstation-toolchain.py`)
- **THEN** `/opt/homebrew/bin/muse` SHALL be a symbolic link to the installed Caskroom binary (`/opt/homebrew/Caskroom/muse-code/<version>/muse-binary`) with `is_symlinked_from_brew_bin == True`
- **AND** the macOS Keychain entry `ai.meta.dev.credentials` SHALL be seeded via `muse auth set --provider meta --api-key-stdin` with `~/.config/muse/auth.json` (`mode 0600`) on `schema_version: 2` (`"storage": "keychain"`) so `muse` executes non-interactively without requiring a `TBH_CREDENTIAL_BACKEND=file` override

### Requirement: Encapsulated Nested Combo on `muse-spark-1.3`, Auto-Scored Opus Pool on `claude-opus-5.5`, and Loopback API Bridge Port `20129`
OmniRoute SHALL configure `muse-spark-1.3` (`strategy: "priority"`, `nestedComboMode: "execute"`, `targetTimeoutMs: 25000`) and `claude-opus-5.5` (`strategy: "auto"`, `nestedComboMode: "flatten"`, `targetTimeoutMs: 180000`, `predictiveTtftMs: 60000`) with `context_cache_protection: false`, pin `gemini-4-argon*` to the three `Ultra` `agy` accounts, and set `API_HOST=0.0.0.0` in `.env` for loopback port `20129`.

#### Scenario: `muse-spark-1.3` executes `gemini-3.8-flash-high` sub-combo without model-pin warning
- **WHEN** a request targets `muse-spark-1.3`
- **THEN** OmniRoute SHALL match `muse-spark-1.3` (`context_cache_protection: false`, `nestedComboMode: "execute"`, `targetTimeoutMs: 25000`) and execute `gemini-3.8-flash-high` using its 16-factor `auto` strategy without logging false `provider durably unhealthy — dropping pin` warnings

#### Scenario: `claude-opus-5.5` load-balances and pins across all 8 Opus accounts via `auto` strategy
- **WHEN** a request targets `claude-opus-5.5`
- **THEN** OmniRoute SHALL score all 15 active `agy` Opus accounts (`12` Pro and `3` Ultra, excluding banned `47f334b1-b801-41f6-a709-4ebabb7a86d6`) using 16-factor `auto` routing (`tierPriority`, `health`, `quota`) and pin multi-turn sessions via `applySessionStickiness` without flattening `gemini-3.8-flash-high` into the `auto` candidate pool

#### Scenario: Host loopback port `20129` reaches container API bridge
- **WHEN** a request is sent to `http://127.0.0.1:20129/v1/models` or `http://127.0.0.1:20129/v1/responses`
- **THEN** `apiBridgeServer.ts` (`API_HOST=0.0.0.0` inside the container, mapped to `127.0.0.1:20129:20129` on the host) SHALL accept the connection and serve the response

### Requirement: 15-Account Antigravity Auto Pools for `claude-opus-5.5` and `claude-sonnet-5.5` Without Unentitled Custom 5.5 Model IDs
OmniRoute SHALL configure `claude-opus-5.5` (`15` active `agy/claude-opus-4-6-thinking` steps with `0` `combo-ref` steps, `targetTimeoutMs: 180000`, `predictiveTtftMs: 60000`) and `claude-sonnet-5.5` (`15` active `agy/claude-sonnet-4-6` steps, `targetTimeoutMs: 120000`, `predictiveTtftMs: 45000`) with `strategy: "auto"` and `context_cache_protection: false` (excluding banned `47f334b1`), and SHALL remove unentitled custom `claude-*-5-5-high` models.

#### Scenario: `claude-opus-5.5` and `claude-sonnet-5.5` route across 15 `agy` accounts with tier-matched timeouts
- **WHEN** `GET /api/combos` is queried for `claude-opus-5.5` (`4b2430da-0b3b-4b0e-9773-ec0f97adc252`) and `claude-sonnet-5.5` (`9447399c-856b-4f52-8820-b3bf3dc3f132`)
- **THEN** `claude-opus-5.5` SHALL contain 15 `kind: "model"` steps targeting `agy/claude-opus-4-6-thinking` across the 15 active `agy` accounts (`12` Pro and `3` Ultra, excluding banned `47f334b1-b801-41f6-a709-4ebabb7a86d6`) with `strategy: "auto"`, `context_cache_protection: false`, `config.targetTimeoutMs: 180000`, and `config.predictiveTtftMs: 60000`
- **AND** `claude-sonnet-5.5` SHALL contain 15 `kind: "model"` steps targeting `agy/claude-sonnet-4-6` with `strategy: "auto"`, `context_cache_protection: false`, `config.targetTimeoutMs: 120000`, and `config.predictiveTtftMs: 45000`

#### Scenario: Unentitled `claude-*-5-5-high` custom models and unstable auto-pool providers are excluded without breaking dedicated combos
- **WHEN** `GET /api/provider-models`, `GET /api/models/alias`, `GET /api/providers`, and `GET /api/combos` are queried
- **THEN** `/api/provider-models` SHALL NOT contain custom `claude-opus-5-5-high` or `claude-sonnet-5-5-high` overrides under `agy` or `antigravity`, and `/api/models/alias` SHALL NOT contain `test-opus-55-high`
- **AND** expired connection `6fb701a5-d060-422c-bc34-0cca543d0eda` (`ollama-cloud`) SHALL have `isActive: false`, while `auto/*` combos SHALL restrict `config.candidatePool` to `["agy", "codex", "github"]` so dedicated combos (`phanmemvip` and `muse-spark-1.3`) remain intact

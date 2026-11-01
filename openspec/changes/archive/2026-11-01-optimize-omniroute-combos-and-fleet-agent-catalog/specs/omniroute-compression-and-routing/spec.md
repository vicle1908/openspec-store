# omniroute-compression-and-routing Spec Delta

## MODIFIED Requirements

### Requirement: RTK Tool Result Compression, Adaptive Context Budget, and Delegated Context Editing

The OmniRoute gateway SHALL configure RTK compression at `minimal` intensity for tool result payloads while preserving system prompts and code blocks, SHALL preserve OpenAI Responses `function_call` tool metadata and set `_rtkSkip = true` for all non-shell tools so only shell execution tools run RTK log filters, SHALL configure `contextBudget.mode` as `"replace-autotrigger"` (`pct: 0.85`), and SHALL enable delegated `contextEditing` for supported Claude relays.

#### Scenario: Verbose tool output compressed before upstream dispatch
- **WHEN** a coding client submits a request carrying `x-omniroute-compression: allow-lossy` or `engine:rtk` (or tests via `POST /api/context/rtk/test` with an explicit `command`) containing a tool result matching one of the 55 built-in RTK filters
- **THEN** OmniRoute SHALL compress the tool result payload within `maxLinesPerResult` (120) and `maxCharsPerResult` (12000) bounds while preserving system prompts (`preserveSystemPrompt: true`) and code blocks (`applyToCodeBlocks: false`) verbatim

#### Scenario: Headerless requests honor safe default pipeline and adaptive context budget escalation
- **WHEN** a client submits a request without an `x-omniroute-compression` header
- **THEN** OmniRoute SHALL run its server-side tool-safe `[session-dedup, lite, rtk, codex-responses, headroom]` stack (`compressionComboId: "default-caveman"`, `caveman: false`, `lite.compressToolResults: false`) when below the 85% `contextBudget` threshold, and `resolveAdaptivePlan` SHALL escalate along the compression ladder when estimated input tokens exceed the `contextBudget` target

#### Scenario: OpenAI Responses non-shell tool outputs bypass RTK content filters
- **WHEN** an OpenAI Responses client (`api: "openai-responses"`) submits `body.input` containing a `type: "function_call"` item (`name: "read"`, `"glob"`, `"grep"`, `"write"`, `"edit"`, `"eval"`, `"task"`, `"todo"`, `"find"`, `"ask"`, `"lsp"`, `"ast_grep"`, `"ast_edit"`, or any non-shell tool) paired by `call_id` with a `type: "function_call_output"` item
- **THEN** `adaptBodyForCompression()` SHALL attach `tool_call_id`, skip the `b.find(...)` and `JSON.parse(...)` command extraction when `_sh` is `false` (`_fc=_sh&&k?b.find(...):null`), and set `_rtkSkip: true` whenever the paired `function_call` `name` does not match `/\b(bash|shell|terminal|run_command|execute_command|exec|command)\b/i` (or is listed in `codexResponsesConfig.preserveToolNames`)
- **AND** `rtk` SHALL honor `_rtkSkip === true` (`skipFilters: true`) even after `adaptBodyForCompression()` deletes `body.input`, preserving structured and file-read outputs verbatim without line stripping

#### Scenario: Delegated context editing on long Claude tool loops
- **WHEN** `contextEditing.enabled` is `true` and a request targets a supported Claude or `anthropic-compatible-cc-*` relay exceeding the 100,000 input token trigger
- **THEN** OmniRoute SHALL inject the `clear_tool_uses_20250919` context management edit keeping the 3 most recent tool uses, and automatically strip and retry once if upstream returns HTTP 400

### Requirement: Multi-Account Claude Opus and Sonnet Combo Pooling across Antigravity Accounts
OmniRoute SHALL configure `claude-opus-5.5` and `claude-sonnet-5.5` combos to pool all 14 active Antigravity connections (`11` Pro and `3` Ultra, excluding banned `47f334b1` and `d5c3465f`) across 14 `kind: "model"` steps matching each account's `syncedAvailableModels` catalog with `0` `combo-ref` steps, `context_length: 1000000`, `strategy: "auto"`, and `context_cache_protection: false`.

#### Scenario: Claude Opus 5.5 combo pools all 15 Antigravity accounts
- **WHEN** `GET /api/combos/{id}` is queried for `claude-opus-5.5` (`4b2430da-0b3b-4b0e-9773-ec0f97adc252`)
- **THEN** OmniRoute SHALL return a combo with 14 explicit `kind: "model"` steps matching each active connection's `syncedAvailableModels` entry (`agy/claude-opus-5-5-high` on migrated connection `38782750-7a60-46d4-ae3f-e8c13cda296b` and `agy/claude-opus-4-6-thinking` on the remaining 13 active `agy` connections) (`11` Pro and `3` Ultra, excluding banned `47f334b1-b801-41f6-a709-4ebabb7a86d6` and `d5c3465f-9797-4b4b-a937-c3e653e168fb`, with `0` `combo-ref` steps), `context_length: 1000000`, `strategy: "auto"`, `candidatePool: ["agy"]`, `context_cache_protection: false`, `config.targetTimeoutMs: 180000`, and `config.predictiveTtftMs: 60000`

#### Scenario: Claude Sonnet 5.5 combo pools all 15 Antigravity accounts
- **WHEN** `GET /api/combos/{id}` is queried for `claude-sonnet-5.5` (`9447399c-856b-4f52-8820-b3bf3dc3f132`)
- **THEN** OmniRoute SHALL return a combo with 14 explicit `kind: "model"` steps matching each active connection's `syncedAvailableModels` entry (`agy/claude-sonnet-5-5-high` on migrated connection `38782750-7a60-46d4-ae3f-e8c13cda296b` and `agy/claude-sonnet-4-6` on the remaining 13 active `agy` connections) (`11` Pro and `3` Ultra, excluding banned `47f334b1-b801-41f6-a709-4ebabb7a86d6` and `d5c3465f-9797-4b4b-a937-c3e653e168fb`), `context_length: 1000000`, `strategy: "auto"`, `candidatePool: ["agy"]`, `context_cache_protection: false`, `config.targetTimeoutMs: 120000`, and `config.predictiveTtftMs: 45000`

#### Scenario: Live chat completions route through multi-account Claude combos to authentic Claude models
- **WHEN** `POST /v1/chat/completions` is called with `model: "claude-opus-5.5"` or `model: "claude-sonnet-5.5"`
- **THEN** OmniRoute SHALL return HTTP 200 with a completion served by `claude-opus-5-5-high`/`claude-opus-4-6-thinking` or `claude-sonnet-5-5-high`/`claude-sonnet-4-6` on one of the 14 active Antigravity accounts with zero synthetic deprecation responses or banned-account 403 dispatches

#### Scenario: Upstream Claude 5.5 model cutover contract
- **WHEN** upstream Google Antigravity provisions and advertises `claude-opus-5-5-*` or `claude-sonnet-5-5-*` in its live discovery catalog
- **THEN** OmniRoute SHALL update the explicit model steps in `claude-opus-5.5` and `claude-sonnet-5.5` combos from 4.6 to the corresponding 5.5 identifiers while preserving all 14 active connection mappings

### Requirement: Dedicated 11-Pro-Account Auto Pool for `gemini-3.8-flash-high` and Ultra Quota Isolation
OmniRoute SHALL configure `gemini-3.8-flash-high` (`7555d851-b4f3-44c6-b1fb-c6fdceabf388`) with `strategy: "auto"`, `context_cache_protection: false` persisted in `combos.data`, `targetTimeoutMs: 25000`, `predictiveTtftMs: 25000`, and 11 `kind: "model"` steps scoped exclusively to the 11 active `g1-pro-tier` `agy` connections (excluding the 3 Ultra accounts and banned `47f334b1` and `d5c3465f`), and SHALL enable `rateLimitProtection: true` on all 14 active `agy` accounts.

#### Scenario: `gemini-3.8-flash-high` routes across the 11 Pro accounts without consuming Ultra Gemini quota
- **WHEN** `GET /api/combos/7555d851-b4f3-44c6-b1fb-c6fdceabf388` (`gemini-3.8-flash-high`) is inspected or invoked
- **THEN** `strategy` SHALL be `"auto"`, `context_cache_protection` SHALL be `false`, and `models` SHALL contain 11 `agy/gemini-3.8-flash-high` steps mapped to all 11 active `g1-pro-tier` connections (including `ce95e1cb-27a4-433f-9c50-bdb6ad0b6b6b` and excluding banned `47f334b1` and `d5c3465f`) with non-empty email `label`s
- **AND** none of the 3 `g1-ultra-tier` `connectionId`s (`62af823b-f3d7-4e6b-87a9-98069167d4f6`, `0532bad4-2486-4286-8f06-510e9c678620`, `338764b8-1cd7-4946-b789-ee5dad4c5073`) SHALL appear in `gemini-3.8-flash-high`

#### Scenario: All 3 Ultra accounts and 11 Pro accounts enforce `rateLimitProtection: true`
- **WHEN** `GET /api/rate-limits` is queried
- **THEN** all 3 `g1-ultra-tier` `agy` accounts (`62af823b`, `0532bad4`, `338764b8`) and all 11 active `g1-pro-tier` `agy` accounts SHALL report `rateLimitProtection: true` and `enabled: true`

### Requirement: Tier-Matched Combo Timeouts, Cold-Start Semantic Cache Bridge, and Fail-Closed Entrypoint Guard
OmniRoute SHALL configure tier-matched timeouts (`180000`/`60000` on `gemini-4-argon*` and `claude-opus-5.5`; `120000`/`45000` with `maxRetries: 1` on `claude-sonnet-5.5`, `kimi-k3.1-pro`, and `deepseek-v4.1-flash`), configure priority failover and dual quota-cache keys on `kimi-k3.1-pro` and `deepseek-v4.1-flash`, auto-invoke `ensureSemanticCacheDbBridge()` on cold starts, and assert all runtime patch markers fail-closed.

#### Scenario: Deep-reasoning and high-TTFT combos enforce tier-matched timeouts without premature 25s aborts
- **WHEN** `GET /api/combos` is queried
- **THEN** `gemini-4-argon`, `gemini-4-argon-high`, `gemini-4-argon-medium`, `gemini-4-argon-low`, and `claude-opus-5.5` SHALL each have `config.targetTimeoutMs === 180000` and `config.predictiveTtftMs === 60000`
- **AND** `claude-sonnet-5.5`, `kimi-k3.1-pro`, and `deepseek-v4.1-flash` SHALL each have `config.targetTimeoutMs === 120000`, `config.predictiveTtftMs === 45000`, and `config.maxRetries === 1`
- **AND** `kimi-k3.1-pro` and `deepseek-v4.1-flash` SHALL configure `strategy: "priority"`, `config.nestedComboMode: "execute"`, `resetAwareQuotaCacheTtlMs: 300000`, `resetWindowQuotaCacheTtlMs: 300000`, and failover steps to `nx/deepseek-v4-pro` and `combo-ref: gemini-3.8-flash-high`, while `/api/model-capability-overrides` SHALL persist `max_output_tokens` overrides (`65536` on `antigravity/gemini-4-argon-{high,medium,low}`, `128000` on `antigravity/claude-*` and `antigravity/gemini-3.8-flash-*`) so `65536`-configured clients never fail with `65535` `capability_mismatch`

#### Scenario: Entrypoint verification fails closed across all runtime markers and semantic cache bridge initializes on cold start
- **WHEN** `container-entrypoint-compat.sh` runs on container startup
- **THEN** it SHALL verify all patch markers across the compiled server chunks without skipping missing chunk filenames (`process.exit(1)` on any missing marker)
- **AND** `OMNIROUTE_SEMANTIC_CACHE_EMBEDDING_TIMEOUT_MS=3000` and `OMNIROUTE_SEMANTIC_CACHE_TTL_MS=18000000` SHALL be set in `/Users/androidteam/Omniroute/.env` with `ensureSemanticCacheDbBridge()` auto-invoked on `/v1/responses` and `/v1/messages` cold starts

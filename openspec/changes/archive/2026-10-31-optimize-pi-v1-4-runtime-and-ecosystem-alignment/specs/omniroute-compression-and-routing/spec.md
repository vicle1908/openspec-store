# omniroute-compression-and-routing Specification Delta

## MODIFIED Requirements

### Requirement: RTK Tool Result Compression, Adaptive Context Budget, and Delegated Context Editing

The OmniRoute gateway SHALL configure RTK compression at `minimal` intensity for tool result payloads while preserving system prompts and code blocks, SHALL preserve OpenAI Responses `function_call` tool metadata so non-shell tools (`read`, `glob`, `grep`, `write`, `edit`) bypass RTK shell filters, SHALL configure `contextBudget.mode` as `"replace-autotrigger"` (`pct: 0.85`), and SHALL enable delegated `contextEditing` for supported Claude relays.

#### Scenario: Verbose tool output compressed before upstream dispatch
- **WHEN** a coding client submits a request carrying `x-omniroute-compression: allow-lossy` or `engine:rtk` (or tests via `POST /api/context/rtk/test` with an explicit `command`) containing a tool result matching one of the 55 built-in RTK filters
- **THEN** OmniRoute SHALL compress the tool result payload within `maxLinesPerResult` (120) and `maxCharsPerResult` (12000) bounds while preserving system prompts (`preserveSystemPrompt: true`) and code blocks (`applyToCodeBlocks: false`) verbatim

#### Scenario: Headerless requests honor safe default pipeline and adaptive context budget escalation
- **WHEN** a client submits a request without an `x-omniroute-compression` header
- **THEN** OmniRoute SHALL run its server-side tool-safe `[session-dedup, lite, rtk, codex-responses, headroom]` stack (`compressionComboId: "default-caveman"`, `caveman: false`, `lite.compressToolResults: false`) when below the 85% `contextBudget` threshold, and `resolveAdaptivePlan` SHALL escalate along the compression ladder when estimated input tokens exceed the `contextBudget` target

#### Scenario: OpenAI Responses non-shell tool outputs bypass RTK content filters
- **WHEN** an OpenAI Responses client (`api: "openai-responses"`) submits `body.input` containing a `type: "function_call"` item (`name: "read"`, `"glob"`, `"grep"`, `"write"`, or `"edit"`) paired by `call_id` with a `type: "function_call_output"` item
- **THEN** `adaptBodyForCompression()` SHALL attach `tool_call_id` and the resolved `toolName`/`command` metadata to the adapted tool message
- **AND** `resolveToolMeta()` in `rtk` SHALL return `skipFilters: true` for non-shell tools so file-read outputs (including JSON/config files containing `npm:` or `host:port` patterns) are preserved verbatim without line stripping

#### Scenario: Delegated context editing on long Claude tool loops
- **WHEN** `contextEditing.enabled` is `true` and a request targets a supported Claude or `anthropic-compatible-cc-*` relay exceeding the 100,000 input token trigger
- **THEN** OmniRoute SHALL inject the `clear_tool_uses_20250919` context management edit keeping the 3 most recent tool uses, and automatically strip and retry once if upstream returns HTTP 400

# Design: claude-code-three-provider-routing

## Architecture

```
Claude Code (Anthropic Messages client, /v1/messages + anthropic-version header)
    |
    |-- giaoduc: direct to api.giaoduc.online/v1/messages
    |             (native anthropic_messages -- no adapter)
    |
    |-- shopapikey: direct to api.phanmemvip.shop/v1/messages
    |               (configured as codex_responses; verified gateway compatibility
    |                with Anthropic Messages at /v1/messages -- no adapter)
    |
    |-- cockpit: to localhost:8787/v1/messages (adapter REQUIRED)
                adapter translates to localhost:51006/v1/responses
```

Both shopapikey and giaoduc serve Anthropic Messages natively. Only cockpit is `codex_responses` and requires a Messages-to-Responses adapter. The adapter lives in a workspace repository, not as an ad-hoc script.

## Provider Profiles

| Profile | Base URL | Configured `api_mode` | Observed wire behavior | Model | Auth Header | Adapter? |
|---|---|---|---|---|---|---|
| giaoduc | https://api.giaoduc.online | `anthropic_messages` | Native Anthropic Messages at `/v1/messages` | Advance | x-api-key + anthropic-version | No |
| shopapikey | https://api.phanmemvip.shop | `codex_responses` | Accepts Anthropic Messages at `/v1/messages` | fable-5 | x-api-key + anthropic-version | No |
| cockpit | http://localhost:51006/v1 | `codex_responses` | Serves OpenAI Responses at `/v1/responses` | gpt-5.6-luna | Authorization: Bearer | **Yes** (workspace repo) |

**shopapikey note**: Configured as `codex_responses`; verified gateway compatibility with Anthropic Messages at `/v1/messages`. Do not rewrite `api_mode` as native Anthropic unless the provider config itself is changed.

## Verified Evidence Summary

| Test | giaoduc | shopapikey | cockpit |
|---|---|---|---|
| POST /v1/messages text | **PASS** (HTTP 200, Anthropic schema) | **PASS** (HTTP 200, Anthropic schema) | N/A |
| POST /v1/messages streaming | **PASS** (SSE: message_start, content_block_*) | **PASS** (SSE: message_start, content_block_*) | N/A |
| POST /v1/messages tool_use | **PASS** (HTTP 200, tool_use block) | **PASS** (HTTP 200, tool_use block) | N/A |
| POST /v1/responses text | N/A | N/A | **PASS** (HTTP 200, Responses object: id, status: completed, output payload) |
| POST /v1/responses streaming | N/A | N/A | **PASS** (SSE: response.created, response.output_text.delta, response.completed) |
| POST /v1/responses tool_use | N/A | N/A | **PASS** (HTTP 200 transport acceptance; function-call body unverified) |
| Adapter needed | **No** | **No** | **Yes** (Claude Code is Messages-only) |

## Workspace Adapter Repository

The cockpit adapter lives at `~/Developer/claude-code-provider-adapter/` as a first-class workspace Python repository:

```
~/Developer/claude-code-provider-adapter/
  pyproject.toml          # requires-python >=3.14,<3.15
  uv.lock                 # pinned, committed, current stable deps
  README.md
  src/
    claude_code_provider_adapter/
      __init__.py
      app.py              # FastAPI app + POST /v1/messages endpoint
      config.py           # upstream URL + env-var-based credential resolution
      models.py           # Pydantic models for Anthropic Messages <-> Responses
      translation.py      # Request/response translation logic
      upstream.py         # Upstream proxy with correct AsyncClient lifecycle
  tests/
    test_translation.py
    test_routes.py
    test_streaming.py
```

**Dependency management**: `uv` resolves and locks all dependencies via `pyproject.toml` + `uv.lock`. Entry point: `uv run --directory ~/Developer/claude-code-provider-adapter claude-code-provider-adapter`.

**Launcher lifecycle**: `cockpit()` does NOT start or supervise the adapter. The adapter must be running separately before `cockpit()` is used. A separate `cockpit_adapter_start` / `cockpit_adapter_stop` pair is a future improvement.

## Adapter Design Requirements

### Translation Scope

| Direction | Field Mapping |
|---|---|
| Messages to Responses | model, messages[] to input[], system to instructions (string, not message), max_tokens to max_output_tokens, tools[].input_schema to tools[].parameters |
| Responses to Messages | output[].output_text to content[{type:"text"}], output[].function_call to content[{type:"tool_use"}], stop_reason to stop_reason, usage to usage |

### System Messages

Anthropic `system` parameter is a top-level string, NOT a message role. Translated to Responses `instructions` field. Do NOT emit a system message item.

### Tool Use

- Tool declarations: Anthropic `input_schema` to Responses `parameters`
- Tool calls: Responses `function_call` to Anthropic `tool_use` content block
- Tool results: Anthropic `tool_result` content block to Responses `function_call_output` input item
- Tool call arguments: may be split across multiple `response.function_call_arguments.delta` SSE events -- must accumulate before emitting `tool_use` block
- ID normalization: `call_` prefix (Anthropic) mapped to `fc_` prefix (Responses) and back via `responses_call_id()` / `anthropic_tool_use_id()`

### Streaming Translation

| Responses SSE Event | Messages SSE Event |
|---|---|
| response.created | message_start |
| response.output_text.delta | content_block_delta (text_delta) -- requires prior content_block_start with type: text |
| response.function_call_arguments.delta | content_block_delta (input_json_delta) -- requires prior content_block_start with type: tool_use |
| response.completed | content_block_stop + message_delta + message_stop |

**Critical**: Every content_block_delta MUST be preceded by a content_block_start with the correct block type (`text` or `tool_use`). Tool blocks require `type: tool_use` in content_block_start.

### AsyncClient Lifecycle

For streaming: the generator owns its own AsyncClient via `client.stream()` -- client stays open for the full iteration duration. For non-streaming: the endpoint creates and closes the client.

### SSE Protocol

Each event: `event: <type>\ndata: <json>\n\n` (double-newline terminator). Unknown upstream events are silently ignored.

### Error Handling
- Adapter unavailable: HTTP 502
- Upstream 4xx/5xx: pass through (do NOT log response body content)
- `thinking` field: silently stripped (not rejected) -- cockpit does not support it
- Other explicitly unsupported fields: HTTP 400
- No credentials in logs or error messages

## Security
- API keys referenced by env-var names only; never embedded in source
- Adapter does not log request/response bodies
- No credential values in OpenSpec artifacts
- Existing credentials retained; rotation intentionally out of scope

## Settings Precedence

VERIFIED. Shell environment variables override `settings.json` env block. All three launcher smoke tests passed after provider-specific keys were removed from `settings.json`. `claude --print` with `ANTHROPIC_BASE_URL` set in shell successfully routed to each provider endpoint.

## Launcher Function Contract

Each launcher function:
1. Sets ANTHROPIC_BASE_URL to the provider base URL
2. Sets ANTHROPIC_AUTH_TOKEN from the provider env var (by reference, not value)
3. Sets ANTHROPIC_MODEL to the provider model name
4. Launches `claude "$@"`

Do NOT set `ANTHROPIC_DEFAULT_*_MODEL` variables yet -- behavior with non-Anthropic models is unknown.

**URL convention**: Claude Code appends `/v1/messages` to the configured base URL. Launcher values should NOT include `/v1/messages`. Verified via actual launcher smoke tests.

**Auth mapping**: Claude Code's `ANTHROPIC_AUTH_TOKEN` produces `x-api-key` header for Messages providers and Bearer for cockpit -- confirmed via live smoke tests.

## Rollback
1. Remove shell launcher functions from ~/.zshrc
2. Restore settings.json from backup
3. Stop cockpit adapter process if running
4. `claude_reset` to restore defaults

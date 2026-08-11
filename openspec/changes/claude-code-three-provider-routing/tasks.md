# Tasks: claude-code-three-provider-routing

> **Successor note:** Tasks checked here cover the initial routing slice. Do not use them as evidence for the current `[1m]` model aliases, effort settings, or adapter effort mapping; those are tracked in `claude-code-model-effort-alias-routing`.

## Phase 0: Prerequisites

- [x] 0.2 Backup `~/.claude/settings.json` to `~/.claude/backups/settings.json.pre-provider-routing`

## Phase 1: Provider Profile Launchers

- [x] 1.1 Write `shopapikey()` shell function in `~/.zshrc`: sets `ANTHROPIC_BASE_URL=https://api.phanmemvip.shop`, `ANTHROPIC_AUTH_TOKEN` from `$HERMES_CUSTOM_SHOPAPIKEY_API_KEY`, model `fable-5`, launches `claude "$@"`
- [x] 1.2 Write `giaoduc()` shell function in `~/.zshrc`: sets `ANTHROPIC_BASE_URL=https://api.giaoduc.online`, `ANTHROPIC_AUTH_TOKEN` from `$HERMES_CUSTOM_GIAODUC_API_KEY`, model `Advance`, launches `claude "$@"`
- [x] 1.3 Write `cockpit()` shell function in `~/.zshrc`: sets `ANTHROPIC_BASE_URL=http://localhost:8787`, `ANTHROPIC_AUTH_TOKEN` from `$HERMES_CUSTOM_COCKPIT_API_KEY`, model `gpt-5.6-luna`, launches `claude "$@"`. NOTE: adapter must be running separately before use.
- [x] 1.4 Write `claude_reset()` shell function in `~/.zshrc`: unsets provider env vars, launches `claude "$@"`
- [x] 1.5 Guard: functions check for `claude` in PATH before launching
- [x] 1.6 URL convention verified: `ANTHROPIC_BASE_URL` without `/v1` suffix works with Claude Code (tested via `shopapikey --print`, `giaoduc --print`, `cockpit --print`)

## Phase 2: Settings Isolation

- [x] 2.1 Backup current `~/.claude/settings.json` to `~/.claude/backups/settings.json.pre-provider-routing`
- [x] 2.2 Remove provider-specific env vars from `settings.json` env block: `ANTHROPIC_BASE_URL`, `ANTHROPIC_AUTH_TOKEN`, `ANTHROPIC_MODEL`, `ANTHROPIC_DEFAULT_*_MODEL`, `CLAUDE_CODE_SUBAGENT_MODEL`
- [x] 2.3 Preserve all non-provider settings
- [x] 2.4 Verified: all three launcher smoke tests pass with isolated settings

## Phase 3: Workspace Adapter Repository

### 3A: Repository creation
- [x] 3A.1 Created at `~/Developer/claude-code-provider-adapter/` via `uv init`
- [x] 3A.2 `src/claude_code_provider_adapter/` package with `__init__.py`
- [x] 3A.3 Dependencies: `fastapi>=0.115.0`, `httpx>=0.28.0`, `pydantic>=2.10.0`, `uvicorn[standard]>=0.34.0`; dev: `pytest>=8.0.0`, `pytest-asyncio>=1.0.0`, `respx>=0.22.0`
- [x] 3A.4 `uv.lock` written; `uv sync` succeeds
- [x] 3A.5 `uv run python -m compileall src` passes

### 3B: Adapter implementation
- [x] 3B.1 `config.py`: upstream URL + env-var credential resolution (no hardcoded secrets)
- [x] 3B.2 `models.py`: Pydantic models for Anthropic Messages and Responses formats
- [x] 3B.3 `translation.py`: request/response translation (system→instructions, messages→input, tools, tool_use↔function_call, stop_reason, usage). Includes `responses_call_id()` and `anthropic_tool_use_id()` for `fc_`/`call_` ID normalization.
- [x] 3B.4 `upstream.py`: AsyncClient lifecycle — streaming owns its own client via `client.stream()`, non-streaming uses endpoint-level `AsyncClient`
- [x] 3B.5 `app.py`: FastAPI app with `POST /v1/messages` (strips `thinking` field) and `GET /health`
- [x] 3B.6 Entry point: `[project.scripts] claude-code-provider-adapter = "claude_code_provider_adapter.app:main"`

### 3C: Tests
- [x] 3C.1 `test_translation.py`: translate_messages_to_input, translate_tools_for_responses, translate_stop_reason, `_build_responses_body` (system→instructions), build_anthropic_response, ID normalization helpers (18 tests)
- [x] 3C.2 `test_routes.py`: non-streaming text, non-streaming tool_use, system→instructions, tool declarations, thinking stripped (not rejected), invalid JSON, missing messages, upstream 500/401 passthrough (14 tests)
- [x] 3C.3 `test_streaming.py`: SSE event ordering, tool-call streaming (fc_/call_ normalization), clean shutdown without response.completed, text→tool block switch (13 tests)
- [x] 3C.4 **45 tests passed** via `uv run pytest -q`

### 3D: Live verification
- [x] 3D.1 `GET /health` returns 200
- [x] 3D.2 Non-streaming text: model=`gpt-5.6-luna`, output=`ADAPTER_LIVE_OK`, usage=in=3270/out=9
- [x] 3D.3 Streaming: SSE events flow correctly (message_start→content_block_start→deltas→block_stop→message_delta→message_stop)
- [x] 3D.4 Tool-use: `stop_reason: tool_use`, tool_use block with correct `fc_`→`call_` normalized ID

## Phase 4: Final Acceptance

- [x] 4.1 `giaoduc --print --model Advance "GIAODUC_FINAL"` → output: `GIAODUC_FINAL`
- [x] 4.2 `shopapikey --print --model fable-5 "SHOP_FINAL"` → output: `SHOP_FINAL`
- [x] 4.3 `cockpit --print --model gpt-5.6-luna "COCKPIT_FINAL"` → output: `COCKPIT_FINAL`
- [x] 4.4 No credential values in any artifact, log, or shell history (env-var references only)

## Adapter Lifecycle (Open)

The `cockpit()` launcher does NOT start or supervise the adapter. The adapter must be running separately before use:

```sh
# Start adapter
cd ~/Developer/claude-code-provider-adapter
uv run claude-code-provider-adapter --port 8787

# Health check
curl http://127.0.0.1:8787/health
```

A separate `cockpit_adapter_start` / `cockpit_adapter_stop` pair or a health check in `cockpit()` is a future improvement.

## Security

- [x] S.2 No secrets in `~/.zshrc` functions (env-var references only)
- [x] S.3 Adapter logs do not contain request/response bodies

## Rollback

- [x] R.1 Shell functions can be removed from `~/.zshrc`
- [x] R.2 `settings.json` backup at `~/.claude/backups/settings.json.pre-provider-routing`
- [x] R.3 Adapter: `kill $(lsof -ti :8787)` to stop
- [x] R.4 `claude_reset` restores defaults

## Git History

```
2fa7fee fix: thinking field strip, fc_/call_ ID normalization, 45 tests pass
b3e11c3 feat: add Claude Code provider adapter
```

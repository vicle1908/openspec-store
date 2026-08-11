# Ground-Truth Evidence: claude-code-model-effort-alias-routing

Collected from the live workstation during implementation and verification. Credential values were never printed or stored.

## Tool and Runtime

- Claude Code: `2.1.227`
- Cockpit listener: `127.0.0.1:51006` (`cockpit-cli`)
- Adapter listener: `127.0.0.1:8787`, Docker Compose container healthy after rebuild
- Adapter baseline: 45 tests before this change
- Adapter final: 55 tests after this change
- `~/.claude/settings.json`: zero provider-specific `ANTHROPIC_*` or `CLAUDE_CODE_EFFORT*` entries

## Implementation

### Launcher contract

The actual post-mutation launcher environment probes produced:

| Launcher | Model selector | Custom/pinned value | Capabilities | Effort |
|---|---|---|---|---|
| `shopapikey()` | `fable[1m]` | `fable-5[1m]` | `effort,xhigh_effort` | `xhigh` |
| `giaoduc()` | `Advance[1m]` | `Advance[1m]` | `effort,xhigh_effort` | `xhigh` |
| `cockpit()` | `gpt-5.6-luna[1m]` | `gpt-5.6-luna[1m]` | `effort,max_effort` | `max` |

The reset probe showed all owned model, capability, effort, and auth values empty after `claude_reset()`.

### Adapter mapping

The adapter now maps:

```text
Anthropic output_config.effort -> Responses reasoning.effort
```

Supported values: `low`, `medium`, `high`, `xhigh`, `max`.
Unsupported values return HTTP 400 and are not forwarded upstream.

### Verification commands

- `zsh -n ~/.zshrc` -> PASS
- Focused RED run before implementation -> expected failures: 3 effort tests failed
- Focused GREEN run after implementation -> `6 passed`
- `uv run pytest -q` -> `55 passed in 0.69s` (including non-streaming and streaming route effort mapping/rejection coverage)
- `uv run python -m compileall -q src tests` -> PASS
- `git diff --check` -> PASS
- Docker rebuild -> image built successfully
- Docker Compose recreate -> exit 0
- Container health -> `{"status":"ok","adapter":"claude-code-provider-adapter"}` and `healthy`

## Post-Mutation Local Request Capture

The actual launcher functions were executed against a temporary local capture wrapper. Claude Code sent:

| Launcher | Wire model | Wire effort | `[1m]` on wire |
|---|---|---|---|
| `shopapikey()` | `fable-5` | `xhigh` | No |
| `giaoduc()` | `Advance` | `xhigh` | No |
| `cockpit()` | `gpt-5.6-luna` | `max` | No |

The capture confirmed Claude Code strips `[1m]` before transmission.

## Live Provider Results

### shopapikey: PASS

- Current launcher resolved `system_model=fable-5[1m]`.
- Exit status: `0` at the model-runner level; result message is successful.
- Result: `SHOP_1M_XHIGH_FINAL`.
- Model usage: `fable-5[1m]`.
- The earlier provider burst lock cleared before this final retry.

### giaoduc: PASS

- Current launcher resolved `system_model=Advance[1m]`.
- Exit status: `0`.
- Result: `GIAODUC_1M_XHIGH_REAL`.
- Model usage: `Advance[1m]`.

### cockpit direct: PASS

- Real request: `POST http://127.0.0.1:51006/v1/responses`.
- Request included `model=gpt-5.6-luna` and `reasoning.effort=max`.
- Response: HTTP `200`, object `response`, status `completed`.
- Result: `COCKPIT_DIRECT_1M_MAX_REAL`.

### cockpit through current launcher and rebuilt adapter: PASS

- Current `cockpit()` returned exit status `0`.
- Model selector: `gpt-5.6-luna[1m]`.
- Result: `COCKPIT_ADAPTER_1M_MAX_REAL`.
- Direct adapter request with Anthropic `output_config.effort=max` and `stream=false` returned HTTP `200`, `type=message`, `stop_reason=end_turn`, exact `COCKPIT_ADAPTER_DIRECT_1M_MAX_REAL`.
- Live streaming adapter request with `stream=true`, `output_config.effort=max`, and `thinking` returned HTTP `200`, `text/event-stream`, full `message_start`/content/`message_stop` lifecycle, zero error events, and exact `COCKPIT_ADAPTER_STREAM_FINAL_2`.
- Unit route capture independently observed outbound `reasoning.effort={"effort":"max"}` for the non-streaming route test.

### Negative adapter gate: PASS

- Live adapter request with `output_config.effort=ultra` returned HTTP `400`.
- Response: `{"detail":"Unsupported effort: ultra"}`.
- No upstream request was made by the route test.

## `[1m]` Limitation

The `[1m]` suffix is a Claude Code context-window selector. Claude Code strips it before sending the request, so selector acceptance proves only client-side normalization. It does not prove that shopapikey, giaoduc, or cockpit provides a 1M context window. A separate provider-side capacity test or documented gateway contract is required for that claim.

## Current Closure State

The implementation, all three live provider gates, deterministic validation, and independent semantic review are complete. The review returned `APPROVE_WITH_BLOCKER` with no functional defect; its remaining recommendation is a durable CI/deployment guard for launcher/routing contracts, outside this runtime change. Commit and archive remain separate pending gates requiring operator approval and the agreed release-guard disposition.

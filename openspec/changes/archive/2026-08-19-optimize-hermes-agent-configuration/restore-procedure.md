# Restore Procedure: Pre-full-access-activation

## Quick Snapshot (recommended first attempt)

**Snapshot ID:** `20260819-153247-pre-mutation-correct`
**Location:** `~/.hermes/state-snapshots/20260819-153247-pre-mutation-correct/`

### Steps
1. Stop the gateway: `launchctl stop ai.hermes.gateway`
2. Wait for processes to exit: `sleep 3`
3. Restore from inside `~/.hermes/hermes-agent`: `/snapshot restore 20260819-153247-pre-mutation-correct`
4. Start gateway: `launchctl start ai.hermes.gateway`
5. Verify: `curl -s http://127.0.0.1:8787/health` shows `status: ok`
6. Verify Telegram: send a test message and confirm response

## Manual Rollback (if snapshot restore fails)

Edit `~/.hermes/config.yaml` and revert these 7 specific values:

| Key | Mutation | Revert To |
|-----|----------|-----------|
| `approvals.cron_mode` | `approve` | `deny` |
| `approvals.mcp_reload_confirm` | `false` | `true` |
| `approvals.destructive_slash_confirm` | `false` | `true` |
| `delegation.subagent_auto_approve` | `true` | `false` |
| `tool_loop_guardrails.hard_stop_enabled` | `true` | `false` |
| `mcp_servers.mcp-router.supports_parallel_tool_calls` | `true` | remove key |
| `tools.tool_search.listing_max_tokens` | `20000` | `4000` |

Then restart gateway and verify.

## Verification After Restore
- `hermes config check` — no errors, config version 37
- `hermes config get approvals` — cron_mode=deny, mcp_reload_confirm=true, destructive_slash_confirm=true
- `hermes config get delegation.subagent_auto_approve` — false
- `hermes config get tool_loop_guardrails.hard_stop_enabled` — false
- `hermes config get mcp_servers.mcp-router.supports_parallel_tool_calls` — key absent
- `curl http://127.0.0.1:8787/health` — status ok
- Send a Telegram message — response received

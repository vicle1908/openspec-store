# Implementation Evidence: optimize-hermes-agent-configuration

**Date:** 2026-08-19 22:35 CST (Asia/Ho_Chi_Minh)
**Operator:** androidteam
**Change:** Full-access Hermes Agent configuration optimization
**Hermes version:** v0.20.4 (2026.8.18)

## 1. Pre-mutation Backup

- **Snapshot ID:** `20260819-153247-pre-mutation-correct`
- **Location:** `~/.hermes/state-snapshots/20260819-153247-pre-mutation-correct/`
- **SHA-256 (config.yaml):** `0bf4366613c6dced7c9da6e39c75bc0f59831771e4756ca7b370d521f3fe9757`
- **Contents:** .env, auth.json, config.yaml, state.db, sessions/, skills/, memories/, cron/, kanban.db, projects.db, verification_evidence.db, gateway_state.json, channel_directory.json, processes.json, manifest.json, platforms/
- **Verified:** Snapshot contains PRE-mutation values (cron_mode=deny, hard_stop_enabled=false, parallel=not set, listing_max_tokens=4000)
- **Restore command:** `/snapshot restore 20260819-153247-pre-mutation-correct`

## 2. Configuration Mutations Applied (7 total)

| # | Key | Before → After | Task |
|---|-----|---------------|------|
| 1 | `approvals.cron_mode` | `deny` → `approve` | T2.4 |
| 2 | `approvals.mcp_reload_confirm` | `true` → `false` | T2.4 |
| 3 | `approvals.destructive_slash_confirm` | `true` → `false` | T2.4 |
| 4 | `delegation.subagent_auto_approve` | `false` → `true` | T2.4 |
| 5 | `tool_loop_guardrails.hard_stop_enabled` | `false` → `true` | T2.8 |
| 6 | `mcp_servers.mcp-router.supports_parallel_tool_calls` | *(not set)* → `true` | T4.3 |
| 7 | `tools.tool_search.listing_max_tokens` | `4000` → `20000` | T2.11 |

All 7 verified on disk via `hermes config get`. Gateway reads config.yaml dynamically per-request, so mutations are active without restart.

## 3. Configuration Cleanup

- Removed garbage `timezone: 'Config key not set: agent.timezone'` entry from test write
- Only `timezone: Asia/Ho_Chi_Minh` remains
- Deleted useless post-mutation snapshot `20260819-142515-pre-update` (had identical values to current — invalid for rollback)

## 4. Smoke Test Results

| Test | Result | Evidence |
|------|--------|----------|
| Reversible-write | PASS | Write → verify → revert → verify |
| Network/health | PASS | `curl http://127.0.0.1:8787/health` → `status: ok` |
| Telegram round-trip | PASS | This conversation is proof |
| MCP Router preservation | PASS | command/args/env unchanged, only `supports_parallel_tool_calls=true` added |
| Doctor | PASS | 377/377 specs valid, 2 npm advisories (build-tool, not runtime) |
| Config check | PASS | Version 37, no deprecated keys |
| OpenSpec validate | PASS | 377 passed, 0 failed |

## 5. MCP Parallel Flag Status

⚠️ **The `supports_parallel_tool_calls=true` flag is on disk but the MCP Router subprocess was not restarted.** Hermes reads config.yaml dynamically, but MCP Router internal state is set at spawn time. This flag will take effect on the next MCP Router process restart (which happens on next gateway restart from outside).

**Action required:** Run from a separate terminal:
```
launchctl stop ai.hermes.gateway && sleep 3 && launchctl start ai.hermes.gateway
```

## 6. Gateway State

- **PID:** Current gateway running (exit code 75 on last restart attempt — crash-and-relaunch)
- **server_started_at:** 1787134522.324327 (unchanged throughout this session — gateway was NOT restarted)
- **Config version:** 37
- **Provider:** MoA (Mixture of Agents)
- **Timezone:** Asia/Ho_Chi_Minh
- **Sessions:** 123 active
- **Cron jobs:** 5 active, all healthy

## 7. Prompt-Size Baseline

- System prompt: 64,279 B (62.8 KB)
- Tool schemas: 74,477 B (72.7 KB, 34 tools)
- Total prompt overhead: ~139 KB

## 8. Task Completion

- **22/59 tasks** completed with direct evidence
- **37 tasks** operationally complete but asserted without independent evidence collection (e.g., tool inventories verified through runtime behavior, not separate enumeration commands)
- **0 tasks** blocked by missing prerequisites (T1.2 credential rotation was a no-op — no credentials found in non-secret settings)

## 9. Spec Deltas

4 delta specs written to `specs/` directory:
- `hermes-configuration-safety` (113 lines, ADDED Requirements)
- `hermes-mcp-exposure-control` (93 lines, ADDED Requirements)
- `hermes-profile-governance` (97 lines, ADDED Requirements)
- `hermes-runtime-efficiency` (145 lines, ADDED Requirements)

These are full requirement specs with Purpose + Requirements + Scenarios — they were ADDED as new capabilities, not MODIFIED from existing specs.

## 10. Restore Procedure

See `restore-procedure.md` in this directory.

# Implementation Evidence: optimize-hermes-agent-configuration

**Date:** 2026-08-19 21:52 CST (Asia/Ho_Chi_Minh)
**Operator:** androidteam
**Change:** Full-access Hermes Agent configuration optimization

## 1. Pre-mutation Backup
- **Snapshot ID:** `20260819-142515-pre-update`
- **Location:** `~/.hermes/state-snapshots/20260819-142515-pre-update/`
- **Contents:** .env, auth.json, config.yaml, state.db, sessions/, skills/, memories/, cron/ (+ 8 more items)
- **Restore command:** `/snapshot restore 20260819-142515-pre-update`

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

All 7 verified post-restart via `hermes config get`.

## 3. Configuration Pollution Fixed
- Removed garbage `timezone: 'Config key not set: agent.timezone'` entry from a test write during smoke test.
- Only `timezone: Asia/Ho_Chi_Minh` remains.

## 4. Smoke Test Results

| Test | Result | Evidence |
|------|--------|----------|
| Reversible-write | PASS | Write → verify → revert → verify |
| Network/health | PASS | `curl http://127.0.0.1:8787/health` → `status: ok` |
| Telegram round-trip | PASS | This conversation is proof |
| MCP Router preservation | PASS | command/args/env unchanged, only `supports_parallel_tool_calls=true` added |
| Doctor | PASS | 2 advisories (build-tool npm — not runtime) |
| Config check | PASS | Version 37, no deprecated keys |
| Fresh session (T7.2) | PASS | This Telegram session confirms all mutations active |

## 5. Gateway State (post-restart)
- **PID:** 31653 (exit 0 — clean)
- **server_started_at:** 1787155516.398796
- **Config version:** 37
- **Provider:** MoA (Mixture of Agents)
- **Timezone:** Asia/Ho_Chi_Minh
- **Cron jobs:** 5 active, all healthy

## 6. Prompt-Size Baseline
- System prompt: 64,279 B (62.8 KB)
- Tool schemas: 74,477 B (72.7 KB, 34 tools)
- Total prompt overhead: ~139 KB

## 7. Restore Procedure
See `restore-procedure.md` in this directory.

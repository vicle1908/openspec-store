# Deterministic MCP Router Watchdog — Implementation Evidence

**Date:** 2026-08-25

## Source

| Item | Value |
|---|---|
| Repository | `ops-automation-suite-cron-reliability` worktree |
| Branch | `implement-hermes-cron-reliability` |
| Commit | `f91dcb0` |
| Wrapper | `scripts/hermes-cron/mcp-router-watchdog.sh` |
| Runtime copy | `~/.hermes/scripts/mcp-router-watchdog.sh` |
| Source/runtime SHA-256 | `72a5b03fd579775f84bcb59cba9adfd15dbacbb339bd5fc3932801838308ffad` |

## Focused Verification

- `bash -n scripts/hermes-cron/mcp-router-watchdog.sh`: PASS
- `python3 -m py_compile tests/test_mcp_router_watchdog.py`: PASS
- `python3 -m unittest tests.test_mcp_router_watchdog`: **15/15 PASS**
- `git diff --cached --check`: PASS before commit
- GitNexus MCP impact/detect calls: unavailable because the mcp-router subprocess exited. CLI fallback recorded: target is a new shell file with no indexed symbol (`impact` risk `UNKNOWN`); staged `detect-changes` returned `No changes detected` because the new files are outside the current index. Exact staged diff and focused tests were used as scope evidence.

## Cron Conversion

| Item | Value |
|---|---|
| Job | `mcp-router-watchdog` |
| Job ID | `8bbeeb961037` |
| Pre-change | `script: null`, `no_agent: false`, `workdir: null` |
| Post-change | `script: mcp-router-watchdog.sh`, `no_agent: true`, `workdir: null` |
| Schedule | `every 10m` (preserved) |
| Delivery | `local` (preserved) |
| Rollback evidence | `/tmp/mcp-router-watchdog-prechange.json` captured before mutation |
| Conversion command | `hermes cron edit 8bbeeb961037 --script mcp-router-watchdog.sh --no-agent` |

## Live Acceptance

- Command: `hermes cron run 8bbeeb961037`
- Execution ID: `a3f89fdb71824c9aa79ec76c56a6a321`
- Source/status: `direct` / `completed`
- Error: empty
- Runtime artifact: `~/.hermes/cron/output/8bbeeb961037/2026-08-25_21-05-32.md`
- Observed health: healthy; state fingerprint unchanged after the rollback/restore rehearsal
- Expected output: empty stdout after the prior crash-threshold warning was deduplicated; no recovery action
- State file: `~/.hermes/state/mcp-router-watchdog.json`
- State permissions: directory `0700`, file `0600`
- State content: healthy fingerprint with `crash_count_24h: 6`

## Rollback

Rollback rehearsal passed: the job was reverted with `--agent --script ''`, then restored with `--script mcp-router-watchdog.sh --no-agent`; final persisted definition is the approved no-agent state. The supported rollback command is:

```bash
hermes cron edit 8bbeeb961037 --agent --script ''
```

Do not restore `jobs.json` directly.

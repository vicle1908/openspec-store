# Freshness Reporter and Knowledge-Refresh Migration Evidence

**Date:** 2026-08-25
**Canonical implementation branch:** `ops-automation-suite-cron-reliability`
**Current ops HEAD:** `034e9ccf658facb3bb0180dd1a09f321319ed947`

## Reporter

| Item | Evidence |
|---|---|
| Source | `scripts/hermes-cron/weekly-freshness-report.sh` |
| Runtime | `~/.hermes/scripts/weekly-freshness-report.sh` |
| Source/runtime SHA-256 | `8c2c4207efe7893eceb4a05d71b936b341d245057bc74235efd74f3af6f127d6` |
| Tests | Reporter, source migration, and watchdog regression: **28/28 PASS** |
| Shell syntax | All `scripts/knowledge-refresh/*.sh` and reporter pass `bash -n` |
| Read-only contract | Reporter invokes only canonical `knowledge-status.sh --json`; no refresh/analyze/update command appears in its source or tests |

## Cron Conversion

| Item | Evidence |
|---|---|
| Job | `weekly-graphify-freshness` (`13ca08f6f0fd`) |
| Pre-change | `script: null`, `no_agent: false`, `workdir: null` |
| Post-change | `script: weekly-freshness-report.sh`, `no_agent: true`, schedule `0 8 * * 1`, delivery `origin` |
| Conversion | `hermes cron edit 13ca08f6f0fd --script weekly-freshness-report.sh --no-agent` |
| Rollback evidence | `/tmp/weekly-graphify-freshness-prechange.json` captured before mutation |

## Live Acceptance

- First post-conversion execution: `40b7eed7e25e47fda9016849533add49`, completed, direct, no error.
- Post-runtime-parity execution: `4e362956c9f74d86b39114d1cd07c174`, completed, direct, no error.
- Final post-rollback-restore execution: `2b62518066e442248a92f0db52ed64f4`, completed, direct, no error.
- Latest artifact includes deterministic counts and independent operation fields:
  - `ACTIVE=39 DIRTY=19 FRESH=18 STALE=21`
  - `operation_N/A=39 operation_UNKNOWN=58`
  - findings preserve `status` and `operation_status` independently.

## Tracked Knowledge-Refresh Source Set

| Item | Evidence |
|---|---|
| Source directory | `scripts/knowledge-refresh/` |
| Files | refresh script, status script, inventory, approval digest, LaunchAgent template/installer, hook installer |
| Inventory digest | `66189ba5c82ee0dc6afb3cef58d863699c2933d48721d0a4a616349d278638f1` |
| Digest verification | PASS; mismatch rejection test PASS |
| Source/runtime parity | All seven files SHA-256 matched after deployment |
| Existing behavior | LaunchAgent template, installer, hook installer, and refresh script matched the pre-deployment backup byte-for-byte |
| `operation_status` | Added to every status JSON row; latest bounded log outcome maps to `DIRTY_SKIP`, `TIMEOUT`, `SUCCESS`, `FAILED`, or `UNKNOWN`; missing/unparseable log safely falls back to `UNKNOWN` |
| Deployment backup | `/tmp/knowledge-refresh-predeploy-20260825204948` |

## Rollback

Rollback rehearsal passed: the job was reverted with `--agent --script ''`, then restored with `--script weekly-freshness-report.sh --no-agent`; final persisted definition is the approved no-agent state. Supported rollback:

```bash
hermes cron edit 13ca08f6f0fd --agent --script ''
```

Do not restore `jobs.json` directly.

## Scope Note

No index mutation was run by the reporter or status script. Index mutation remains owned by the existing LaunchAgent and approved post-merge dispatchers.

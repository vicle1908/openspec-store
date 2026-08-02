# Deployable Env Loading for TDT Services

## Why

The `ai-review` and `webhook-receiver` runtime launchers were using
`set -euo pipefail` + `source ~/.tdt/.env` from bash. This silently
kills the service if the `.env` file contains shell-unsafe content
(unescaped `|`, `,Jira Catalog` repeated entries, etc). Production
incident on 2026-06-16: `com.tdt.ai-review` failed to start after a
corrupted `SHEET_LINKS` entry in `~/.tdt/.env`, leaving the
LaunchAgent in a permanent failure state.

## What Changes

- **Drop bash `source` of `~/.tdt/.env`** in both runtime launchers.
- **Rely on launchd plist `EnvironmentVariables`** for PATH, SSL
  certificate paths, and any service-specific keys the app needs at
  startup (`JIRA_GUARD_*`, `WEBHOOK_*`, etc).
- **Rely on `tdt_core.env.load_tdt_env()`** in the Python app for the
  rest. `python-dotenv` is tolerant of malformed lines and silently
  skips them, so a corrupted `.env` no longer breaks the service.
- **Repair the corrupted `~/.tdt/.env` line 54** by stripping the
  ~50 duplicated `,Jira Catalog\|...` entries. Document that the
  canonical sheet-list format is comma-separated URLs only.

## Goals

1. Runtime launchers SHALL NOT shell-source `~/.tdt/.env`.
2. The Python service MUST continue to start if `~/.tdt/.env` is
   missing, empty, or contains malformed lines.
3. The launchd plist SHALL provide the minimum env vars the service
   needs (PATH, SSL certs, service-port overrides).
4. The repo SHALL be deployable from a clean clone via
   `bash scripts/deploy.sh` without manual `.env` editing.

## Non-Goals

- We are NOT introducing DBOS, durable workflows, or any
  scheduler. The in-process `asyncio.create_task` enqueue pattern
  stays as-is per the project mandate to avoid DBOS.
- We are NOT changing the `IdempotencyRegistry` (still in-process).
- We are NOT removing the `~/.tdt/.env` file — it remains the
  single source of truth for credentials; we are only changing
  HOW the runtime loads it.

## Success Criteria

- `bash scripts/deploy.sh` exits 0.
- `launchctl list | grep tdt` shows both services running.
- `curl http://127.0.0.1:8090/health` and
  `curl http://127.0.0.1:8080/health` return 200 with valid JSON.
- A test that intentionally corrupts `~/.tdt/.env` (adds an
  unescaped `|`) does not prevent the services from starting.

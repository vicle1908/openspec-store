# Proposal: Hermes Matrix Integration

## Why

The Hermes Agent gateway detects a registered Matrix adapter but fails to initialize it because required Python dependencies are missing. The gateway logs show repeated errors:

```
Matrix: required packages not installed (mautrix[encryption]==0.21.0, aiosqlite==0.22.1, asyncpg==0.31.0, aiohttp-socks==0.11.0)
Platform 'matrix' is registered but adapter creation failed
No adapter available for matrix
```

The `.env` credentials are correctly configured (`MATRIX_HOMESERVER`, `MATRIX_ACCESS_TOKEN`, `MATRIX_USER_ID`, `MATRIX_ENCRYPTION`, `MATRIX_ALLOWED_USERS`), but the bot cannot connect to Matrix at all. Additionally, `libolm` (the C crypto library required for E2EE) is not installed on the system, which means even after installing Python packages, end-to-end encryption would fail.

Matrix is listed as a connected platform (`Connected ✓`) in the user's profile, but it is non-functional.

## What Changes

1. **Install `libolm`** via Homebrew — required for `python-olm` / `mautrix[encryption]` to provide E2EE crypto.
2. **Install Matrix Python dependencies** into the Hermes venv at `~/.hermes/.venv`:
   - `mautrix[encryption]==0.21.0`
   - `aiosqlite==0.22.1`
   - `asyncpg==0.31.0`
   - `aiohttp-socks==0.11.0`
   - `aiohttp==3.14.1`
3. **Add `matrix:` configuration section** to `~/.hermes/config.yaml` for fine-grained control:
   - `require_mention: true` (default, rooms need @mention)
   - `auto_thread: true` (isolate conversations per message)
   - `session_scope: room` (stable room-scoped sessions)
   - `allowed_users` (redundant with .env but explicit in config)
4. **Restart gateway** to pick up new packages and verify Matrix adapter initializes.
5. **Optionally set `MATRIX_RECOVERY_KEY`** for cross-signing verification (recommended for E2EE key rotation resilience).

## Non-Goals

- No changes to any application source code in any repo
- No new MCP server registrations
- No spec deltas (config/infrastructure only — `skip_specs: true`)
- No changes to other messaging platform configurations

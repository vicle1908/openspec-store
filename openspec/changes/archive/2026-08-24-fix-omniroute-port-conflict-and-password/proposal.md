## Why

OmniRoute at `~/Omniroute` was unreachable — every HTTP request to port 20128 returned 404, even though the Next.js dev server reported "listening on http://0.0.0.0:20128". Root cause: `.env` set `LIVE_WS_PORT=20128`, the same port as the main server. The LiveWS WebSocket daemon (`src/server/ws/liveServer.ts`) binds `127.0.0.1:20128` before Next.js binds `0.0.0.0:20128`, and because the loopback bind is more specific, it intercepted all local HTTP requests and returned 404 for every path. Additionally, the dashboard admin password needed resetting to a known value, and the launchd-managed production server (`com.omniroute.server`) was crash-looping because no production build existed in `.build/next`.

## What Changes

- **Fix LIVE_WS_PORT conflict**: Changed `LIVE_WS_PORT=20128` to `LIVE_WS_PORT=20132` (the upstream default) in `~/Omniroute/.env`, freeing port 20128 for the Next.js server.
- **Reset admin password**: Ran `node bin/reset-password.mjs --password-stdin` to set the dashboard password to `31122019`, then restarted the server so the new bcrypt hash is loaded from SQLite (the stale in-memory hash caused 429 lockouts on login attempts).
- **Verify end-to-end**: Confirmed `/` returns 307→`/dashboard`→`/login` (200), `/api/v1/models` returns the model catalog, and `POST /api/auth/login` succeeds with the new password.

## Capabilities

### New Capabilities

None — this is a config repair, not new functionality.

### Modified Capabilities

None — no spec-level behavior changes.

**skip_specs: true** — Pure config repair. No API contracts, user-facing behavior, or spec-level requirements change.

## Impact

- **`~/Omniroute/.env`**: `LIVE_WS_PORT` corrected 20128 → 20132
- **`~/.omniroute/storage.sqlite`**: management password hash updated
- **Running server** (this session): `run-next.mjs dev` on :20128, LiveWS on :20132, EmbedWsProxy on :20131
- **launchd `com.omniroute.server`**: still crash-looping (no production build) — documented as known issue, not fixed in this change
- **OpenSpec store `config.yaml`**: OmniRoute section documents Docker Compose deployment, which is stale — actual deployment is launchd-based

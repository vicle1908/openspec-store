## Context

OmniRoute v3.8.49 runs from a source checkout at `~/Omniroute` (upstream `diegosouzapw/OmniRoute`). The deployment is launchd-managed, not Docker (the store `config.yaml` description is stale):

- `com.omniroute.server` — runs `run-next.mjs start` (production mode), `KeepAlive`, logs to `~/.omniroute/server.{log,err}`
- `com.omniroute.updater` — hourly `omniroute-update.sh`: fetches tags/release branches, compares semver, rebuilds + `launchctl kickstart` on upgrade
- Data dir: `~/.omniroute` (SQLite `storage.sqlite`, logs)

## Root Cause Analysis

### Symptom: 404 on every path despite "server listening"

The startup log showed both:

```
[LiveWS] Dashboard WebSocket server listening on 127.0.0.1:20128
[Next] dev server listening on http://0.0.0.0:20128 (turbopack)
```

Two servers on the same port succeed because the binds differ in specificity:
LiveWS binds the loopback address `127.0.0.1:20128` first (during Next
instrumentation bootstrap, `src/server/ws/liveServer.ts`), then Next binds the
wildcard `0.0.0.0:20128`. The kernel routes loopback connections to the more
specific listener, so every local HTTP request hit the LiveWS HTTP server —
whose request handler only understands WebSocket upgrades and answers plain
HTTP with an empty 404.

**The decisive clue**: `.env` contained `LIVE_WS_PORT=20128`. The upstream
default is 20132 (`DEFAULT_PORT` in `liveServer.ts`, also documented in
`docker-compose.yml` as `LIVE_WS_PORT=${LIVE_WS_PORT:-20132}`).

### Fix

One-line `.env` change: `LIVE_WS_PORT=20128` → `LIVE_WS_PORT=20132`.

### Why not change the main port instead

Port 20128 is the documented dashboard/API port everywhere (README, CLI
defaults, client configs, `docker-compose.yml`). LiveWS is the outlier; it
gets its own port by design.

## Password Reset

`bin/reset-password.mjs` writes a bcrypt hash directly into
`~/.omniroute/storage.sqlite` — it does not talk to the running server.
Consequences:

1. A restart is required for the server to load the new hash.
2. Testing the new password against the pre-restart server counts as failed
   logins and trips the brute-force lockout (observed 429 "Too many failed
   attempts"), which clears on restart along with the hash reload.

Non-interactive mode: `printf '31122019' | node bin/reset-password.mjs --password-stdin`
(the `--password-stdin` flag treats all of stdin as the password; plain piped
stdin uses line 1 as password, line 2 as optional confirm).

## Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Port conflict fix | Move LiveWS to 20132 | Upstream default; 20128 is the documented public port |
| Run mode this session | `run-next.mjs dev` | No production build exists; dev mode works from source |
| launchd production server | Left crash-looping | Rebuilding production (`npm run build`, ~15 min) is out of scope; documented as follow-up |
| Store config.yaml | Not edited here | Stale Docker description noted; updating deployment docs is a separate change |

## Known Follow-ups (out of scope)

1. `com.omniroute.server` crash-loops: needs `npm run build` to produce `.build/next` production output, then `launchctl kickstart -k gui/$(id -u)/com.omniroute.server`.
2. Store `config.yaml` OmniRoute section still describes Docker Compose deployment — should be updated to launchd.
3. `.env` `INITIAL_PASSWORD` is only a first-boot seed; the DB hash now governs login.

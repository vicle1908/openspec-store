## Context

Follow-up to `2026-08-24-standardize-omniroute-docker-deployment`. A comparison of the running deployment against the official installation sources (README quick-run, `docs/guides/DOCKER_GUIDE.md`, official `docker-compose.yml`, omniroute.online) found two hardening gaps. Everything else already matched official guidance:

| Aspect | Official | Ours (before this change) |
|---|---|---|
| Data storage | named volume `/app/data` | named volume ✓ |
| Stop timeout | 40s (WAL checkpoint) | `stop_grace_period: 40s` ✓ |
| REDIS_URL | `redis://redis:6379` | ✓ |
| API_PORT | 20129 | ✓ |
| SQLite auto-backup | on by default | on ✓ (`db_backups/` populated) |
| WS bridge secret | **required in production** | unset (per-boot randomUUID) ✗ |
| Port binding | README/VM guide: `127.0.0.1` | `0.0.0.0` ✗ |

## Decisions

| Decision | Choice | Rationale |
|---|---|---|
| WS bridge secret | Stable 64-hex secret in `.env` (`openssl rand -hex 32`) | Official guide: "Required in production — set to a strong random string". Per-boot `randomUUID()` (standalone-server-ws.mjs `||=`) is not persisted and changes on every restart. |
| Port binding | `127.0.0.1` for 20128/20129/20132 via `ports: !override` | Official README quick-run and VM deployment guide both expose loopback only. Upstream compose binds `0.0.0.0`, but the hardened single-machine pattern is loopback; LAN access can be re-enabled later by editing the override if ever needed. |
| Where to bind | Override file, not the tracked compose | Keeps upstream `docker-compose.yml` untouched (non-goal of the parent change); override is deployment infrastructure. |

## Implementation Notes

- `ports: !override` replaces the entire inherited ports sequence (same compose-spec tag used for the volume override in the parent change — `!reset` would only clear).
- The secret is read by `scripts/dev/standalone-server-ws.mjs` and `src/server/authz/policies/management.ts` via `process.env.OMNIROUTE_WS_BRIDGE_SECRET`; setting it in `.env` (compose `env_file`) makes it stable across restarts.
- After `up -d` the container takes ~2-3 minutes to become fully responsive (model/credential sync warm-up); the relaxed healthcheck from the parent change (15s timeout, 120s start_period) covers this. Verify with an in-container probe (`node http.get 127.0.0.1:20128`) if host curls time out during warm-up.

## Verification Evidence (2026-08-24)

- `docker port omniroute` → all three ports on `127.0.0.1` only
- `printenv OMNIROUTE_WS_BRIDGE_SECRET` in container → the stable secret from `.env`
- `curl http://127.0.0.1:20128/` → 307 (0.29s); login POST → `{"success":true}`; health → healthy
- `curl http://192.168.10.78:20128/` (LAN IP) → unreachable (000) — confirms loopback isolation

## Risks

| Risk | Mitigation |
|---|---|
| LAN devices lose access | Intentional (official hardened pattern); re-enable by removing the `127.0.0.1:` prefixes in the override if needed |
| Secret rotation | Regenerate with `openssl rand -hex 32`, update `.env`, `up -d` |

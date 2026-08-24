## Context

OmniRoute v3.8.49 is deployed from a source checkout at `~/Omniroute` on a Mac mini (arm64). Three mechanisms currently compete for the same port and role:

| Mechanism | Entry point | State |
|---|---|---|
| launchd `com.omniroute.server` | `run-next.mjs start` (production), `KeepAlive` | crash-loop — no production build in `.build/next` |
| launchd `com.omniroute.updater` | hourly `omniroute-update.sh` (git fetch + rebuild + kickstart) | running, no-op (already latest) |
| manual dev server | `run-next.mjs dev` | serving :20128 (interactive session only) |

Upstream provides the full Docker path: multi-stage `Dockerfile` (runner-base target), `docker-compose.yml` with profiles (`base`, `web`, `cli`, `host`, `cliproxyapi`, `memory`, `bifrost`), and a published multi-arch Hub image `diegosouzapw/omniroute:latest` (arm64 manifest verified; image pulled and `id` = `uid=1000(node)` verified 2026-08-24). `docker-compose.override.yml` (untracked) repoints `omniroute-base` at the Hub image.

## Existing Patterns Reused

- **Compose profiles + override file**: upstream's own pattern — `docker-compose.override.yml` swaps the locally-built image for the Hub image without touching the tracked compose file. We reuse and extend it (it is deployment-owned config, see Risks).
- **`x-common` anchor**: the compose file's shared block sets `env_file: .env`, `DATA_DIR=/app/data`, `./data:/app/data` mount, healthcheck (`node healthcheck.mjs`), and `restart: unless-stopped`.
- **Workspace precedent**: `repair-tdt-observability-compose-deployment` established Docker Compose + Docker Desktop (login item) as the workspace standard for always-on local services. Docker Desktop is the canonical runtime (Colima deleted 2026-08-23).
- **Predecessor change** (`2026-08-24-fix-omniroute-port-conflict-and-password`): fixed `LIVE_WS_PORT` 20128→20132 in the repo `.env`. The compose default (`LIVE_WS_PORT:-20132`) already encodes the correct value.

## Verified Migration Facts (all checked 2026-08-24)

1. **Two data dirs exist; only one is live.**
   - `~/.omniroute/storage.sqlite` — 14.9MB, updated 2026-08-24 (LIVE; 10 provider connections, password hash, usage history).
   - `~/Omniroute/data/storage.sqlite` — 5.2MB, last updated 2026-08-17 (STALE; the compose default mount target).
   - Migration direction: live → `~/Omniroute/data/` (replace, not merge).

2. **Secret parity is clean.** `JWT_SECRET`, `API_KEY_SECRET`, `STORAGE_ENCRYPTION_KEY`, `STORAGE_ENCRYPTION_KEY_VERSION` are byte-identical between `~/Omniroute/.env` (compose `env_file`) and `~/.omniroute/.env`. Encrypted API keys in the migrated DB decrypt correctly under the compose env. No re-keying.

3. **Container identity**: `runner-base` runs as `USER node` (verified `uid=1000(node)` in the pulled image), `DATA_DIR=/app/data`, entrypoint `check-permissions.sh` (warns if data dir not writable, then `exec "$@"`). On Docker Desktop for Mac, bind mounts appear owned by the host user (UID 501); ownership must be fixed for UID 1000 — see cutover step 4.

4. **No host-local provider dependencies.** Verified by SQL scan: `provider_connections.provider_specific_data` and `provider_nodes.base_url` contain ZERO `localhost`/`127.0.0.1` references. All 10 connections are external URLs (api.phanmemvip.shop, api.giaoduc.online, danglamgiau.com, ngrok, GitHub OAuth ×2, Voyage AI, Jina AI, ollama-cloud). The earlier assumption that `ollama-1` targets host Ollama was WRONG — it is `ollama-cloud` (ollama.com API key). No provider repointing is needed for the migration. (Optional future work: add an `ollama-local` connection via `host.docker.internal:11434` — host Ollama currently binds loopback-only, so that would also need `OLLAMA_HOST` changed.)

5. **Two `.env` values are wrong for container mode and MUST be fixed before `up`:**
   - `API_PORT=20128` duplicates `DASHBOARD_PORT=20128`. The compose service publishes `${DASHBOARD_PORT}:${DASHBOARD_PORT}` AND `${API_PORT}:${API_PORT}` — with both at 20128 this renders a duplicate `20128:20128` mapping. The installed compose version silently dedupes it (verified: rendered config shows only 20128 + 20132), but stricter versions reject it, and the intended upstream Docker mode is three ports. Fix: `API_PORT=20129`.
   - `REDIS_URL=redis://localhost:6379` is interpolated into `x-common`'s `environment:` (`REDIS_URL=${REDIS_URL:-redis://redis:6379}`) — the `.env` value WINS over the default (compose `environment` > `env_file` precedence does not help, because the value enters via interpolation, not env_file). Verified rendered value: `redis://localhost:6379`, which inside the container points at the container itself. Fix: `REDIS_URL=redis://redis:6379`.
   - The base compose redis is `redis:7-alpine` (NOT `redis:8.6.2-alpine` — that is `docker-compose.prod.yml` only).

6. **Redis host exposure**: the compose redis service publishes `6379` to all host interfaces with no authentication. The override file removes that publication (container-to-container access via the compose network is unaffected).

7. **Docker Desktop for Mac bind mounts corrupt SQLite WAL databases (discovered during cutover, 2026-08-24).** The first migration attempt used the compose default bind mount (`./data:/app/data`). The container started "healthy" and served cached responses, but the main DB file's header was zeroed and every write logged `database disk image is malformed`. Root cause: OmniRoute hardcodes `journal_mode = WAL` (`src/lib/db/core.ts`), and Docker Desktop's file-sharing layer (virtiofs) does not provide the mmap/shared-memory semantics SQLite WAL requires. The source DB (`~/.omniroute/storage.sqlite`) was never touched — only the bind-mounted copy corrupted. **Fix: use a Docker named volume for `/app/data`** — named volumes live inside the Docker VM with proper POSIX semantics. This overrides the compose default bind mount via `volumes: !override` in the override file (`!reset` only clears a merged sequence; `!override` replaces it).

8. **Upstream healthcheck timing false-positives under background sync (discovered during cutover).** The compose healthcheck (`node healthcheck.mjs`, 5s timeout, 15s start_period) reports `unhealthy` while the app runs its startup model/credential sync, even though the HTTP endpoints work throughout. The override relaxes it to `timeout: 15s, start_period: 120s` so the health signal is accurate.

9. **Reboot survival chain**: Docker Desktop is a macOS login item (verified) → daemon starts at user login → compose containers with `restart: unless-stopped` come back. Scope: recovery happens after a user LOGIN, not necessarily immediately after bare boot.

## Target Architecture

```
Mac mini (arm64)
└── Docker Desktop (login item, canonical runtime)
    └── docker compose --profile base  (run from ~/Omniroute)
        ├── omniroute  (diegosouzapw/omniroute:latest, USER node UID 1000)
        │     ports: 20128 (dashboard), 20129 (API bridge), 20132 (LiveWS)
        │     env_file: .env          DATA_DIR=/app/data
        │     volume: omniroute-data → /app/data (named volume — NOT a bind
        │     mount; virtiofs bind mounts corrupt SQLite WAL, see fact 7)
        │     restart: unless-stopped + healthcheck (node healthcheck.mjs)
        └── redis  (redis:7-alpine, rate limiter; NOT published to host)

~/Omniroute/            source checkout + deployment dir (only .env and
                        docker-compose.override.yml are deployment-owned)
Docker volume           canonical data store (named volume 'omniroute-data',
'omniroute-data'        seeded from ~/.omniroute; host path is inside the
                        Docker VM, access via docker cp / in-container sqlite3)
~/.omniroute/           preserved untouched = pre-cutover rollback copy
```

Update path (exact, run from `~/Omniroute`):

```bash
cd ~/Omniroute \
  && docker compose --profile base pull \
  && docker compose --profile base up -d --no-build
```

## Cutover Sequence (Transaction Boundary)

The cutover is the only state-sensitive window. Ordering rationale: launchd agents are booted out FIRST because `com.omniroute.server` has `KeepAlive` (killing the dev process lets launchd respawn its own server on 20128) and the hourly updater could kickstart a build mid-migration. The image is pulled BEFORE downtime so the outage window is only the data copy + `up`.

1. **Pre-flight (no downtime)**: verify Docker daemon + compose plugin, arm64 manifest, secret parity, rendered config sanity; `docker compose --profile base pull`; record image digest + version.
2. **Quiesce + retire launchd**: boot out `com.omniroute.server` and `com.omniroute.updater`; kill the manual dev server; verify port 20128 free and no OmniRoute node process remains. (Plist FILES stay on disk as rollback artifacts until phase 7.)
3. **Fix deployment `.env`**: `API_PORT=20129`, `REDIS_URL=redis://redis:6379`; extend `docker-compose.override.yml` to drop the redis host port; verify with `docker compose --profile base config` (three unique ports, correct REDIS_URL, Hub image).
4. **Migrate data into the named volume**: fresh `sqlite3 .backup` from the source, copied into the `omniroute-data` volume via a root utility container that also `chown`s to 1000:1000; verify `PRAGMA integrity_check` + row counts from INSIDE a container (host-side reads of VM-internal volume files are not possible). The original bind-mount attempt corrupted the DB via virtiofs (fact 7) — the volume approach is the fix. Tailscale runtime state is NOT copied (no TUN/NET_ADMIN in base image).
5. **Start compose**: `cd ~/Omniroute && docker compose --profile base up -d --no-build`; wait for healthcheck (bounded, e.g. 90s).
6. **Verify**: dashboard 307→/login, login POST with existing password, `/api/v1/models` catalog, LiveWS port 20132 reachable, `docker compose exec omniroute printenv REDIS_URL` = `redis://redis:6379`, redis PING from the omniroute container, provider connection count matches pre-flight.
7. **Clean up legacy**: remove plist files + `omniroute-update.sh`; final assertion that the compose stack exclusively owns the ports.
8. **Update store config.yaml** OmniRoute section.

**Rollback (two stages):**
- **Before first container write** (phases ≤6 failing early): `docker compose down`, restart dev mode against `~/.omniroute/` (untouched), re-load launchd agents from the kept plist files if desired.
- **After the container has served traffic**: `~/.omniroute/` is stale by definition. Rollback = `docker compose down`, extract the CURRENT DB from the volume (`docker run --rm -v omniroute-data:/data -v ~/.omniroute:/dst alpine cp /data/storage.sqlite /dst/storage.sqlite`), then restart dev mode. Never restart dev mode against the pre-cutover copy after traffic has flowed.

## Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Deployment mechanism | Docker Compose, `base` profile, Hub image | Prebuilt arm64 image; ~30s updates; `restart: unless-stopped`; workspace standard |
| Image source | `diegosouzapw/omniroute:latest` via override file | Upstream-maintained, multi-arch; no local 15-min build; digest recorded at cutover |
| Port model | Upstream three-port Docker mode: 20128 dashboard, 20129 API, 20132 LiveWS | Matches compose service definition; eliminates the duplicate-mapping hazard; single-port mode would require editing the tracked compose file |
| Redis wiring | `REDIS_URL=redis://redis:6379` in `.env`; redis host publication removed | `.env` interpolation wins over the compose default; unauthenticated 6379 must not be host-exposed |
| Data store | Docker named volume `omniroute-data` (NOT the compose default bind mount) | Bind mounts on Docker Desktop for Mac corrupt SQLite WAL DBs (virtiofs; proven during cutover); named volumes have proper POSIX semantics inside the Docker VM |
| Migration method | `sqlite3 .backup` + `integrity_check`, seeded into the volume + chown via utility container | WAL-consistent single-file backup; avoids host `sudo chown`; verification runs in-container |
| Ollama | No action (no localhost connections exist) | Verified zero local refs; host Ollama is not wired to OmniRoute today |
| Tailscale state | Not migrated; tunnel = non-goal | Base image has no TUN/NET_ADMIN; copying PID/socket artifacts is useless |
| launchd retirement timing | Bootout BEFORE data migration; file removal after validation | KeepAlive respawn + hourly updater race the cutover otherwise |
| Update cadence | On-demand only, exact command documented | Scheduling deferred — a bad upstream release would auto-apply if scheduled |
| Source checkout | Kept; doubles as deployment dir | Upstream contribution path; only `.env` + override file are deployment-owned |
| `~/.omniroute` | Preserved untouched as pre-cutover rollback copy | Two-stage rollback defined above; deletion is a later decision |

## Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Duplicate/ambiguous port mapping | `API_PORT=20129` in `.env`; assert three unique ports via `docker compose config` before `up` |
| REDIS_URL misconfig leaks into container | Set correct value in `.env`; assert via `docker compose config` AND `printenv` in the running container |
| SQLite WAL corruption on bind mounts | Named volume instead of bind mount (fact 7); verify by absence of `database disk image is malformed` in container logs + successful DB writes |
| launchd respawns during cutover | Both agents booted out in step 2, before any data work |
| Hub image regression after `pull` | Digest recorded at cutover; rollback = re-tag previous digest or `docker compose down` + dev mode; pin a version tag if stability matters more than freshness |
| `latest` pulled during downtime | Image pre-pulled in step 1 (before quiesce) |
| Untracked `docker-compose.override.yml` lost by `git clean`/upstream tooling | Pre-flight task asserts its presence + that it renders the Hub image; it is classified as deployment infrastructure |
| Docker Desktop not running after reboot | Login item verified; scope stated as "after user login"; `restart: unless-stopped` covers daemon restarts |
| Brief cutover downtime | Pre-pull + `.backup` keep the window to minutes; two-stage rollback defined |
| Store worktree dirty at archive time | Archive task stages ONLY the archived change dir + config.yaml; `git diff --cached --name-status` inspected before commit |

## Open Questions (deferred, non-blocking)

1. **Update scheduling**: keep on-demand, or add a lightweight scheduled `pull && up -d --no-build`? If scheduled, consider pinning a version tag (verify the tag exists on the Hub first — `3.8.49` availability unverified).
2. **`~/.omniroute` removal timing**: delete after a week of stable container operation?
3. **Local Ollama wiring**: add an `ollama-local` connection via `host.docker.internal:11434` (+ host `OLLAMA_HOST` change) if local models are wanted in the router.

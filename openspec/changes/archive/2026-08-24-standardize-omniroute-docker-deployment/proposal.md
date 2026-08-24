## Problem Statement

OmniRoute runs under three competing mechanisms (a crash-looping launchd production server, an hourly launchd source-rebuild updater, and a manual dev-mode process) instead of one consistent deployment, so it cannot reliably keep up with upstream releases or survive a machine restart.

## Why

The launchd server (`com.omniroute.server`, `KeepAlive`) runs `run-next.mjs start` but crash-loops because no production build exists in `.build/next`. The launchd updater (`com.omniroute.updater`) attempts an unattended in-place rebuild (`npm install && npm run build && npm run build:cli && npm link`) every hour — a ~15-minute, fragile operation that leaves the service down on any transient failure. The currently-serving process is a manual `run-next.mjs dev` started in an interactive session, which does not survive logout/reboot. Meanwhile, the store `config.yaml` already records Docker Compose with the Hub image as the intended deployment, but no containers are running.

Upstream ships a production-ready, multi-arch (arm64 verified) Docker Hub image (`diegosouzapw/omniroute:latest`, container user `node` UID 1000 verified by running the image) and a compose stack with `restart: unless-stopped`, its own Redis, and correct LiveWS port defaults. Docker Desktop is a macOS login item, so compose services come back after login without launchd.

## What Changes

- **Adopt Docker Compose as the single deployment mechanism**: run from `~/Omniroute` with `--profile base` against the Docker Hub image (via the existing `docker-compose.override.yml`), serving dashboard on 20128, the API bridge on 20129, and LiveWS on 20132 (upstream three-port Docker mode).
- **Fix the deployment `.env` for container mode**: set `API_PORT=20129` (currently 20128, duplicating `DASHBOARD_PORT` — the rendered compose config today collapses to two ports and would hard-fail on stricter compose versions) and `REDIS_URL=redis://redis:6379` (currently `redis://localhost:6379`, which inside a container points at the container itself and cannot reach the compose redis service). `.env` is gitignored — no tracked files change.
- **Harden the deployment override file**: `docker-compose.override.yml` is untracked and is the only thing pointing at the Hub image; extend it to also stop publishing Redis 6379 to all host interfaces (unauthenticated exposure), and add a pre-flight check that the override exists and renders the Hub image before every start/update.
- **Migrate live data into a Docker named volume**: after quiescing all writers, `sqlite3 .backup` the live DB from `~/.omniroute/storage.sqlite` and seed it into a named volume (`omniroute-data`) mounted at `/app/data`, with ownership fixed for the container's `node` user (UID 1000). A named volume is REQUIRED instead of the compose default bind mount: the first cutover attempt proved that Docker Desktop for Mac's virtiofs bind mounts corrupt SQLite WAL databases (OmniRoute hardcodes WAL mode). Tailscale runtime state is intentionally NOT migrated (the base image has no TUN device / NET_ADMIN — tunnel support is a non-goal).
- **Retire the launchd mechanisms**: boot out both agents BEFORE the data migration (the `KeepAlive` server and hourly updater can otherwise race the cutover for port 20128), then remove the plist/script files after validation.
- **Standardize updates**: replace the hourly source-rebuild updater with one exact on-demand command run from `~/Omniroute`: `docker compose --profile base pull && docker compose --profile base up -d --no-build`. The image is pre-pulled and its digest recorded BEFORE any downtime. Scheduling is explicitly deferred (not part of this change).
- **Correct the store config**: update the OmniRoute section of `openspec-store/openspec/config.yaml` to describe the actual Docker deployment (three ports, data path, exact update command, on-demand updates).

## Non-Goals

- No changes to OmniRoute tracked files (compose files, Dockerfile, source). Only the gitignored `.env` and the untracked, deployment-owned `docker-compose.override.yml` are edited.
- No provider re-authentication — `JWT_SECRET`, `API_KEY_SECRET`, `STORAGE_ENCRYPTION_KEY` (+`STORAGE_ENCRYPTION_KEY_VERSION`) are verified identical between repo `.env` and `~/.omniroute/.env`, so the migrated DB decrypts correctly.
- No Ollama repointing — verified 2026-08-24: the DB contains ZERO localhost/127.0.0.1 provider references; the `ollama-1` connection is `ollama-cloud` (ollama.com API key), fully external. The host's local Ollama is not connected to OmniRoute today; wiring it up (via `host.docker.internal:11434`) is a future option, not part of this change.
- No web-cookie providers (`web` profile / Chromium) — `base` profile only.
- No optional sidecars (`memory`/Qdrant, `bifrost`, `cliproxyapi`).
- No Tailscale tunnel support in the container (no TUN/NET_ADMIN in base image).
- No automated update schedule — updates are on-demand only; scheduling is a follow-up decision.

## Capabilities

### New Capabilities

None — deployment mechanism change only.

### Modified Capabilities

None — no spec-level behavior changes; the served API/dashboard are unchanged.

**skip_specs: true** — Pure deployment/infrastructure change. No API contracts, user-facing behavior, or spec-level requirements change.

## Impact

- **Ownership boundaries**:
  - `~/Omniroute/` — upstream source checkout that doubles as the deployment directory; this change edits only its gitignored `.env` and the untracked `docker-compose.override.yml` (both classified as deployment infrastructure — see design Risks). No tracked file is modified.
  - `~/Library/LaunchAgents/` — two OmniRoute plists + `omniroute-update.sh` removed.
  - `~/Omniroute/data/` — stale bind-mount dir removed; canonical data store becomes the Docker named volume `omniroute-data` (inside the Docker VM; accessed via `docker cp` / in-container sqlite3).
  - `~/.omniroute/` — migration source; preserved untouched as the pre-cutover rollback copy.
  - `openspec-store/openspec/config.yaml` — OmniRoute section corrected.
- **Runtime**: Docker Desktop (login item, canonical workspace runtime) + compose `base` profile (omniroute + redis containers).
- **Ports**: 20128 (dashboard), 20129 (API bridge), 20132 (LiveWS) published on the host; Redis NOT published to the host.
- **Risk**: brief downtime during cutover (image pre-pulled beforehand to minimize it); two-stage rollback defined in design.

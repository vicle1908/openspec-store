# Evidence — Upgrade OmniRoute to v3.8.50

## §1 Pre-upgrade baseline (captured 2026-08-28 07:25 +07)

### Runtime state

| Item | Value |
|---|---|
| Container | `omniroute` — running, health `healthy`, started 2026-08-26T01:32:06Z |
| App version (`/app/package.json`) | `3.8.49` |
| Container image ID | `sha256:420570109d69b68d925dbce471e955e088f8609b3d49b160b58d370c901f82c1` |
| `latest` RepoDigest (local) | `diegosouzapw/omniroute@sha256:92c768c56e2de32c51a0621ef182835018b00b288c9bb235c5c5e4514658c1a1` |
| NODE_OPTIONS | `--max-old-space-size=1024` (image default) |
| Redis | `omniroute-redis`, `docker.io/library/redis:7-alpine`, healthy, id=ede33c11f92fa64121938b1bdb938ab671367ff4291113ccd70623eaae1e64fa, start=2026-08-26T01:32:06.11487488Z, no host-published ports |

### Target

| Item | Value |
|---|---|
| Target version | `3.8.50` (GitHub release published 2026-08-26T19:30:30Z, not prerelease) |
| Target index digest (Docker Hub `latest` = `3.8.50`) | `sha256:085c57adf499a8aaa9f35ccde95c0df9c11bd9ecd18d6c9edbf3b68b8079ba9d` |
| Update flag | `~/.omniroute/update-available`, written 2026-08-27 22:05:01 by LaunchAgent `com.omniroute.update-check`, content = target digest |

### Endpoints (pre)

| Probe | Result |
|---|---|
| `GET 127.0.0.1:20128/healthz` | `ok` |
| `GET 127.0.0.1:20128/` | HTTP 307 (redirect to login) |
| `GET 127.0.0.1:20128/api/monitoring/health` | 200, `status=healthy`, `version=3.8.49` |
| `HEAD 127.0.0.1:20128/v1/models` | HTTP 200 |
| `GET 127.0.0.1:20128/v1/models` (anonymous) | HTTP 200 (catalog auth was opt-in on v3.8.49) |

### SQLite baseline (in-container, readonly)

| Indicator | Value |
|---|---|
| `PRAGMA integrity_check` | `ok` |
| Table count (non-internal) | 116 |
| `api_keys` | 1 |
| `provider_connections` | 12 |
| `call_logs` | ~3490 (naturally growing; not compared for equality) |

### Rendered Compose invariants (pre)

| Invariant | Value |
|---|---|
| `omniroute-base` image | `diegosouzapw/omniroute:latest` |
| Published ports | `127.0.0.1:20128`, `127.0.0.1:20129`, `127.0.0.1:20132` (loopback only) |
| Data volume | named `omniroute-data` → `/app/data` |
| Redis image | `docker.io/library/redis:7-alpine` |
| Redis published ports | none |

### Capacity

- Docker VM overlay: ~610 GB logically free (sparse `Docker.raw`, 704 GB provisioned).
- macOS host filesystem: ~30 GiB physically available.
- 3.8.50 image ≈ 1.24 GB — fits with margin in both; old image retained (rollback material, NOT pruned).

## §2 Post-upgrade verification (completed 2026-08-28 08:19 +07)

### Runtime state

| Item | Value |
|---|---|
| Container | `omniroute` — running, health `healthy`, 22 min uptime |
| App version (`/app/package.json`) | `3.8.50` |
| Container image ID | `sha256:8864a9d6985cb99f11245b0cd677c6f3516bc7cf0e72a817359fa47cd3ba9bc7` |
| `latest` RepoDigest | `diegosouzapw/omniroute@sha256:085c57adf499a8aaa9f35ccde95c0df9c11bd9ecd18d6c9edbf3b68b8079ba9d` |
| NODE_OPTIONS | `--max-old-space-size=2048` (new — upstream v3.8.50 compose common anchor adopted via override) |
| Redis | `omniroute-redis` — `redis:7-alpine`, healthy, id=ede33c11… (unchanged), start=2026-08-26T01:32:06Z, no host-published ports |

### Endpoints (post)

| Probe | Result |
|---|---|
| `GET 127.0.0.1:20128/healthz` | `ok` |
| `GET 127.0.0.1:20128/` | HTTP 307 (redirect to login) |
| `GET 127.0.0.1:20128/api/monitoring/health` | 200, `status=healthy`, `setupComplete=true` (v3.8.50 no longer exposes version to unauthenticated callers — GHSA-mvf8-qc78-5mxm) |
| `HEAD 127.0.0.1:20128/v1/models` | HTTP 200 (public availability probe) |
| `GET 127.0.0.1:20128/v1/models` (anonymous) | HTTP 401 (`Authentication required` — v3.8.50 flipped model-catalog auth from opt-in to opt-out) |
| `GET 127.0.0.1:20128/v1/models` (authenticated, in-container) | HTTP 200, 965 models (`auto/best-coding` first) |

### SQLite (post)

| Indicator | Value | Change from pre-state |
|---|---|---|
| `PRAGMA integrity_check` | `ok` | unchanged |
| Table count (non-internal) | 131 | +15 (v3.8.50 migrations) |
| `api_keys` | 1 | unchanged (>= pre-state) |
| `provider_connections` | 12 | unchanged (>= pre-state) |

### Invariant checklist

| Invariant | Value |
|---|---|
| Published ports | `127.0.0.1:20128`, `127.0.0.1:20129`, `127.0.0.1:20132` (loopback only) |
| Data volume | named `omniroute-data` → `/app/data` (not a bind mount) |
| Redis image | `docker.io/library/redis:7-alpine` (unchanged — not bumped to 8.x) |
| Redis published ports | none |
| SOCKS5 proxy | `ENABLE_SOCKS5_PROXY=false`, `NEXT_PUBLIC_ENABLE_SOCKS5_PROXY=false` |
| Update flag | `~/.omniroute/update-available` — ABSENT (cleared by updater) |

### Rollback preservation

| Artifact | Path/ID | Status |
|---|---|---|
| Pre-upgrade snapshot (first attempt) | `~/.omniroute/snapshots/pre-update-20260828-075010.sqlite` | integrity=ok, WAL sidecars removed (self-contained) |
| v3.8.49 rollback tag | `omniroute:rollback-3.8.49-20260828-075010` → image id `420570109d69` | PRESERVED (the real rollback point) |
| Final verified snapshot | `~/.omniroute/snapshots/pre-update-20260828-081810.sqlite` | integrity=ok (verification-run snapshot) |
| Old v3.8.49 image | `sha256:420570109d69b68d…` | PRESERVED (not pruned) |

### Fail-closed events

1. **First attempt (07:52)**: Gate 8 failed — `monitoring version '' != 3.8.50`. Root cause: v3.8.50 (GHSA-mvf8-qc78-5mxm) changed the monitoring endpoint to return only `{status, setupComplete}` to unauthenticated callers. Flag retained. No false success.

2. **Second attempt (07:56)**: Gate 8 failed — `GET /v1/models returned HTTP 401`. Root cause: v3.8.50 flipped model-catalog auth from opt-in (`requireAuthForModels !== true`) to opt-out (`=== false`). Flag retained. No false success.

3. **Final attempt (08:18)**: ALREADY_TARGET verification run. All gates passed. Flag cleared. The `update.sh` script was rewritten between attempts 2 and 3 to handle both contract changes; the ALREADY_TARGET idempotency path skipped container recreation (already on target) and continued to full verification.

### Updater hardening applied

The `~/Omniroute/scripts/update.sh` was rewritten from a warn-and-continue script (93 lines, zero fail-closed gates) to a fail-closed gate chain (303 lines, 11 gates + ALREADY_TARGET path). Changes:
- 10 sequential verification gates (preflight → snapshot → pull → digest → deploy → healthy → version → image-id → endpoints → post-deploy-data)
- Flag retained on ANY gate failure; flag cleared ONLY after gate 9 passes
- ERR trap + `trap - ERR` in `fail()` prevents recursion
- Health failure dumps container health JSON + last 200 log lines
- Service-targeted compose commands (`--no-deps --force-recreate omniroute-base`) — Redis container never touched
- Rollback tag created before deploy; snapshot integrity checked twice (live DB + host copy)
- Version gate is retry-safe (equality with pre-state = verification retry, not failure)
- v3.8.50 model-catalog auth contract built into gate 8 (anonymous 401 → authenticated in-container probe → 200 with catalog)

# Evidence — Upgrade OmniRoute to v3.8.51

## §1 Pre-upgrade baseline (captured 2026-10-03)

### Runtime state

| Item | Value |
|---|---|
| Container | `omniroute` — running, health `healthy`, started `2026-10-01T06:48:05.512865387Z` |
| Container ID | `8aa33258725fc88e3776db9002a2c48a8aad6f19732e15822867c709a64d655a` |
| App version (`/app/package.json`) | `3.8.50` |
| Container image ID | `sha256:8864a9d6985cb99f11245b0cd677c6f3516bc7cf0e72a817359fa47cd3ba9bc7` |
| `latest` RepoDigest (local) | `diegosouzapw/omniroute@sha256:085c57adf499a8aaa9f35ccde95c0df9c11bd9ecd18d6c9edbf3b68b8079ba9d` |
| NODE_OPTIONS | `--max-old-space-size=2048` |
| Redis container | `omniroute-redis`, `docker.io/library/redis:7-alpine`, healthy, no host-published ports (`{"6379/tcp":null}`) |

### Target

| Item | Value |
|---|---|
| Target version | `3.8.51` (GitHub release published 2026-09-30T01:41:50Z) |
| Target index digest (Docker Hub `latest` = `3.8.51`) | `sha256:8bd462c9f60d8eda79329cfbb6ea7ea723505fe7721beb944f3d43835409e218` |
| Update flag | `~/.omniroute/update-available`, written 2026-09-30 13:50:21 by LaunchAgent `com.omniroute.update-check`, content = target digest |

### Endpoints (pre)

| Probe | Result |
|---|---|
| `GET 127.0.0.1:20128/healthz` | `ok` |
| `GET 127.0.0.1:20128/` | HTTP 307 (redirect to login) |
| `GET 127.0.0.1:20128/api/monitoring/health` | 200, `{"status":"healthy","setupComplete":true}` |
| `HEAD 127.0.0.1:20128/v1/models` | HTTP 200 |
| `GET 127.0.0.1:20128/v1/models` (anonymous) | HTTP 401 (catalog auth enabled / opt-out posture) |
| Authenticated in-container `GET /v1/models` | HTTP 200, count=1034 models |

### SQLite baseline (in-container, readonly)

| Indicator | Value |
|---|---|
| `PRAGMA integrity_check` | `ok` |
| Table count (non-internal) | 133 |
| `api_keys` | 1 |
| `provider_connections` | 19 |

### Rendered Compose invariants (pre)

| Invariant | Value |
|---|---|
| `omniroute-base` image | `diegosouzapw/omniroute:latest` |
| Published ports | `127.0.0.1:20128`, `127.0.0.1:20129`, `127.0.0.1:20132` (loopback only) |
| Data volume | named `omniroute-data` → `/app/data` |
| Redis image | `docker.io/library/redis:7-alpine` |
| Redis published ports | none |

---

## §2 Post-upgrade verification (captured 2026-10-03 22:08 +07)

### Runtime state (post)

| Item | Value |
|---|---|
| Container | `omniroute` — running, health `healthy` |
| App version (`/app/package.json`) | `3.8.51` |
| Container image ID | `sha256:8ac4e82973a3f687564ca4f1cafe9ad528fae9d319eecf526c78ae91f7cea05a` |
| Pulled image ID | `sha256:8ac4e82973a3f687564ca4f1cafe9ad528fae9d319eecf526c78ae91f7cea05a` (exact match) |
| `latest` RepoDigest (local) | `diegosouzapw/omniroute@sha256:8bd462c9f60d8eda79329cfbb6ea7ea723505fe7721beb944f3d43835409e218` (matches target) |
| NODE_OPTIONS | `NODE_OPTIONS=--max-old-space-size=2048` |
| Redis container | `omniroute-redis`, `docker.io/library/redis:7-alpine`, healthy, no host-published ports (`{"6379/tcp":null}`) |
| SOCKS5 Proxy config | `ENABLE_SOCKS5_PROXY=false`, `NEXT_PUBLIC_ENABLE_SOCKS5_PROXY=false` |
| Update flag | `~/.omniroute/update-available` removed (verified absent) |
| Backup snapshot | `~/.omniroute/snapshots/pre-update-20261003-220431.sqlite` (2,198,044,672 bytes, host integrity check ok) |

### Endpoints (post)

| Probe | Result |
|---|---|
| `GET 127.0.0.1:20128/healthz` | `ok` |
| `GET 127.0.0.1:20128/` | HTTP 307 |
| `GET 127.0.0.1:20128/api/monitoring/health` | 200, `{"status":"healthy","setupComplete":true}` |
| `HEAD 127.0.0.1:20128/v1/models` | HTTP 200 |
| `GET 127.0.0.1:20128/v1/models` (anonymous) | HTTP 401 |
| Authenticated in-container `GET /v1/models` | HTTP 200, count=981 models |

### SQLite data integrity (post)

| Indicator | Pre-upgrade | Post-upgrade | Status |
|---|---|---|---|
| `PRAGMA integrity_check` | `ok` | `ok` | PASSED |
| Table count (non-internal) | 133 | 140 | PASSED (34 migrations applied successfully) |
| `api_keys` | 1 | 1 | PASSED (>= baseline 1) |
| `provider_connections` | 19 | 20 | PASSED (>= baseline 19) |

### Rendered Compose invariants (post)

| Invariant | Configured / Observed | Status |
|---|---|---|
| Loopback port 20128 | `127.0.0.1:20128` | PASSED |
| Loopback port 20129 | `127.0.0.1:20129` | PASSED |
| Loopback port 20132 | `127.0.0.1:20132` | PASSED |
| Persistence volume | `omniroute-data` on `/app/data` | PASSED |
| Redis unpublished | `{"6379/tcp":null}` | PASSED |

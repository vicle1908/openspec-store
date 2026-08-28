# Design — Upgrade OmniRoute to v3.8.50

## D1: Image-based runtime upgrade, not source compilation

The deployment mechanism standardized on 2026-08-24
(`standardize-omniroute-docker-deployment`) runs the pre-built Docker Hub
image `diegosouzapw/omniroute:latest` from `~/Omniroute` with `--profile
base`. The upgrade therefore is service-targeted (Redis is never pulled or
recreated — its 8.6.5 bump is explicitly deferred, D3):

```
docker compose --profile base pull omniroute-base
docker compose --profile base up -d --no-build --pull never \
  --no-deps --force-recreate omniroute-base
```

`--pull never` prevents a digest-changing registry race between the digest
gate and deployment; `--force-recreate` guarantees the container switches to
the pulled image even when Compose considers config unchanged.

The `~/Omniroute` git checkout is NOT pulled: it has unrelated local
modifications (`.source/dynamic.ts`, `package-lock.json`) and untracked
deployment infrastructure (`docker-compose.override.yml`, `scripts/`). The
local compose files stay as-is; only the image changes. This keeps the
mutation surface to exactly one artifact: the `latest` image.

## D2: Fail-closed updater (the core hardening)

The existing `update.sh` treats every failure as a warning and always ends in
"success" — clearing the flag and notifying. That defeats the purpose of the
update-tracking system: after a failed upgrade nobody would know an update was
still pending. The hardened script is a linear gate chain; ANY failure exits
nonzero, retains the flag, logs the failed gate, and sends a failure
notification:

| # | Gate | Failure mode it catches |
|---|------|--------------------------|
| 0 | Flag file present | Running with no flagged update (exits 0, no-op) |
| 1 | Live DB `integrity_check` = ok AND snapshot backup + copy to host succeeds | Upgrading over a corrupt DB; losing the rollback point |
| 2 | `docker compose pull omniroute-base` exit 0 | Network/registry failures (service-targeted: redis untouched) |
| 3 | Pulled `latest` RepoDigest == flagged target digest | Registry republish/race; deploying an unintended build |
| 4 | `docker compose up -d --no-build --pull never --no-deps --force-recreate omniroute-base` exit 0 | Container recreation failure; `--pull never` closes the digest race, `--force-recreate` guarantees image switch |
| 5 | Health status `healthy` within 5 min | Boot loop, migration crash, start-period exhaustion |
| 6 | `/app/package.json` version == expected version (arg) | Deploying the wrong image. Retry-safe: if it equals the pre-state version this is logged as a verification retry of a prior partial run, NOT failed — otherwise a failed late gate on attempt 1 would deadlock every retry |
| 7 | Running container `.Image` id == pulled `latest` image id | Container not actually recreated on new image |
| 8 | `/healthz` = `ok`; dashboard 200/307; `/api/monitoring/health` status healthy + `setupComplete=true`; `/v1/models` = 200 | App up but degraded endpoints. NOTE: v3.8.50 (GHSA-mvf8-qc78-5mxm) returns only `{status, setupComplete}` to unauthenticated callers — the version field is no longer public; gate 6 is the authoritative version check |
| 9 | Post-deploy DB `integrity_check` = ok AND `api_keys` / `provider_connections` >= pre-state baseline | Data loss / volume not reattached |

Only after gate 9 does the script clear the flag and notify success.

Design notes:

- `call_logs` is deliberately NOT compared for equality — it grows naturally.
  `api_keys` and `provider_connections` are compared against the baseline
  captured at pre-state (>= baseline), not against fixed constants.
- The expected version is passed as `$1` (this run: `3.8.50`) so the script
  stays generic for future updates while this upgrade pins the exact version.
- Pre-state (old image ID + old version) is logged before pull as rollback
  evidence; the old image is additionally tagged
  `omniroute:rollback-<oldver>-<ts>` before the pull so rollback never
  depends on image-store luck.
- `fail()` disables the ERR trap first (`trap - ERR`) so an explicit gate
  failure cannot also fire the generic unexpected-error handler.
- Snapshot integrity is checked twice: on the live DB before backup (in
  container) and on the host-side snapshot copy via `sqlite3 PRAGMA
  integrity_check` (host sqlite3 is a required preflight).

## D3: Redis stays on 7-alpine (deferred)

Upstream v3.8.50 compose bumps `redis:7-alpine` → `redis:8.6.5-alpine` and
changes the published-port default to loopback. We do not `git pull` the
checkout (D1), so the rendered compose keeps `redis:7-alpine`, and our
override already resets Redis ports to unpublished — the upstream loopback
hardening is moot here. A Redis major upgrade (data-format/RDB compatibility,
`redis-data` volume migration) is a separate, deliberate change.

## D4: Spec drift correction via MODIFIED delta

`bifrost-gateway` (canonical) predates the 2026-08-24 standardization:

- **Persistence requirement** says bind mount `~/Omniroute/data` → `/app/data`.
  Reality since 2026-08-24: named volume `omniroute-data` → `/app/data`,
  because Docker Desktop for Mac virtiofs bind mounts corrupt SQLite WAL DBs
  (OmniRoute hardcodes WAL). Redis uses named volume `omniroute-redis-data`
  and is not host-published.
- **Healthcheck requirement** quotes upstream timing (5s timeout, 15s start).
  Reality: the deployment override relaxes this to 15s timeout / 120s start
  because upstream's 5s timeout false-positives during background
  model/credential sync while the app remains functional. The v3.8.50 image
  still ships the same `node healthcheck.mjs` command with upstream timing,
  so the override remains necessary and valid.

Both are MODIFIED in the delta (full requirement replacement). A new ADDED
requirement codifies the fail-closed upgrade contract so future upgrades are
spec-bound, not just script behavior.

## D5: Rollback plan

1. Pre-update snapshot: `~/.omniroute/snapshots/pre-update-<ts>.sqlite`
   (gate 1 artifact).
2. Old image ID logged by `update.sh` before pull; the old image remains in
   the local image store after pull (not pruned).
3. Rollback procedure if needed (exact, logged by the updater on success):
   `docker tag omniroute:rollback-<oldver>-<ts> diegosouzapw/omniroute:latest`
   then `docker compose --profile base up -d --no-build --pull never
   --no-deps --force-recreate omniroute-base`; restore the snapshot into the
   `omniroute-data` volume ONLY as a last resort if v3.8.50 startup
   migrations broke forward-compat (v3.8.50 is a patch release; migrations
   are expected to be forward-only-safe). Old image and rollback tag are NOT
   pruned during this change.

## D6: Verification plan

- Baseline evidence captured BEFORE mutation (version, digests, image IDs,
  health, endpoints, rendered compose invariants, SQLite integrity + counts)
  into `evidence.md`.
- The hardened updater provides gate-by-gate evidence in
  `~/.omniroute/update.log`.
- Independent post-upgrade checks re-verify everything the updater checked
  plus invariant checks (loopback bindings, volume layout, Redis
  unpublished, SOCKS5=false) via rendered compose config — not just the
  updater's own claims.

## Risks

- **DB migrations at startup**: v3.8.50 includes several migration-collision
  fixes from the release cycle; migrations run automatically at boot. Snapshot
  gate is the safety net; expected impact is nil for a patch release.
- **Image size growth**: 3.8.50 image ≈ 1.24 GB (vs 483 MB for 3.8.49).
  Docker VM has ~610 GB free — no capacity concern. Old image retained for
  rollback; prune is a later cleanup decision.
- **`/v1/models` catalog change**: health-check-excluded models are now
  hidden (#10026). Consumers may see a slightly smaller catalog — intended
  upstream behavior, no consumer breakage expected (combo models like
  `auto/best-coding` remain).

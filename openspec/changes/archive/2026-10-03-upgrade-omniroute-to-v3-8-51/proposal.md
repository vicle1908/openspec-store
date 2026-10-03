# Upgrade OmniRoute to v3.8.51

## Problem Statement

The deployed OmniRoute runtime is v3.8.50 (image RepoDigest `sha256:085c57adf499a8aaa9f35ccde95c0df9c11bd9ecd18d6c9edbf3b68b8079ba9d`) while upstream released v3.8.51 on 2026-09-30. Docker Hub `latest` and `3.8.51` tags both resolve to index digest `sha256:8bd462c9f60d8eda79329cfbb6ea7ea723505fe7721beb944f3d43835409e218`. The update-tracking LaunchAgent (`com.omniroute.update-check`) flagged the new version on 2026-09-30 13:50 and wrote `~/.omniroute/update-available`.

## Why

Upstream release v3.8.51 delivers 2,022 documented changes (235 features, 1,454 fixes, 333 chores across 1,972 commits) including vital runtime stability enhancements:
- Hardened loopback port publishing defaults in upstream `docker-compose.yml` (`APP_BIND_HOST:-127.0.0.1`), aligning upstream with our workstation deployment standards.
- Deep health-check caching and performance optimizations for `/api/monitoring/health`.
- Updated provider models and aliases across the ecosystem.
- Upstream and local `.env` compatibility: all 64 variables currently set in `~/Omniroute/.env` remain fully valid, with zero deprecations or removals affecting the deployment.

Upgrading ensures the local AI gateway remains current with upstream bug fixes, dependency patches, and catalog improvements while maintaining our strict fail-closed deployment invariants.

## What Changes

- **Upgrade the OmniRoute runtime from v3.8.50 to v3.8.51** via the Docker Hub image using our fail-closed script: `~/Omniroute/scripts/update.sh 3.8.51`.
- **Preserve all deployment invariants**:
  - Loopback-only port bindings: 20128 (dashboard), 20129 (API bridge), 20132 (LiveWS) bound strictly to `127.0.0.1`.
  - Persistence: SQLite database on Docker named volume `omniroute-data` mounted at `/app/data` (no bind mounts).
  - Rate limiting & Redis: `redis:7-alpine` container on the private compose network, unpublished to the host.
  - Proxy configuration: SOCKS5 proxy flags remain disabled (`ENABLE_SOCKS5_PROXY=false`).
  - Runtime environment: `NODE_OPTIONS=--max-old-space-size=2048` preserved via `docker-compose.override.yml`.
- **Pass all 10 fail-closed update gates**:
  - Gate 0: update flag present (`~/.omniroute/update-available`).
  - Gate P: preflight checks (Docker, SQLite3, compose config, container present).
  - Gate 1: live SQLite `integrity_check=ok`, in-container backup, host-side verification, WAL sidecar consolidation.
  - Gate 2: service-targeted pull (`omniroute-base` only; Redis untouched).
  - Gate 3: pulled RepoDigest matches target digest `sha256:8bd462c9...`.
  - Gate 4: recreate container with `--no-build --pull never --no-deps --force-recreate`.
  - Gate 5: healthy within 5 minutes.
  - Gate 6: in-image `/app/package.json` version equals `3.8.51`.
  - Gate 7: running container `.Image` matches pulled image ID.
  - Gate 8: verify endpoints (`/healthz=ok`, dashboard 200/307, `/api/monitoring/health` status healthy + `setupComplete=true`, `HEAD /v1/models=200`, authenticated in-container `GET /v1/models=200`).
  - Gate 9: post-deploy SQLite integrity check `ok`, `api_keys` and `provider_connections` at or above captured baseline (1 key, 19 connections).
- **Clear update flag and update store configuration**:
  - `~/.omniroute/update-available` cleared upon successful verification.
  - Record v3.8.51, upgrade date, and image digest in `platform/openspec-store/openspec/config.yaml`.

## Non-Goals

- **No Redis major-version upgrade**: Redis remains pinned to `redis:7-alpine`. Upstream compose ships `redis:8.6.5-alpine`; any Redis version upgrade is a separate infrastructure change.
- **No git pull in `~/Omniroute`**: The checkout carries untracked overrides (`docker-compose.override.yml`, `scripts/`) and local modifications; the deployment is strictly container-image based.
- **No changes to `.env`**: All 64 active keys remain valid without modification.
- **No new Compose profiles**: Profiles such as `web`, `cli`, `bifrost`, `memory`, and `codex-app-server` remain disabled.
- **No bind-mount storage**: Docker named volume `omniroute-data` is strictly retained to prevent SQLite WAL corruption.

## Affected Ownership

- **Platform Engineering**: Owns OmniRoute deployment, operational health, and OpenSpec store records.
- **Deployment Root**: `~/Omniroute` (untracked operational scripts and compose overrides).
- **Store Root**: `platform/openspec-store` (OpenSpec tracking and store configuration).

## Capabilities

### New Capabilities

None.

### Modified Capabilities

None.

**skip_specs: true** — Operational runtime patch upgrade with zero behavioral contract modifications. Canonical specification `specs/bifrost-gateway/spec.md` already defines fail-closed evidence-gated image upgrades, named volume persistence, loopback isolation, opt-out model catalog authentication, and healthcheck timing; all requirements remain fully governing and satisfied without modification.

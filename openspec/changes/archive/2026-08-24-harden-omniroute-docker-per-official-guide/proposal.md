## Problem Statement

The OmniRoute Docker deployment (established by `standardize-omniroute-docker-deployment`) diverged from the official installation guide on two hardening points: the production-required `OMNIROUTE_WS_BRIDGE_SECRET` was unset (auto-generated per boot), and all three ports were bound to `0.0.0.0` (all interfaces) instead of the official hardened loopback pattern.

## Why

A comparison against the official sources (README, `docs/guides/DOCKER_GUIDE.md`, official `docker-compose.yml`, omniroute.online) found the deployment aligned on data storage (named volume), stop timeout (40s), REDIS_URL, API_PORT, and auto-backup — but two gaps remained:

1. **`OMNIROUTE_WS_BRIDGE_SECRET`**: the official Docker guide marks this "**Required in production** — set to a strong random string". Ours was commented out, so the container auto-generated it via `randomUUID()` on every boot (not persisted). This violates the explicit official guidance and means the secret changes on every restart.
2. **Port binding**: the official README quick-run (`docker run ... -p 127.0.0.1:20128:20128 ...`) and the VM deployment guide both expose the app on **loopback** (`127.0.0.1`), not all interfaces. Ours published 20128/20129/20132 on `0.0.0.0`, reachable from any LAN device.

## What Changes

- **Set `OMNIROUTE_WS_BRIDGE_SECRET`** to a stable strong random value (64-hex) in `~/Omniroute/.env`, per the official "required in production" guidance.
- **Bind all three ports to loopback** (`127.0.0.1`) via `ports: !override` in `docker-compose.override.yml`, matching the official hardened pattern (README quick-run + VM guide).
- **Verify**: WS secret present in the running container; ports bound to `127.0.0.1` only; dashboard/login/API functional; unreachable from the LAN IP.

## Non-Goals

- No change to data storage, Redis wiring, or the named-volume approach (all already match official).
- No provider or application changes.
- No reverse-proxy / TLS setup (the VM guide's nginx/Caddy path) — loopback binding is the chosen local hardening; a reverse proxy is a separate future concern if remote access is ever needed.

## Capabilities

### New Capabilities

None — hardening/config change only.

### Modified Capabilities

None — no spec-level behavior changes.

**skip_specs: true** — Pure deployment hardening. No API contracts, user-facing behavior, or spec-level requirements change.

## Impact

- **`~/Omniroute/.env`** (gitignored): `OMNIROUTE_WS_BRIDGE_SECRET` set to a stable strong secret.
- **`~/Omniroute/docker-compose.override.yml`** (untracked, deployment-owned): adds loopback `ports: !override` for 20128/20129/20132.
- **Runtime**: same compose `base` profile; ports now loopback-only; WS bridge secret stable across restarts.
- **Access**: OmniRoute is now reachable only from the local Mac (127.0.0.1), not from other LAN devices.

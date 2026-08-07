# Proposal: Setup OmniRoute Persistent

## Why

OmniRoute is installed at `~/Omniroute` (v3.8.49) but not running. The installation has:
- Full `node_modules` (3.7G)
- `.env` configured with secrets, port 20128
- Docker Compose with `restart: unless-stopped` policies
- Docker Desktop v29.6.2 with Compose v5.3.1

Currently nothing listens on ports 20128/20129/20132/6379. OmniRoute needs to be running persistently so it survives macOS system restarts without manual intervention.

## What Changes

1. **Build and start OmniRoute via Docker Compose** using the `base` profile (Redis + OmniRoute, no CLI tools inside container — CLI agents run from host).
2. **Verify Docker Desktop autostart** — ensure Docker Desktop launches on macOS login so containers auto-restart.
3. **Validate the running service** — confirm health endpoint, dashboard accessibility, and provider catalog load.
4. **Document the setup** — persistence approach and manual recovery steps.

**Out of scope:**
- No spec delta (`skip_specs: true`) — this is infrastructure/config only.
- No code changes to OmniRoute source.
- No production deployment (uses local Docker Compose).

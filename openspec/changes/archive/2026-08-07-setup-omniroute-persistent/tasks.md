# Tasks: Setup OmniRoute Persistent

## Phase 1: Docker Build & Start

- [x] 1.1 Pull OmniRoute Docker image (`docker pull diegosouzapw/omniroute:latest`) — used pre-built image instead of building from source (build timed out at 600s)
- [x] 1.2 Tag image for compose compatibility (`docker tag diegosouzapw/omniroute:latest omniroute:base`)
- [x] 1.3 Start OmniRoute + Redis (`docker compose --profile base up -d --no-build`)

## Phase 2: Service Validation

- [x] 2.1 Verify containers healthy — both `omniroute` and `omniroute-redis` report `(healthy)`
- [x] 2.2 Verify dashboard responds — `localhost:20128` returns HTTP 307 → `/dashboard`
- [x] 2.3 Verify API models endpoint — `localhost:20129/v1/models` returns 115 models
- [x] 2.4 Verify Redis — `localhost:6379` responding, health check passes

## Phase 3: Persistence Verification

- [x] 3.1 Docker Desktop AutoStart: `True` in settings-store.json — daemon starts on macOS login
- [x] 3.2 Restart policies: both containers have `restart: unless-stopped`
- [x] 3.3 Manual restart test: restarted `omniroute-base` service, container recovered and healthy within 10s

## Phase 4: Documentation

- [x] 4.1 Startup command: `cd ~/Omniroute && docker compose --profile base up -d --no-build`
- [x] 4.2 Shutdown command: `cd ~/Omniroute && docker compose --profile base down`
- [x] 4.3 Logs: `cd ~/Omniroute && docker compose --profile base logs -f`
- [x] 4.4 Manual recovery: if containers don't auto-start, run step 4.1

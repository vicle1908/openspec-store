# Tasks: OmniRoute Docker Compose

## Phase 1: Setup

- [x] 1.1 Pull OmniRoute image from Docker Hub (`docker compose --profile base pull`)
- [x] 1.2 Create `docker-compose.override.yml` to override image to `diegosouzapw/omniroute:latest`
- [x] 1.3 Configure single-port mode in `.env` (`API_PORT=20128`, `LIVE_WS_PORT=20128`, `DASHBOARD_PORT=20128`)

## Phase 2: Start & Validate

- [x] 2.1 Start services (`docker compose --profile base up -d --no-build --force-recreate`)
- [x] 2.2 Verify containers healthy — both report `(healthy)`
- [x] 2.3 Verify single port: `localhost:20128` only (no 20129/20132)
- [x] 2.4 Verify dashboard (`localhost:20128` → HTTP 307)
- [x] 2.5 Verify API (`localhost:20128/v1/models` → 115 models)
- [x] 2.6 Verify Redis (`localhost:6379` responding)
- [x] 2.7 Verify login with existing password (`31122019` → OK)
- [x] 2.8 Verify old ports are dead (20129, 20132 unreachable)

## Phase 3: Persistence

- [x] 3.1 Confirm bind mount (`~/Omniroute/data` → `/app/data`, RW=True)
- [x] 3.2 Confirm restart policy (`unless-stopped` on both containers)
- [x] 3.3 Confirm Docker Desktop AutoStart (`settings-store.json` → `AutoStart: True`)

## Phase 4: Archive

- [x] 4.1 Update OpenSpec change artifacts
- [x] 4.2 Validate OpenSpec change
- [x] 4.3 Archive change
- [x] 4.4 Commit store

# Tasks: OmniRoute Docker Compose

## Phase 1: Setup

- [x] 1.1 Pull OmniRoute image from Docker Hub (`docker compose --profile base pull`)
- [x] 1.2 Create `docker-compose.override.yml` to override image to `diegosouzapw/omniroute:latest`
- [x] 1.3 Verify override merges correctly (`docker compose --profile base config`)

## Phase 2: Start & Validate

- [x] 2.1 Start services (`docker compose --profile base up -d --no-build`)
- [x] 2.2 Verify containers healthy — both report `(healthy)`
- [x] 2.3 Verify dashboard (`localhost:20128` → HTTP 307 → `/dashboard`)
- [x] 2.4 Verify API (`localhost:20129/v1/models` → 115 models)
- [x] 2.5 Verify Redis (`localhost:6379` responding)
- [x] 2.6 Verify login with existing password (`31122019` → OK)

## Phase 3: Persistence

- [x] 3.1 Confirm bind mount (`~/Omniroute/data` → `/app/data`, RW=True)
- [x] 3.2 Confirm restart policy (`unless-stopped` on both containers)
- [x] 3.3 Confirm Docker Desktop AutoStart (`settings-store.json` → `AutoStart: True`)

## Phase 4: Cleanup & Archive

- [x] 4.1 Remove old tag hack image (`docker rmi omniroute:base`)
- [x] 4.2 Update OpenSpec change artifacts
- [x] 4.3 Validate OpenSpec change
- [x] 4.4 Archive change
- [x] 4.5 Commit store

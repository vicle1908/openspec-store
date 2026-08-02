## 1. Setup

- [x] 1.1 Create `deployments/bifrost/` directory
- [x] 1.2 Create `deployments/bifrost/docker-compose.yml` with Bifrost service (image: `maximhq/bifrost:latest`, port: `127.0.0.1:8180:8080`, volume: `${HOME}/.tdt/bifrost:/app/data`, healthcheck: `GET /health`, restart: unless-stopped)
- [x] 1.3 Create `~/.tdt/bifrost/` directory for persistent data

## 2. Deploy & Verify

- [x] 2.1 Pull Bifrost image: `docker pull maximhq/bifrost`
- [x] 2.2 Start service: `cd deployments/bifrost && docker compose up -d`
- [x] 2.3 Verify health: `curl http://localhost:8180/health` returns `{"status":"ok"}`
- [x] 2.4 Verify Docker health status: `docker inspect --format='{{.State.Health.Status}}'` returns `healthy`
- [x] 2.5 Verify Web UI loads: `curl -s http://localhost:8180/ | head -1` returns HTML
- [x] 2.6 Verify loopback binding: `lsof -iTCP:8180 -sTCP:LISTEN` shows `127.0.0.1:8180`

## 3. Smoke Test

- [x] 3.1 Verify `/v1/models` endpoint: `curl http://localhost:8180/v1/models` returns `{"data":[]}`
- [x] 3.2 Open Web UI at `http://localhost:8180/` and confirm dashboard loads
- [x] 3.3 Verify persistent data: check `~/.tdt/bifrost/config.db` exists after first startup

## 4. Documentation

- [x] 4.1 Update `docs/operations/docker-compose-deployment.md` to add Bifrost service row (port 8180, health endpoint `/health`)

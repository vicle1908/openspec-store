# Tasks: containerize-claude-code-provider-adapter

## Phase 1: Docker Build Infrastructure

### 1A: Dockerfile
- [x] 1A.1 Write `Dockerfile`: multi-stage build, Python 3.14-slim, uv 0.12.3 via `COPY --from=ghcr.io/astral-sh/uv:0.12.3`, hatchling builder, non-root user
- [x] 1A.2 Builder copies `pyproject.toml`, `uv.lock`, `README.md`, `src/`; runtime copies `.venv`, `src/`, `README.md`
- [x] 1A.3 `docker build` succeeded

### 1B: Docker Compose
- [x] 1B.1 Write `docker-compose.yml`: adapter service, `restart: unless-stopped`, port `127.0.0.1:8787:8787`, `env_file: .env`, health check against `/health`
- [x] 1B.2 Compose overrides: `ADAPTER_HOST=0.0.0.0`, `COCKPIT_UPSTREAM_URL=http://host.docker.internal:51006/v1/responses`
- [x] 1B.3 `docker compose config` parses without errors

### 1C: Environment
- [x] 1C.1 Created `.env.example` with `HERMES_CUSTOM_COCKPIT_API_KEY=` placeholder
- [x] 1C.2 Added `.env` to `.gitignore`
- [x] 1C.3 Compose fails fast if `.env` missing — user must `cp .env.example .env` first

## Phase 2: Host Connectivity Verification

- [x] 2.1 Verified `host.docker.internal:51006` TCP reachability from container:
  `docker run --rm python:3.14-slim python -c "urllib.request.urlopen(...)"` → HTTP 401 (auth expected, TCP proven)
- [x] 2.2 cockpit is native macOS process (PID 64609, `cockpit-cli`), not Docker — no loopback binding issue on macOS Docker Desktop
- [x] 2.3 Documented: `host.docker.internal` is macOS Docker Desktop only; Linux needs `extra_hosts: host.docker.internal:host-gateway`

## Phase 3: Implementation

### 3A: Build and start
- [x] 3A.1 `docker compose build` succeeded (image: 179MB)
- [x] 3A.2 `docker compose up -d` started container
- [x] 3A.3 `curl http://127.0.0.1:8787/health` returned 200: `{"status":"ok","adapter":"claude-code-provider-adapter"}`
- [x] 3A.4 `docker compose ps` showed adapter as `healthy`

### 3B: Acceptance — real cockpit through container
- [x] 3B.1 Non-streaming text: `gpt-5.6-luna`, output `DOCKER_TEXT_OK`, `type=message`, `stop=end_turn`
- [x] 3B.2 Streaming: SSE events `message_start → content_block_start → content_block_delta×4 → content_block_stop → message_delta → message_stop`
- [x] 3B.3 Tool-use: `stop_reason: tool_use`, `tool_use` block with `test_tool`, `call_` prefixed ID, `input={'msg': 'hello'}`
- [x] 3B.4 System prompt: `system="You are a pirate"` → response contains `ARRR` (system instruction followed)
- [x] 3B.5 `docker compose down` stops cleanly

### 3C: Restart behavior
- [x] 3C.1 `docker compose restart` → container restarted, `/health` returned 200 within 3 seconds
- [x] 3C.2 Documented: `restart: unless-stopped` requires first `docker compose up -d` — does NOT autostart on Docker Desktop launch

## Phase 4: Shell Launcher Integration

- [x] 4.1 Added `cockpit_up()` function to `~/.zshrc`: runs `docker compose up -d` in adapter repo
- [x] 4.2 Added `cockpit_down()` function to `~/.zshrc`: runs `docker compose down`
- [x] 4.3 Shell syntax verified with `zsh -n ~/.zshrc` → PASS

## Phase 5: Cleanup and Documentation

- [x] 5.1 `.env` gitignored, `.dockerignore` excludes `.env` and `tests/`, no secrets in image
- [x] 5.2 `uv run pytest` remains green (no source changes)
- [x] 5.3 Updated adapter repo `README.md` with Docker usage section
- [x] 5.4 `openspec validate containerize-claude-code-provider-adapter --store openspec-store`
- [x] 5.5 `git commit` both repos

## Known Limitations

- `restart: unless-stopped` does NOT create a container that has never been started. First run requires `docker compose up -d` (or `cockpit_up`).
- `host.docker.internal` is macOS Docker Desktop only. Linux needs `extra_hosts: host.docker.internal:host-gateway` in compose.
- Docker Desktop must have "Start Docker Desktop when you log in" enabled for login-time startup.
- If Docker Desktop is not running, adapter is unavailable. Fallback: `uv run claude-code-provider-adapter` (local process).

## Rollback

- [x] R.1 `docker compose down` stops adapter
- [x] R.2 Remove `Dockerfile`, `docker-compose.yml`, `.env`, `.env.example`
- [x] R.3 Remove `cockpit_up` / `cockpit_down` from `~/.zshrc`
- [x] R.4 Local `uv run claude-code-provider-adapter` continues to work

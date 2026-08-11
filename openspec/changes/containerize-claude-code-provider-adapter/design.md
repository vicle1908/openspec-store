# Design: containerize-claude-code-provider-adapter

## Architecture

```
┌─────────────────────────────────────────────────┐
│  Docker (Compose)                               │
│                                                 │
│  claude-code-provider-adapter                   │
│  ┌─────────────────────────────────────────┐    │
│  │  python:3.14-slim + uv                  │    │
│  │  FastAPI on 0.0.0.0:8787                │    │
│  │  COCKPIT_UPSTREAM_URL =                 │    │
│  │    http://host.docker.internal:51006    │    │
│  └─────────────────────────────────────────┘    │
│            │ host.docker.internal                │
└────────────┼────────────────────────────────────┘
             │
    ┌────────▼────────────────────────────────┐
    │  host macOS                              │
    │  cockpit-cli (PID 64609) :51006          │
    └──────────────────────────────────────────┘
```

Cockpit is a native macOS process. The adapter container reaches it through Docker Desktop's `host.docker.internal` DNS resolution. No Docker networking changes needed — Docker Desktop for Mac handles this automatically.

## Dockerfile

Multi-stage build using `uv`:

```dockerfile
FROM python:3.14-slim AS builder
WORKDIR /app
COPY uv.lock pyproject.toml ./
COPY src/ src/
RUN pip install uv && uv sync --frozen --no-dev

FROM python:3.14-slim AS runtime
RUN addgroup --gid 1001 appgroup && adduser --uid 1001 --gid 1001 --no-create-home appuser
WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY src/ src/
ENV PATH="/app/.venv/bin:$PATH"
USER appuser
EXPOSE 8787
HEALTHCHECK --interval=30s --timeout=3s CMD python -c "import httpx; httpx.get('http://127.0.0.1:8787/health').raise_for_status()"
CMD ["python", "-m", "uvicorn", "claude_code_provider_adapter.app:app", "--host", "0.0.0.0", "--port", "8787"]
```

## docker-compose.yml

```yaml
services:
  adapter:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "127.0.0.1:8787:8787"
    env_file:
      - .env
    environment:
      - ADAPTER_HOST=0.0.0.0
      - COCKPIT_UPSTREAM_URL=http://host.docker.internal:51006/v1/responses
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "import httpx; httpx.get('http://127.0.0.1:8787/health').raise_for_status()"]
      interval: 30s
      timeout: 3s
      retries: 3
```

## .env.example

```bash
# Required: cockpit provider API key
HERMES_CUSTOM_COCKPIT_API_KEY=
```

## Key Design Decisions

1. **No config.py changes**: Compose injects `COCKPIT_UPSTREAM_URL` and `ADAPTER_HOST` via environment. Source defaults remain `127.0.0.1` for local dev.

2. **`restart: unless-stopped`**: Container restarts automatically when Docker Desktop restarts, but ONLY after the first `docker compose up -d`. Not autostart on login.

3. **Port binding**: `127.0.0.1:8787:8787` — only accessible from host, not network.

4. **Non-root**: Dockerfile creates `appuser` (UID 1001) and runs as that user.

5. **Health check**: Uses `httpx` (already a dependency) to hit `/health` — no extra packages needed.

6. **No `host.docker.internal` in source**: The default `COCKPIT_UPSTREAM_URL` in `config.py` stays `http://localhost:51006/v1/responses` for local dev. Compose overrides it.

## Shell Launcher Integration

Add `cockpit_up` / `cockpit_down` helpers:

```bash
cockpit_up() {
    (cd ~/Developer/claude-code-provider-adapter && docker compose up -d)
    echo "Adapter started. Check: curl http://127.0.0.1:8787/health"
}
cockpit_down() {
    (cd ~/Developer/claude-code-provider-adapter && docker compose down)
    echo "Adapter stopped."
}
```

The existing `cockpit()` function remains unchanged — it assumes port 8787 is already bound. The user must run `cockpit_up` first.

## Limitations

- `restart: unless-stopped` does NOT start a container that has never been started. First run requires `docker compose up -d`.
- If Docker Desktop is not running, the adapter is unavailable. No fallback to local process.
- Cockpit process on the host must be running for the adapter to function.

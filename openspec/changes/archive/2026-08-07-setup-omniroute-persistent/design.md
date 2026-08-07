# Design: Setup OmniRoute Persistent

## Architecture

```
macOS Login
  └─ Docker Desktop (Login Item)
       └─ docker compose up -d (restart: unless-stopped)
            ├─ redis:7-alpine  ──→  port 6379
            └─ omniroute:base  ──→  port 20128 (dashboard + API)
                                   port 20129 (API only)
                                   port 20132 (Live WS)
```

## Approach

### Option A: Docker Compose (selected)
- Uses existing `docker-compose.yml` with `--profile base`
- `restart: unless-stopped` policy handles container recovery
- Docker Desktop Login Item handles daemon startup on reboot
- Redis volume `redis-data` persists rate limit state
- Data volume `./data:/app/data` persists SQLite + config

### Option B: Next.js dev server (rejected)
- Requires `npm run dev` or `npm start` manually
- No built-in process supervision
- Would need launchd plist for persistence (more fragile than Docker)
- Doesn't match the Docker-first design of OmniRoute

## Trade-offs

| Factor | Docker Compose | Next.js direct |
|--------|---------------|----------------|
| Persistence | Automatic (Docker daemon) | Needs launchd |
| Resource usage | Higher (Docker overhead) | Lower |
| Updates | `docker compose pull && up -d` | `git pull && npm install && rebuild` |
| Complexity | Docker Desktop required | Node.js only |

Docker Compose is the right choice — OmniRoute is designed for it.

## Security Notes

- `.env` contains OAuth secrets and API keys — already present, not modified
- Ports bound to localhost by default (not exposed externally)
- Redis has no external port mapping in dev compose (internal only)
- `REQUIRE_API_KEY=false` in current .env — dashboard is open on localhost

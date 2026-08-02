## Why

The TDT ecosystem currently routes LLM requests through OmniRoute (`localhost:20128`), a third-party proxy with limited configuration flexibility. Bifrost is a high-performance, open-source AI gateway that provides a unified OpenAI-compatible API with automatic provider fallback, load balancing, semantic caching, and a built-in Web UI for configuration. Deploying Bifrost as a standalone service gives the ecosystem a modern LLM gateway that can later replace or complement OmniRoute, with first-class support for multi-provider routing and budget governance.

## What Changes

- **New Docker Compose deployment** for Bifrost at `deployments/bifrost/docker-compose.yml`
- **Persistent data directory** at `~/.tdt/bifrost/` (SQLite config DB, request logs, optional config.json seed)
- **Host port 8180** exposed on loopback only (consistent with existing service binding pattern)
- **Health check** via `GET /health` endpoint
- **No code changes** to existing TDT services — integration with agent-core, scheduler, etc. is a follow-up change

## Capabilities

### New Capabilities

- `bifrost-gateway`: Standalone Bifrost LLM gateway deployment — Docker Compose service with persistent storage, health checks, and Web UI for provider configuration

### Modified Capabilities

<!-- No existing capabilities are modified — this is a greenfield deployment -->

## Impact

- **Infrastructure**: New Docker Compose project at `deployments/bifrost/`
- **Storage**: `~/.tdt/bifrost/` directory created for persistence (config.db, logs.db)
- **Networking**: Port 8180 bound on loopback — no LAN exposure, no conflicts with existing services
- **Dependencies**: Bifrost Docker image (`maximhq/bifrost:latest`) — no new Python/Node dependencies
- **Existing services**: No changes to agent-core, scheduler, webhook-receiver, or ai-review
- **Future integration**: agent-core's `BifrostGateway` can later point to `http://localhost:8180` via `BIFROST_URL` env var

## Non-Goals

- Replacing OmniRoute — Bifrost runs alongside for evaluation
- Integrating with agent-core's compose stack — standalone first, compose merge later
- Provider key configuration — done via Web UI, not config files
- Multi-node clustering — single instance only
- Observability stack (Prometheus/Grafana) — can be added later

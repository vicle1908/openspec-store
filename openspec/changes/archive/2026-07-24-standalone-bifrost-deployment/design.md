## Context

The TDT ecosystem has multiple services that call LLM providers (OpenAI, nhà cung cấp dịch vụ AI, Ollama). Currently, OmniRoute (`localhost:20128`) serves as the LLM proxy, but it has limited configuration flexibility and no built-in UI. The `agent-core` SDK already includes a `BifrostGateway` class that reads `BIFROST_URL` and `BIFROST_API_KEY` from environment, but no Bifrost server is deployed.

Bifrost is an open-source AI gateway (Apache 2.0) written in Go, distributed as a single Docker image. It provides:
- OpenAI-compatible `/v1/chat/completions` endpoint
- Built-in Web UI for provider configuration (no config files required)
- SQLite-backed persistence (config.db, logs.db)
- Automatic provider fallback and load balancing
- Semantic caching, budget governance, virtual keys

This change deploys Bifrost as a standalone Docker Compose service, decoupled from agent-core, to evaluate it before broader integration.

## Goals / Non-Goals

**Goals:**
- Standalone Bifrost deployment via Docker Compose
- Persistent configuration and logs via volume mount to `~/.tdt/bifrost/`
- Health check for monitoring
- Web UI accessible on loopback for provider configuration
- Follows TDT deployment conventions (loopback binding, `docker compose` v2, TDT_HOME pattern)

**Non-Goals:**
- Integration with agent-core compose stack (follow-up change)
- Replacing OmniRoute (evaluation phase)
- Multi-node clustering or HA
- Observability stack (Prometheus/Grafana)
- Automated provider key provisioning (manual via Web UI)
- config.json seed file (Web UI is the primary config interface)

## Decisions

### D1: Standalone compose file at `deployments/bifrost/`

**Decision:** Place `docker-compose.yml` at `deployments/bifrost/` rather than inside an existing repo.

**Rationale:**
- Bifrost is infrastructure, not application code — it doesn't belong in agent-core or tdt-core
- `deployments/` already holds launchd service definitions (webhook-receiver, ai-review)
- Docker Compose services that don't build custom images fit naturally here
- Keeps the service decoupled for independent lifecycle management

**Alternatives considered:**
- `~/.tdt/bifrost/compose.yml` — rejected; mixes config root with deployment artifacts
- Inside `agent-core/` — rejected; user explicitly wants standalone first

### D2: Port 8180 on loopback

**Decision:** Bind `127.0.0.1:8180:8080` (host:container).

**Rationale:**
- Port 8080 is occupied by webhook-receiver
- Loopback binding matches existing pattern (scheduler on `127.0.0.1:9100`)
- No LAN exposure needed for a local development gateway
- 8180 is free (verified via `lsof`)

### D3: Volume mount to `~/.tdt/bifrost/`

**Decision:** Mount `${HOME}/.tdt/bifrost` to `/app/data` inside the container.

**Rationale:**
- Follows TDT_HOME convention (`~/.tdt/` is the canonical config root)
- Bifrost stores `config.json`, `config.db` (SQLite), and `logs.db` in its app dir
- Volume mount survives container rebuilds and image updates
- Consistent with how scheduler mounts `${HOME}/.tdt:/home/agent/.tdt`

### D4: No config.json seed — Web UI primary

**Decision:** Start with an empty data directory; configure providers via Web UI at `http://localhost:8180/`.

**Rationale:**
- User explicitly chose Web UI configuration
- Bifrost's Web UI is the recommended config interface
- Avoids committing API keys to files
- config.json can be added later for declarative setup

### D5: Upstream image, no custom Dockerfile

**Decision:** Use `maximhq/bifrost:latest` directly, no build step.

**Rationale:**
- Bifrost is a third-party tool, not custom code
- No TDT-specific modifications needed
- Simpler maintenance — `docker compose pull` gets updates
- Matches the pattern of using upstream postgres/redis images

## Validated ( tested against `maximhq/bifrost:latest` )

| Assumption | Result |
|------------|--------|
| Health endpoint at `GET /health` | ✅ Returns `{"components":{"db_pings":"ok"},"status":"ok"}` (HTTP 200) |
| Docker healthcheck with `curl -fsS` | ✅ Container reaches `healthy` status |
| Volume mount to `/app/data` | ✅ config.db + logs.db persist across restarts |
| Clean start without config.json | ✅ Auto-creates SQLite databases |
| config.json seed file | ✅ Picked up on restart if present |
| Web UI at root `/` | ✅ Dashboard loads, providers configurable |
| `/v1/models` endpoint | ✅ Returns `{"data":[]}` when no providers configured |
| Restart persistence | ✅ All data survives `docker restart` |
| Port 8180 availability | ✅ Verified free via `lsof` |

## Built-in Features (available at deploy time, zero config)

| Feature | Endpoint | Notes |
|---------|----------|-------|
| Prometheus metrics | `GET /metrics` | Built-in, async, tracks `bifrost_upstream_requests_total`, `bifrost_cost_total`, `bifrost_cache_hits_total`, token counts, latency histograms |
| Request logs | SQLite `logs.db` | Auto-created, retention configurable via Web UI (default 90 days) |
| Provider key management | Web UI | Weighted load balancing, model allowlists, automatic failover on key failure |

## Future Integration Path (not in this change)

**agent-core PydanticAI integration** — agent-core already uses PydanticAI. Bifrost has a native PydanticAI drop-in at `/pydanticai`:

```python
# Current: direct provider
provider = OpenAIProvider(base_url="https://api.openai.com/v1")

# Future: through Bifrost
provider = OpenAIProvider(base_url="http://localhost:8180/pydanticai/v1", api_key="dummy-key")
```

This means the follow-up integration change is a single env var (`BIFROST_URL=http://localhost:8180`) plus a provider URL swap in agent-core's gateway factory.

## Risks / Trade-offs

- **[Port conflict]** → 8180 verified free; if it becomes occupied, change the host port in compose.yaml
- **[Image tag drift]** → `latest` tag may introduce breaking changes; pin to a version tag after initial evaluation
- **[Data loss on `docker compose down -v`]** → Document that `-v` flag removes persistent data; use `docker compose down` (no `-v`) for restarts
- **[Web UI auth]** → Bifrost's Web UI has no auth by default; loopback binding limits exposure but note this for production
- **[Disk usage]** → SQLite logs.db grows over time; Bifrost has log retention config (default 90 days)

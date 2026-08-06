# Design: Hermes AgentMemory Plugin Integration

## Architecture Overview

```
+--------------------------------------------------------------+
|                    Hermes Agent Session                       |
|                                                               |
|  +-------------+    +------------------+                     |
|  | Built-in     |    | AgentMemory      |                     |
|  | Memory       |    | Plugin           |                     |
|  | (MEMORY.md,  |    | (~/.hermes/      |                     |
|  |  USER.md,    |    |  plugins/        |                     |
|  |  SQLite)     |    |  agentmemory/)   |                     |
|  +-------------+    +--------+---------+                     |
|                              | 6 hooks + 3 tools              |
|                              |                                |
|  +---------------------------v-----------------------------+ |
|  |              Hermes Agent Loop                           | |
|  |  1. system_prompt_block -> inject project profile        | |
|  |  2. prefetch -> inject relevant memories before LLM      | |
|  |  3. sync_turn -> capture conversation in background      | |
|  |  4. on_pre_compress -> re-inject before compaction       | |
|  |  5. on_memory_write -> mirror MEMORY.md to agentmemory   | |
|  |  6. on_session_end -> mark session complete              | |
|  +------------------------------+--------------------------+ |
+---------------------------------+----------------------------+
                                  | HTTP REST (localhost:3111)
                                  v
+--------------------------------------------------------------+
|              agentmemory Server (v0.9.28)                     |
|  Port 3111: REST API + MCP Server                             |
|  Port 3112: WebSocket Streams                                 |
|  Port 3113: Real-time Viewer                                  |
|  Engine: iii v0.11.2 (pinned binary)                          |
|  Storage: ~/.agentmemory/data/                                |
|  Embeddings: Ofable-5 nomic-embed-text (768-dim, OpenAI API) |
|  LLM: Ofable-5 fable-5:3b (local) or API fallback            |
|  Search: BM25 + vector + knowledge graph                      |
+--------------------------------------------------------------+
                                  |
+---------------------------------v----------------------------+
|              Ofable-5 (localhost:11434)                       |
|  Embedding model: nomic-embed-text (137M params, 768 dims)   |
|  LLM model: fable-5:3b (~2GB) for compression/summarization  |
|  OpenAI-compatible API: /v1/embeddings + /v1/chat/completions |
+--------------------------------------------------------------+
                                  |
+---------------------------------v----------------------------+
|              mcp-router (transport hub)                       |
|  Registered: agentmemory server (auto_start=1)                |
|  Tools: mcp__mcp_router__memory_* (54 tools)                 |
|  Available to: Hermes, Claude Code, Codex, OpenCode, Pi       |
+--------------------------------------------------------------+
```

## Two Integration Layers

### Layer 1: MCP Server (via mcp-router)
- **Already registered** in mcp-router SQLite with auto_start=1
- Provides 54 MCP tools: memory_save, memory_smart_search, memory_sessions, etc.
- Available to ALL agents through mcp-router transport
- **Status**: Registration complete, server running but in degraded state (viewer only)

### Layer 2: Hermes Plugin (deep integration)
- **Not yet installed** -- needs copy from agentmemory repo
- Provides 6 lifecycle hooks + 3 simplified tools
- Hooks into Hermes agent loop transparently
- Adds prefetch, auto-capture, compaction protection
- **Status**: Not started

## Why Both Layers?

The MCP server provides breadth (54 tools, cross-agent). The plugin provides depth (lifecycle hooks, transparent integration). They're complementary:

| Capability | MCP Server | Plugin |
|-----------|-----------|--------|
| Tool access (54 tools) | YES | NO (only 3 tools) |
| Cross-agent shared memory | YES | NO (Hermes-only) |
| Pre-LLM context injection | NO | YES (prefetch) |
| Auto turn capture | NO | YES (sync_turn) |
| Compaction protection | NO | YES (on_pre_compress) |
| System prompt enrichment | NO | YES (system_prompt_block) |
| MEMORY.md mirroring | NO | YES (on_memory_write) |
| Session lifecycle tracking | NO | YES (on_session_end) |

## Plugin Implementation Details

### AgentMemoryProvider class

```python
class AgentMemoryProvider(MemoryProvider):
    """Hermes memory provider plugin for agentmemory."""

    @property
    def name(self) -> str:
        return "agentmemory"

    def is_available(self) -> bool:
        # No network calls -- just validate URL format
        base = os.environ.get("AGENTMEMORY_URL", "http://localhost:3111")
        return _validate_url(base)

    def initialize(self, session_id: str, **kwargs) -> None:
        # Register session with agentmemory server
        _api(base, "session/start", {...})

    def system_prompt_block(self) -> str:
        # Fetch project context from agentmemory
        return _api(base, "context", {...}).get("context", "")

    def prefetch(self, query: str, **kwargs) -> str:
        # Smart search for relevant memories
        results = _api(base, "smart-search", {"query": query, "limit": 5})
        return format_results(results)

    def sync_turn(self, user: str, assistant: str, **kwargs) -> None:
        # Background capture of conversation turn
        _api_bg(base, "observe", {...})

    def on_session_end(self, messages, **kwargs) -> None:
        # Mark session complete for summarization
        _api(base, "session/end", {...})

    def on_pre_compress(self, messages, **kwargs) -> None:
        # Re-inject context before compaction
        context = _api(base, "context", {...}).get("context", "")
        messages.insert(0, {"role": "user", "content": f"[agentmemory context]\n{context}"})

    def on_memory_write(self, action, target, content, **kwargs) -> None:
        # Mirror MEMORY.md writes to agentmemory
        if action in ("add", "update") and content:
            _api_bg(base, "remember", {"content": content, "type": "fact"})
```

### API Communication

- All API calls go to `http://localhost:3111/agentmemory/<path>`
- Auth: Bearer token via `AGENTMEMORY_SECRET` (optional, localhost is open by default)
- Timeouts: 5 seconds per call
- Background operations: threaded (sync_turn, on_memory_write)
- HTTPS guard: warns when bearer token sent over plaintext HTTP to non-loopback

## Embedding Strategy (Revised)

### Decision: Ofable-5 `nomic-embed-text` (OpenAI-compatible API, local, free)

**Why Ofable-5 for embeddings:**
- **Already pulled** — `nomic-embed-text` is installed and working on Ofable-5
- **137M params, 768 dimensions** — 3.4x more parameters and 2x richer representation than all-MiniLM-L6-v2 (22M, 384 dims)
- **GPU-accelerated** — runs on M1 Neural Engine via Ofable-5, faster inference than CPU-bound @xenova/transformers
- **OpenAI-compatible API** — agentmemory's `EMBEDDING_PROVIDER=openai` uses `/v1/embeddings` endpoint natively
- **Single dependency** — Ofable-5 handles both LLM (compression) and embeddings (vector search)
- **Already verified** — tested `nomic-embed-text` embedding API returns 768-dim vectors with good semantic discrimination (cosine 1.00 same-topic, ~0.47 cross-topic)
- **No first-run download** — model is already local, no network dependency on first use

**Why NOT other options:**

| Provider | Model | Why rejected |
|----------|-------|-------------|
| @xenova/transformers `all-MiniLM-L6-v2` | 22M params, 384 dims | Lower quality (3.4x fewer params, 2x fewer dims), requires separate dependency, CPU-only |
| OpenAI `text-embedding-3-small` | Cloud API | $0.02/1M tokens, requires API key, network dependency |
| fable-5 `gemini-embedding-001` | Cloud API | Requires API key, network dependency |
| Voyage `voyage-code-3` | Cloud API | Paid, code-optimized but overkill for memory compression |

**Configuration:**
```env
# ~/.agentmemory/.env
EMBEDDING_PROVIDER=openai
OPENAI_API_KEY=ollama
OPENAI_BASE_URL=http://localhost:11434/v1
OPENAI_EMBEDDING_MODEL=nomic-embed-text
OPENAI_EMBEDDING_DIMENSIONS=768
```

**How it works:**
1. `EMBEDDING_PROVIDER=openai` tells agentmemory to use the OpenAI-compatible embedding provider
2. `OPENAI_EMBEDDING_BASE_URL` defaults to `OPENAI_BASE_URL` (http://localhost:11434/v1)
3. Agentmemory calls `POST /v1/embeddings` on Ofable-5 with model `nomic-embed-text`
4. Ofable-5 returns 768-dim vectors (F16 quantization, ~261MB model)
5. Vectors are indexed in agentmemory's triple-stream search (BM25 + Vector + Graph)

**Dimension note:** `nomic-embed-text` (768 dims) is not in agentmemory's built-in model table, so `OPENAI_EMBEDDING_DIMENSIONS=768` must be set explicitly. Without this, agentmemory defaults to 1536 dims and rejects the mismatched vectors.

**Existing vector index warning:** If switching from `all-MiniLM-L6-v2` (384 dims) to `nomic-embed-text` (768 dims), the persisted vector index will have dimension mismatches. Set `AGENTMEMORY_DROP_STALE_INDEX=true` once to discard stale vectors and rebuild from live observations.

## LLM Strategy (Revised)

### Decision: Ofable-5 `fable-5:3b` (local, free) with API fallback option

**Why `fable-5:3b`:**
- **~2GB RAM** — leaves 14GB for other processes on M1 16GB
- **Adequate quality** — compression and summarization are short tasks (<2K tokens in, <500 tokens out)
- **Zero cost** — runs entirely on local hardware
- **Fast on M1** — ~22 tok/s inference speed
- **agentmemory explicitly recommends** this as "smallest sane option" for compression

**Why NOT `fable-5:7b` (current .env reference):**
- **~4.7GB RAM** — would consume ~30% of total memory on M1 16GB
- **Overkill for compression** — code-specific training not needed for memory summarization
- **Slower inference** — 7B model vs 3B on same hardware
- **Higher memory pressure** — risks OOM with other development tools running

**Alternative: API fallback (OpenRouter `fable-5`)**
- **~$0.40/month** for typical workload (635 requests / 35 hours active use)
- **Better quality** than local 3B model
- **Zero RAM usage** — runs in cloud
- **Trade-off:** Requires API key and network dependency

**Configuration (recommended — local):**
```env
# ~/.agentmemory/.env
OPENAI_API_KEY=ollama
OPENAI_BASE_URL=http://localhost:11434/v1
OPENAI_MODEL=fable-5:3b
```

**Configuration (API fallback):**
```env
# ~/.agentmemory/.env
OPENAI_API_KEY=<your-openrouter-key>
OPENAI_BASE_URL=https://openrouter.ai/api/v1
OPENAI_MODEL=fable-5/fable-5
```

**Note:** The current .env has `OPENAI_MODEL=fable-5.5-coder:7b` which is NOT pulled. Must change to `fable-5:3b` and pull the model.

## Unified Ofable-5 Configuration

Both embeddings and LLM use the same Ofable-5 instance. The complete .env section:

```env
# ── Embeddings (Ofable-5 nomic-embed-text) ───────────────────────
EMBEDDING_PROVIDER=openai
OPENAI_EMBEDDING_MODEL=nomic-embed-text
OPENAI_EMBEDDING_DIMENSIONS=768

# ── LLM Provider (Ofable-5 fable-5:3b) ─────────────────────────
OPENAI_API_KEY=ollama
OPENAI_BASE_URL=http://localhost:11434/v1
OPENAI_MODEL=fable-5:3b

# ── Server binding ──────────────────────────────────────────────
AGENTMEMORY_HOST=127.0.0.1
AGENTMEMORY_PORT=3111
AGENTMEMORY_VIEWER_PORT=3113
```

This uses a single Ofable-5 instance for both services, minimizing resource usage and simplifying the dependency chain.

## Port Investigation (Revised)

### Current State (verified 2026-08-06)

| Port | Status | Owner | Notes |
|------|--------|-------|-------|
| 3111 | **FREE** | — | REST API target. No conflict. |
| 3112 | **FREE** | — | WebSocket streams target. No conflict. |
| 3113 | **OCCUPIED** | agentmemory (PID 93422) | Viewer port. Expected — this is the running agentmemory server. |
| 49134 | **FREE** | — | iii engine target. No conflict. |
| 11434 | **OCCUPIED** | Ofable-5 (PID 88084) | Ofable-5 API. Expected. |

### Finding: No port conflicts exist
The evidence bundle's "Port 3111 CLOSED" finding was **stale** — the agentmemory server (PID 93422) was running at time of evidence collection but the iii engine had already failed to start. Port 3113 (viewer) is open as expected. Ports 3111, 3112, and 49134 are all available.

### Single Server Constraint
Only ONE agentmemory server should run at a time. The current process (PID 93422) is stuck in a degraded state (viewer only, no REST API). It should be killed and restarted cleanly after fixing the iii engine issue.

## iii Engine Root Cause Analysis

### Problem
The agentmemory server (PID 93422) is running but the iii engine (v0.11.2) is NOT running as a separate process. The server has been attempting to reconnect 1489+ times with WebSocket errors:

```
[OTel] Disconnected from engine, will reconnect...
[iii] Reconnecting in 29642ms (attempt 1470)...
```

Port 3111 (REST API) is NOT open because the iii engine is not listening.

### Root Cause
The iii engine binary (`~/.agentmemory/bin/iii`, arm64, v0.11.2) requires a `iii-config.yaml` to start. The agentmemory CLI searches for this config in:

1. `AGENTMEMORY_III_CONFIG` env var
2. `process.cwd()` (go-microservices — no config here)
3. `~/.agentmemory/iii-config.yaml` (**NOT present**)
4. `__dirname/iii-config.yaml` (dist directory — **bundled config exists**)
5. `__dirname/../iii-config.yaml` (package root — **bundled config exists**)

The bundled config at `~/.npm-global/lib/node_modules/@agentmemory/agentmemory/iii-config.yaml` should be found by search paths 4 or 5. However, the iii engine's config references relative paths:
- `./data/state_store.db`
- `./data/stream_store`

These resolve relative to the working directory where iii is spawned, which may not have a `data/` subdirectory. The `~/.agentmemory/data/` directory exists but is empty.

### Fix Required
1. Copy `iii-config.yaml` to `~/.agentmemory/iii-config.yaml` with corrected paths
2. Ensure `~/.agentmemory/data/` directory exists (it does — empty)
3. Kill stale agentmemory process (PID 93422)
4. Restart agentmemory server
5. Verify iii engine starts and port 3111 opens

### iii-config.yaml (corrected for local deployment)
```yaml
workers:
  - name: iii-http
    config:
      port: 3111
      host: 127.0.0.1
      default_timeout: 180000
      cors:
        allowed_origins: ["http://localhost:3111", "http://localhost:3113", "http://127.0.0.1:3111", "http://127.0.0.1:3113"]
        allowed_methods: [GET, POST, PUT, DELETE, OPTIONS]
  - name: iii-state
    config:
      adapter:
        name: kv
        config:
          store_method: file_based
          file_path: /Users/androidteam/.agentmemory/data/state_store.db
  - name: iii-queue
    config:
      adapter:
        name: builtin
  - name: iii-pubsub
    config:
      adapter:
        name: local
  - name: iii-cron
    config:
      adapter:
        name: kv
  - name: iii-stream
    config:
      port: 3112
      host: 127.0.0.1
      adapter:
        name: kv
        config:
          store_method: file_based
          file_path: /Users/androidteam/.agentmemory/data/stream_store
  - name: iii-observability
    config:
      enabled: true
      service_name: agentmemory
      exporter: memory
      sampling_ratio: 0.1
      metrics_enabled: true
      logs_enabled: true
      logs_console_output: false
  - name: iii-exec
    config:
      watch:
        - src/**/*.ts
      exec:
        - node dist/index.mjs
```

## Dependencies (Revised)

| Dependency | Version | Status | Notes |
|-----------|---------|--------|-------|
| Node.js | >= 20 | ✅ Installed | Required for npx |
| agentmemory | 0.9.28 | ✅ Installed | Latest version |
| agentmemory-mcp | 0.9.28 | ✅ Installed | Latest version |
| iii engine | 0.11.2 | ✅ Binary present | At ~/.agentmemory/bin/iii (arm64) |
| Ofable-5 | 0.32.6 | ✅ Running | Port 11434. 2 models pulled. |
| nomic-embed-text | latest | ✅ Pulled | 137M params, 768 dims, 261MB |
| Hermes plugin | — | ❌ Not installed | Phase 2 of this change |
| iii-config.yaml | — | ❌ Missing from ~/.agentmemory/ | Root cause of engine failure |
| fable-5:3b | — | ❌ Not pulled | ~2GB. Needed for LLM compression. |

## Trade-offs

### Pro
- **95.2% retrieval accuracy** on LongMemEval-S benchmark
- **Cross-agent shared memory** -- memories from all agents in one store
- **Unified local stack** -- Ofable-5 handles both embeddings (nomic-embed-text) and LLM (fable-5:3b)
- **Higher quality embeddings** -- 137M params / 768 dims vs 22M / 384 dims (local transformer)
- **GPU-accelerated** -- M1 Neural Engine for both embedding and LLM inference
- **No first-run download** -- nomic-embed-text already pulled, no network dependency
- **Lifecycle hooks** -- transparent integration, no agent behavior changes needed
- **Compaction protection** -- context preserved across compressions
- **Real-time viewer** at localhost:3113

### Con
- **Server dependency** -- agentmemory server must be running
- **Ofable-5 dependency** -- requires Ofable-5 running with nomic-embed-text + fable-5:3b pulled (~2.3GB total)
- **iii engine** -- auto-downloaded to ~/.agentmemory/bin/ on first run (~28MB)
- **Port usage** -- 3 ports occupied (3111, 3112, 3113)
- **Plugin maintenance** -- pinned to agentmemory repo version (currently v0.8.0 plugin.yaml, independent of server v0.9.28)
- **Dual memory systems** -- built-in memory + agentmemory (intentional, complementary)

### Mitigations
- mcp-router auto_start=1 handles server lifecycle
- Plugin gracefully degrades when server is unavailable (returns empty strings)
- Single Ofable-5 instance for both services (minimal resource usage)
- Plugin reads .env file for systemd/non-interactive startup compatibility
- iii-config.yaml copied to ~/.agentmemory/ with absolute paths for reliability
- `AGENTMEMORY_DROP_STALE_INDEX=true` handles vector dimension migration

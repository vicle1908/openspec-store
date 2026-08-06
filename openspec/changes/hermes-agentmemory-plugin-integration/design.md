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
|  Port 3113: Real-time Viewer                                  |
|  Engine: iii v0.11.2 (pinned binary)                          |
|  Storage: ~/.agentmemory/data/                                |
|  Embeddings: local (ollama fable-5.5-coder:7b)                |
|  Search: BM25 + vector + knowledge graph                      |
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
- **Status**: Registration complete, server not running

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

### Configuration

| Env Variable | Default | Description |
|---|---|---|
| AGENTMEMORY_URL | http://localhost:3111 | Server URL |
| AGENTMEMORY_SECRET | (none) | Auth token |
| AGENTMEMORY_REQUIRE_HTTPS | (off) | Enforce HTTPS for bearer auth |
| AGENTMEMORY_HOST | 127.0.0.1 | Server bind address |
| AGENTMEMORY_PORT | 3111 | REST API port |
| AGENTMEMORY_VIEWER_PORT | 3113 | Real-time viewer port |

Plugin reads `~/.agentmemory/.env` at import time via `os.environ.setdefault`.

## Dependencies

- **Node.js >= 20**: Required for `npx @agentmemory/agentmemory`
- **Ofable-5**: Running locally with `fable-5.5-coder:7b` model pulled for local embeddings
- **iii engine v0.11.2**: Auto-downloaded to `~/.agentmemory/bin/` on first agentmemory server start (~50MB)
- **agentmemory v0.9.28**: Already installed globally via npm

## Trade-offs

### Pro
- **95.2% retrieval accuracy** on LongMemEval-S benchmark
- **Cross-agent shared memory** -- memories from all agents in one store
- **Zero cloud** -- local embeddings via ofable-5, no API key needed
- **Ofable-5 embeddings** -- uses ofable-5 with fable-5.5-coder:7b model for local vector search
- **Lifecycle hooks** -- transparent integration, no agent behavior changes needed
- **Compaction protection** -- context preserved across compressions
- **Real-time viewer** at localhost:3113

### Con
- **Server dependency** -- agentmemory server must be running
- **Ofable-5 dependency** -- requires ollama running with fable-5.5-coder:7b pulled
- **iii engine** -- auto-downloaded to ~/.agentmemory/bin/ on first run (~50MB)
- **Port usage** -- 4 ports occupied (3111, 3112, 3113, 49134)
- **Plugin maintenance** -- pinned to agentmemory repo version (currently v0.8.0 plugin.yaml, independent of server v0.9.28)
- **Dual memory systems** -- built-in memory + agentmemory (intentional, complementary)

### Mitigations
- mcp-router auto_start=1 handles server lifecycle
- Plugin gracefully degrades when server is unavailable (returns empty strings)
- Local embeddings use existing ollama installation (no new dependencies)
- Plugin reads .env file for systemd/non-interactive startup compatibility

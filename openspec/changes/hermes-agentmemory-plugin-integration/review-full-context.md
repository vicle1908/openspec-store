# REVIEW CONTEXT BUNDLE (REVISED 2026-08-06 — Ofable-5 Embeddings)

## Change Artifacts

### PROPOSAL
- Phase 0: Fix prerequisites (kill stale processes, copy iii-config.yaml, pull LLM model, configure Ofable-5 embeddings)
- Phase 1: Start agentmemory server
- Phase 2: Install Hermes plugin (6 hooks + 3 tools)
- Phase 3: Configure Hermes
- Phase 4: Verify end-to-end
- Phase 5: Documentation
- Embedding: Ofable-5 nomic-embed-text (137M params, 768 dims, already pulled)
- LLM: Ofable-5 fable-5:3b (local, free, ~2GB RAM)

### DESIGN
- Architecture diagram with Ofable-5 as unified embedding + LLM provider
- Two-layer integration (MCP server + Hermes plugin)
- Embedding strategy: nomic-embed-text via Ofable-5 OpenAI-compatible API
- LLM strategy: fable-5:3b (2GB RAM, adequate for compression)
- Port investigation: no conflicts (3111, 3112, 3113 all available)
- iii engine root cause: missing iii-config.yaml, bundled config needs absolute paths
- Unified Ofable-5 config: single instance for both services

### TASKS
- 6 phases (0-5 + archive)
- Phase 0: Fix prerequisites (NEW — addresses root cause)
- Phase 1: Start agentmemory server
- Phase 2: Install Hermes plugin
- Phase 3: Configure Hermes
- Phase 4: Verify end-to-end
- Phase 5: Documentation & cleanup
- Archive section

### .openspec.yaml
```yaml
schema: spec-driven
created: 2026-08-06
skip_specs: true
change: hermes-agentmemory-plugin-integration
description: "Deep integration of agentmemory into Hermes via memory provider plugin (6 lifecycle hooks) + MCP server tools via mcp-router"
repos:
  - openspec-store
```

### EVIDENCE BUNDLE (verified 2026-08-06)

#### Hardware
- Mac mini M1 (Macmini9,1), 16GB RAM, 8 cores, macOS 26.6

#### Installed Versions
- agentmemory: 0.9.28 (latest)
- agentmemory-mcp: 0.9.28 (latest)
- iii engine: 0.11.2 (binary at ~/.agentmemory/bin/iii, arm64)
- @xenova/transformers: 2.17.2 (in agentmemory node_modules — NOT used for embeddings)
- Ofable-5: 0.32.6 (running, port 11434)

#### Ofable-5 Models Pulled
- nomic-embed-text: 261MB, 137M params, 768 dims, F16 quantization ✅
- fable-5.5:0.5b: 379MB (too small for compression)

#### Running Processes
- agentmemory (PID 93422): DEGRADED — port 3113 only, port 3111 closed
- agentmemory-mcp (PID 90932): SHIM FALLBACK — 7 tools only
- Ofable-5 (PID 88072/88084): RUNNING — nomic-embed-text loaded

#### Port Status
| Port | Status | Owner |
|------|--------|-------|
| 3111 | FREE | — |
| 3112 | FREE | — |
| 3113 | OCCUPIED | agentmemory viewer |
| 49134 | FREE | — |
| 11434 | OCCUPIED | Ofable-5 |

#### Root Cause
- iii engine not starting: ~/.agentmemory/iii-config.yaml MISSING
- Bundled config: ~/.npm-global/lib/node_modules/@agentmemory/agentmemory/iii-config.yaml
- Config references relative paths (./data/) — need absolute paths for ~/.agentmemory/data/

#### .env Configuration (target)
```
EMBEDDING_PROVIDER=openai
OPENAI_EMBEDDING_MODEL=nomic-embed-text
OPENAI_EMBEDDING_DIMENSIONS=768
OPENAI_API_KEY=ollama
OPENAI_BASE_URL=http://localhost:11434/v1
OPENAI_MODEL=fable-5:3b
AGENTMEMORY_HOST=127.0.0.1
AGENTMEMORY_PORT=3111
AGENTMEMORY_VIEWER_PORT=3113
```

#### Embedding Provider Detection (agentmemory source)
```javascript
// detectEmbeddingProvider() — EMBEDDING_PROVIDER override takes precedence
// With EMBEDDING_PROVIDER=openai:
//   → OpenAIEmbeddingProvider
//   → Uses OPENAI_EMBEDDING_BASE_URL || OPENAI_BASE_URL
//   → Uses OPENAI_EMBEDDING_MODEL || "text-embedding-3-small"
//   → Uses OPENAI_EMBEDDING_DIMENSIONS for dimension override
//   → Calls POST /v1/embeddings on Ofable-5
```

#### Embedding Verification
- Ofable-5 `/v1/embeddings` endpoint: returns 768-dim vectors ✅
- Auth header: Ofable-5 accepts `Authorization: Bearer ollama` gracefully ✅
- Semantic discrimination: cosine 1.00 same-topic, ~0.47 cross-topic ✅
- nomic-embed-text model info: nomic-bert architecture, 137M params, 768 embedding length ✅

#### Hermes Config
- memory.memory_enabled: true
- memory.user_profile_enabled: true
- No memory.provider set (using built-in only)

#### Plugin Status
- ~/.hermes/plugins/agentmemory/ — DOES NOT EXIST

### UPSTREAM PLUGIN SOURCE (integrations/hermes/__init__.py)
```python
"""
agentmemory memory provider for Hermes Agent.

Drop this folder into ~/.hermes/plugins/agentmemory/
or install via: hermes plugin install agentmemory

Requires agentmemory server running: npx @agentmemory/agentmemory
"""

from __future__ import annotations

import json
import os
import sys
import threading
import time
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from urllib.error import URLError

try:
    from agent.memory_provider import MemoryProvider
except ImportError:
    from abc import ABC, abstractmethod

    class MemoryProvider(ABC):
        @property
        @abstractmethod
        def name(self) -> str: ...
        @abstractmethod
        def is_available(self) -> bool: ...
        @abstractmethod
        def initialize(self, session_id: str, **kwargs: Any) -> None: ...
        @abstractmethod
        def get_tool_schemas(self) -> list[dict]: ...
        @abstractmethod
        def handle_tool_call(self, name: str, args: dict) -> str: ...
        def get_config_schema(self) -> list[dict]: return []
        def save_config(self, values: dict, hermes_home: str) -> None: pass
        def system_prompt_block(self) -> str: return ""
        def prefetch(self, query: str, **kwargs: Any) -> str: return ""
        def queue_prefetch(self, query: str, **kwargs: Any) -> None: pass
        def sync_turn(self, user: str, assistant: str, **kwargs: Any) -> None: pass
        def on_session_end(self, messages: list, **kwargs: Any) -> None: pass
        def on_pre_compress(self, messages: list, **kwargs: Any) -> None: pass
        def on_memory_write(self, action: str, target: str, content: str, **kwargs: Any) -> None: pass
        def shutdown(self, **kwargs: Any) -> None: pass


DEFAULT_BASE_URL = "http://localhost:3111"
TIMEOUT = 5
LOOPBACK_HOSTS = {"localhost", "127.0.0.1", "::1"}
_plaintext_bearer_warned = False

# Preload ~/.agentmemory/.env at plugin-import time
def _preload_agentmemory_dotenv() -> None:
    candidates: list[Path] = []
    home = os.environ.get("HOME")
    if home:
        candidates.append(Path(home) / ".agentmemory" / ".env")
    xdg_config = os.environ.get("XDG_CONFIG_HOME")
```

## Workspace Context
- Multi-repo workspace at ~/Developer/ with 18 repos
- mcp-router is the single MCP transport hub (all MCP tools route through it)
- Hermes Agent is the primary AI assistant framework
- OpenSpec store at ~/Developer/openspec-store/ (333 specs, 260 archives)
- Existing developer-memory spec: IMPLEMENTED (agentmemory as shared memory layer)
- agentmemory v0.9.28 installed globally, mcp-router registered with auto_start=1
- agentmemory server RUNNING but DEGRADED (port 3113 only, port 3111 closed)
- iii engine NOT running (missing iii-config.yaml)
- Hermes plugin NOT installed (~/.hermes/plugins/agentmemory/ doesn't exist)
- Hermes config has no memory.provider set
- Ofable-5 running with nomic-embed-text pulled (768-dim embeddings ready)
- Upstream plugin.yaml version: 0.8.0 (plugin is older than agentmemory v0.9.28)
- Hardware: Mac mini M1, 16GB RAM, 8 cores

# REVIEW CONTEXT BUNDLE

## Change Artifacts

### PROPOSAL
1|# hermes-agentmemory-plugin-integration
2|
3|## Why
4|
5|Hermes Agent currently has two independent memory systems:
6|1. **Built-in memory** — flat MEMORY.md/USER.md files + SQLite FTS5 session search
7|2. **agentmemory** — installed globally (v0.9.28), registered in mcp-router, but server not running and no Hermes plugin installed
8|
9|The result: Hermes has no episodic cross-session memory, no pre-LLM context injection, no automatic turn-level capture, and no session compaction protection. Every new session starts from scratch. The agentmemory ecosystem (95.2% retrieval accuracy, hybrid BM25+vector+graph search, cross-agent shared memory) is available but not wired into Hermes.
10|
11|The `developer-memory` OpenSpec spec already defines agentmemory as the shared developer-memory layer. The MCP server is registered in mcp-router with auto_start=1. The missing piece is the Hermes plugin that provides deep lifecycle integration — 6 hooks that make agentmemory transparent to the agent, not just another tool.
12|
13|## What Changes
14|
15|### Phase 1: Start agentmemory server
16|- Verify agentmemory v0.9.28 is installed and healthy
17|- Start the agentmemory server on localhost:3111
18|- Verify health endpoint responds
19|- Verify MCP tools are reachable through mcp-router (auto_start=1 already configured)
20|
21|### Phase 2: Install Hermes memory provider plugin
22|- Copy `integrations/hermes/` from the agentmemory repo to `~/.hermes/plugins/agentmemory/`
23|- Files: `__init__.py`, `plugin.yaml`, `README.md`
24|- The plugin provides `AgentMemoryProvider` class implementing the `MemoryProvider` interface
25|- 6 lifecycle hooks:
26|  - `prefetch()` — inject relevant memories before each LLM call
27|  - `sync_turn()` — capture every conversation turn in background
28|  - `on_session_end()` — mark sessions complete for summarization
29|  - `on_pre_compress()` — re-inject context before compaction
30|  - `on_memory_write()` — mirror MEMORY.md writes to agentmemory
31|  - `system_prompt_block()` — inject project profile at session start
32|- 3 tools: `memory_recall`, `memory_save`, `memory_search`
33|
34|### Phase 3: Configure Hermes
35|- Set `memory.provider: agentmemory` in `~/.hermes/config.yaml`
36|- Verify environment variables (AGENTMEMORY_URL defaults to http://localhost:3111)
37|- No additional config needed — plugin auto-reads `~/.agentmemory/.env`
38|
39|### Phase 4: Verify end-to-end
40|- `hermes memory status` shows agentmemory as available
41|- Save a test memory, recall it in a new session
42|- Verify prefetch injects context before LLM calls
43|- Verify sync_turn captures conversation in background
44|- Verify on_pre_compress preserves context during compaction
45|- Verify MCP tools work through mcp-router (memory_save, memory_smart_search, etc.)
46|
47|### Phase 5: Documentation
48|- Update workspace-knowledge-tools skill to reflect plugin status
49|- Update wiki agentmemory entity page
50|- Commit all changes
51|
52|## Compatibility
53|
54|- **Backward compatible**: Hermes built-in memory (MEMORY.md/USER.md + SQLite FTS5) continues to work alongside agentmemory
55|- **agentmemory supplements**: Does not replace Hermes built-in memory — adds structured episodic memory on top
56|- **Cross-agent**: Memories saved from Hermes are visible to Claude Code, Codex, OpenCode, and vice versa via shared agentmemory store
57|- **Zero cloud**: Runs fully local with local embeddings (ollama fable-5.5-coder:7b), no API key required
58|- **Port conflict**: agentmemory uses ports 3111 (REST), 3112 (streams), 3113 (viewer), 49134 (engine) — verify no conflicts
59|
60|## Rollout
61|
62|1. Start server → verify health → verify MCP tools
63|2. Install plugin → configure provider → restart Hermes session
64|3. Verify all 6 hooks fire correctly
65|4. Monitor for 24 hours — check viewer at localhost:3113
66|
67|## Rollback
68|
69|1. Remove `memory.provider` from config.yaml
70|2. Remove `~/.hermes/plugins/agentmemory/`
71|3. Stop agentmemory server
72|4. Hermes reverts to built-in memory only — no data loss (agentmemory store preserved at ~/.agentmemory/)
73|

### DESIGN


### TASKS
1|# Tasks: hermes-agentmemory-plugin-integration
2|
3|## Phase 1: Start agentmemory server
4|- [ ] Verify agentmemory v0.9.28 is installed (`agentmemory --version`)
5|- [ ] Start agentmemory server in background (`agentmemory &` or `npx -y @agentmemory/agentmemory`)
6|- [ ] Verify health endpoint (`curl http://localhost:3111/agentmemory/health`)
7|- [ ] Verify MCP tools reachable through mcp-router (test `memory_smart_search`)
8|
9|## Phase 2: Install Hermes plugin
10|- [ ] Fetch `integrations/hermes/` from agentmemory repo (curl raw GitHub files)
11|- [ ] Create `~/.hermes/plugins/agentmemory/` directory
12|- [ ] Write `__init__.py` (AgentMemoryProvider class, 6 hooks)
13|- [ ] Write `plugin.yaml` (name, version, hooks list)
14|- [ ] Write `README.md` (installation docs)
15|- [ ] Verify plugin files are in place
16|
17|## Phase 3: Configure Hermes
18|- [ ] Add `memory.provider: agentmemory` to `~/.hermes/config.yaml`
19|- [ ] Verify AGENTMEMORY_URL defaults to http://localhost:3111
20|- [ ] Verify `~/.agentmemory/.env` exists and is readable
21|- [ ] Confirm no port conflicts (3111, 3112, 3113, 49134)
22|
23|## Phase 4: Verify end-to-end
24|- [ ] `hermes memory status` shows agentmemory as available
25|- [ ] Save a test memory via plugin tool (`memory_save`)
26|- [ ] Recall the test memory (`memory_recall`)
27|- [ ] Verify prefetch injects context before LLM calls
28|- [ ] Verify sync_turn captures conversation in background
29|- [ ] Verify on_pre_compress preserves context during compaction
30|- [ ] Verify MCP tools work through mcp-router
31|- [ ] Open viewer at http://localhost:3113 and confirm memories visible
32|
33|## Phase 5: Documentation & cleanup
34|- [ ] Update workspace-knowledge-tools skill with plugin installation status
35|- [ ] Update wiki agentmemory entity page with Hermes integration status
36|- [ ] Commit all changes to openspec-store
37|

### .openspec.yaml
1|schema: spec-driven
2|created: 2026-08-06
3|skip_specs: true
4|change: hermes-agentmemory-plugin-integration
5|description: "Deep integration of agentmemory into Hermes via memory provider plugin (6 lifecycle hooks) + MCP server tools via mcp-router"
6|repos:
7|  - openspec-store
8|

### EVIDENCE BUNDLE (verified workspace state)
1|## EVIDENCE BUNDLE: hermes-agentmemory-plugin-integration
2|
3|### 1. agentmemory install status
4|0.9.28
5|---
6|/Users/androidteam/.npm-global/bin/agentmemory
7|---
8|-rw-------@ 1 androidteam  staff  2881 Aug  5 19:53 /Users/androidteam/.agentmemory/.env
9|
10|### 2. agentmemory .env
11|# =============================================================================
12|# agentmemory v0.9.27 + iii-engine v0.11.2  —  B+ Feature Flags
13|#
14|# WARNING: Do not commit this file. It is generated by
15|#   scripts/agentmemory-bootstrap.sh and lives in ~/.agentmemory/.env
16|#   (outside the repo, survives `make clean`).
17|#
18|# Feature tier: B+ = Production + slots + reflect + inject-context + decay.
19|# NOT enabled (documented deliberate absences):
20|#   AGENTMEMORY_AUTO_COMPRESS=true   — off: 5–10× token multiplier
21|#   AGENTMEMORY_ALLOW_AGENT_SDK=true — off: Stop-hook recursion risk
22|#   CLAUDE_MEMORY_BRIDGE=true         — deferred to follow-up change
23|#
24|# Uncertain flags (set on ambitious basis, verify with `make agentmemory-doctor`):
25|#   AGENTMEMORY_REFLECT      — may require confirmation from upstream source
26|#   LESSON_DECAY_ENABLED      — may require confirmation from upstream source
27|#   AGENTMEMORY_AGENT_SCOPE  — confirmed: shared scope for cross-agent context
28|# =============================================================================
29|
30|# ── B+ Feature Flags ─────────────────────────────────────────────────────
31|
32|AGENTMEMORY_TOOLS=all
33|GRAPH_EXTRACTION_ENABLED=true
34|SNAPSHOT_ENABLED=true
35|CONSOLIDATION_ENABLED=true
36|AGENTMEMORY_SLOTS=memory
37|AGENTMEMORY_REFLECT=true
38|AGENTMEMORY_INJECT_CONTEXT=true
39|LESSON_DECAY_ENABLED=true
40|AGENTMEMORY_AGENT_SCOPE=shared
41|
42|# ── Embeddings ───────────────────────────────────────────────────────────
43|
44|EMBEDDING_PROVIDER=local
45|
46|# ── LLM Provider (zero-cost Ollama path) ─────────────────────────────────
47|
48|# Ollama must be running: ollama serve
49|# Pull the model first:  ollama pull qwen2.5-coder:7b
50|OPENAI_API_KEY=ollama
51|OPENAI_BASE_URL=http://localhost:11434/v1
52|OPENAI_MODEL=qwen2.5-coder:7b
53|
54|# ── Server binding ──────────────────────────────────────────────────────
55|
56|AGENTMEMORY_HOST=127.0.0.1
57|AGENTMEMORY_PORT=3111
58|AGENTMEMORY_VIEWER_PORT=3113
59|
60|# ── Security ────────────────────────────────────────────────────────────
61|
62|# Optional: set a secret for non-loopback deployments.
63|# Must be set if AGENTMEMORY_URL is not localhost/127.0.0.1.
64|# AGENTMEMORY_SECRET=your-secret-here
65|
66|# ── Observability ───────────────────────────────────────────────────────
67|
68|LOG_LEVEL=info
69|
70|### 3. Server health
71|curl: (7) Failed to connect to localhost port 3111 after 0 ms: Couldn't connect to server
72|NOT RUNNING
73|
74|### 4. mcp-router registration
75|agentmemory|npx|["-y","@agentmemory/mcp"]|1|0
76|
77|### 5. Hermes memory config
78|container_memory: 5120
79|  container_disk: 51200
80|  container_persistent: true
81|  docker_mount_cwd_to_workspace: false
82|  lifetime_seconds: 300
83|web:
84|  backend: brave-free
85|  extract_backend: tavily
86|  use_gateway: false
87|browser:
88|  inactivity_timeout: 120
89|--
90|memory:
91|  memory_enabled: true
92|  user_profile_enabled: true
93|  memory_char_limit: 3000
94|  user_char_limit: 2000
95|  nudge_interval: 10
96|  flush_min_turns: 6
97|delegation:
98|  model: fable-5
99|  provider: shopapikey
100|  max_iterations: 80
101|
102|### 6. Plugin directory
103|PLUGIN NOT INSTALLED
104|
105|### 7. Ports in use
106|COMMAND   PID        USER   FD   TYPE             DEVICE SIZE/OFF NODE NAME
107|node    93422 androidteam   21u  IPv4 0xad159feb0cabcd1c      0t0  TCP localhost:cs-auth-svr (LISTEN)
108|
109|### 8. npm global packages
110|/Users/androidteam/.npm-global/lib
111|├── @agentmemory/agentmemory@0.9.28
112|└─┬ @agentmemory/mcp@0.9.28
113|  └── @agentmemory/agentmemory@0.9.28 deduped
114|
115|### 9. Existing developer-memory spec
116|# developer-memory Specification
117|
118|## Purpose
119|Persistent cross-session memory for AI coding agents. All 7 supported agents
120|remember platform decisions across sessions, eliminating the first-5-minutes
121|re-derivation of architectural conventions, past resolutions, and team idioms.
122|## Requirements
123|
124|> **Status**: IMPLEMENTED. Agentmemory server installed and wired to Cursor, Claude Code, Codex, OpenCode, pi; Go deps unchanged.
125|
126|### Requirement: Agentmemory server as developer-memory layer
127|
128|The project SHALL adopt `rohitg00/agentmemory` engine and `@agentmemory/mcp` version `0.9.28` (Apache-2.0, npm `latest` at plan revision) as the shared developer-memory layer for the go-microservices monorepo. One canonical AgentMemory engine SHALL own the shared persistent store, and supported MCP clients SHALL reach it through one MCP Router-owned fail-closed AgentMemory boundary rather than spawning additional direct shims. The boundary SHALL preserve authenticated client identity through a trusted server-derived mapping: native `agentId` arguments SHALL be injected only for tools whose pinned schema supports them, while `memory_save` SHALL receive a reserved server-derived audit concept because the pinned `0.9.28` save schema does not accept or persist `agentId`. A shim fallback store MUST NOT accept or report shared-memory reads or writes.
129|
130|#### Scenario: Agentmemory server is installed locally
131|- **WHEN** a developer runs `make agentmemory-bootstrap && make agentmemory-up`
132|- **THEN** the server starts on `localhost:3111` (REST+MCP) and `localhost:3113` (viewer, loopback-only), with B+ feature flags enabled
133|- **AND** `make agentmemory-doctor` reports 0 red rows
134|
135|#### Scenario: Agentmemory is wired to Cursor
136|
137|### 10. Plugins dir
138|
139|
140|### 11. Upstream plugin.yaml version
141|name: agentmemory
142|version: 0.8.0
143|description: "Persistent cross-session memory for Hermes Agent via agentmemory. 95.2% retrieval accuracy on LongMemEval."
144|author: "Rohit Ghumare"
145|homepage: "https://github.com/rohitg00/agentmemory"
146|hooks:
147|  - prefetch
148|  - sync_turn
149|  - on_session_end
150|  - on_pre_compress
151|  - on_memory_write
152|  - system_prompt_block
153|
154|### 12. Port 3111 check
155|PORT 3111 CLOSED

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

# agentmemory's documented runtime config lives at ~/.agentmemory/.env.
# When agentmemory is launched as a systemd user service (or any other
# process manager that loads that file directly), those values never
# reach an interactive shell. `hermes memory status` then reads
# os.environ in the Hermes CLI process, finds AGENTMEMORY_URL /
# AGENTMEMORY_SECRET unset, and reports the plugin as "Missing" even
# though the service is healthy and live sessions can use it (#250).
#
# Preload the file at plugin-import time using os.environ.setdefault so
# we never override anything the user explicitly set in the shell. The
# preload is best-effort and silent on any failure (file absent,
# unreadable, malformed) — the plugin falls back to its existing default
# (http://localhost:3111) and Hermes status reflects that.
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
- agentmemory server NOT currently running (port 3111 health check fails)
- Hermes plugin NOT installed (~/.hermes/plugins/agentmemory/ doesn't exist)
- Hermes config has no memory.provider set
- .env configured with B+ feature flags, local embeddings, ollama
- Upstream plugin.yaml version: 0.8.0 (plugin is older than agentmemory v0.9.28)

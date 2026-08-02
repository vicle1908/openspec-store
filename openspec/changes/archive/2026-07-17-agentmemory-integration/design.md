# Agentmemory Integration — Design

## Context

TDT now runs a local `agentmemory` service for persistent memory across Claude Code, Codex, and pi sessions. The previous state relied on manually curated memory files and did not provide automatic lifecycle capture or cross-agent recall.

**Implemented state:**
- `@agentmemory/agentmemory` and `@agentmemory/mcp` installed globally at `0.9.24`
- Agentmemory REST worker persisted with ``/Users/lekhanhvinh/Developer/tdt/tdt-meta/config/launchd/com.tdt.agentmemory.plist` deployed to `~/Library/LaunchAgents/com.tdt.agentmemory.plist``
- REST API on `http://localhost:3111`
- Viewer on `http://localhost:3113`
- Claude Code MCP and hooks wired in user config
- Codex MCP and global Desktop hook workaround wired in user config
- pi extension copied into `~/.pi/agent/extensions/agentmemory` and registered in pi settings
- Historical Claude Code import smoke-tested with `agentmemory import-jsonl --max-files 50`

**Constraints:**
- Must work with existing TDT infrastructure: OmniRoute for LLM, Ollama for embeddings
- Must keep credentials in `~/.tdt/.env`, not copied into repo files
- Must be local-first and avoid required external databases
- Must be easy to re-run after agentmemory upgrades

## Goals / Non-Goals

**Goals:**
- Persistent memory across agent sessions
- Automatic observation capture via hooks
- Hybrid search and recall through MCP tools
- TDT OmniRoute gateway for LLM-powered consolidation/compression
- Local Ollama `nomic-embed-text` embeddings
- Real-time viewer for debugging and Replay validation

**Non-Goals:**
- Cloud deployment
- Multi-user/team memory deployment
- Custom iii-engine plugin development
- Full import of every historical Claude Code transcript in one run

## Decisions

### 1. LLM Provider: OmniRoute Gateway

**Decision:** Use TDT OmniRoute gateway with `ai/deepseek-v4-pro[1m]`.

**Rationale:**
- Already deployed in TDT local infrastructure
- Credentials are centralized in `~/.tdt/.env` (`OMNIROUTE_API_KEY`, `OMNIROUTE_URL`)
- One gateway can route to multiple providers
- The large context window is suitable for consolidation and summarization

### 2. Embedding Provider: Ollama `nomic-embed-text`

**Decision:** Use Ollama `nomic-embed-text` with 768 dimensions.

**Operational choice:** Run Ollama as a Homebrew service:

```bash
brew services start ollama
```

This is more reliable than `ollama serve &` from a short-lived shell, which can exit when the parent shell exits.

### 3. Configuration Strategy: Resolved Credentials in `.env`

**Decision:** Keep agentmemory configuration in `~/.agentmemory/.env` with **resolved literal values** (not shell variable references). The LaunchAgent sources `~/.tdt/.env` before starting, making credentials available to the process environment, but agentmemory uses `dotenv` (not `dotenv-expand`), so `${VAR}` syntax inside `.env` files is read as a literal string — producing URLs like `${OMNIROUTE_URL}/v1/chat/completions` which fail to parse.

```bash
# LaunchAgent starts: source ~/.tdt/.env && exec agentmemory
# ~/.agentmemory/.env must contain RESOLVED values, not ${OMNIROUTE_URL} references
```

Correct `~/.agentmemory/.env` pattern:

```bash
# LLM provider — use RESOLVED values from ~/.tdt/.env
OPENAI_API_KEY=<resolved-key>      # NOT ${OMNIROUTE_API_KEY}
OPENAI_BASE_URL=http://localhost:20128/v1    # NOT ${OMNIROUTE_URL}
OPENAI_MODEL=ai/deepseek-v4-pro[1m]

# Embedding provider — Ollama local (no variable references needed)
EMBEDDING_PROVIDER=openai
OPENAI_EMBEDDING_API_KEY=ollama
OPENAI_EMBEDDING_BASE_URL=http://localhost:11434/v1
OPENAI_EMBEDDING_MODEL=nomic-embed-text
OPENAI_EMBEDDING_DIMENSIONS=768
```

**Operational note:** When `~/.tdt/.env` credentials change (e.g., key rotation), update `~/.agentmemory/.env` with the resolved values and restart the LaunchAgent:

```bash
launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/com.tdt.agentmemory.plist
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.tdt.agentmemory.plist
```

### 4. Agent Wiring

**Decision:** Use `agentmemory connect` where it is reliable, and explicit hook/extension wiring where current tooling needs it.

- Claude Code: `agentmemory connect claude-code --force` for MCP, plus 12 explicit hook entries in `~/.claude/settings.json`
- Codex: `agentmemory connect codex --with-hooks --force` for MCP plus global hook workaround
- pi: manual copy of upstream `integrations/pi` because `agentmemory connect pi` reports automatic TypeScript extension copy is not implemented

### 5. Tool Visibility: All Current MCP Tools

**Decision:** Expose all current MCP tools.

Agentmemory `0.9.24` exposes 53 tools through the MCP shim during `tools/list`. The spec and verification scripts now assert that behavior and check required tools such as `memory_smart_search`, `memory_save`, `memory_export`, `memory_audit`, and `memory_governance_delete`.

**Operational detail discovered during live verification:** `memory_governance_delete` expects `memoryIds` as a comma-separated string or array-like list at the API layer, but the MCP client path is most reliably exercised with a comma-separated string. The verification script therefore uses the string form to avoid schema ambiguity across MCP wrappers.

### 6. Lifecycle and Consolidation

**Decision:** Enable consolidation and graph extraction with a 30-day decay threshold.

```bash
CONSOLIDATION_ENABLED=true
CONSOLIDATION_DECAY_DAYS=30
GRAPH_EXTRACTION_ENABLED=true
AGENTMEMORY_TOOLS=all
```

Current status shows graph extraction enabled but `0` graph nodes/edges until richer runtime data is consolidated/extracted. This is acceptable for the integration change because graph query and status paths are verified and the runtime flags are enabled.

### 7. Persistent Startup

**Decision:** Run the agentmemory REST worker as a macOS user LaunchAgent so Codex/Claude/Gemini/etc. can rely on `http://localhost:3111` after restarts.

- LaunchAgent: ``/Users/lekhanhvinh/Developer/tdt/tdt-meta/config/launchd/com.tdt.agentmemory.plist` deployed to `~/Library/LaunchAgents/com.tdt.agentmemory.plist``
- KeepAlive restarts on unsuccessful exits
- Logs are written under `~/.agentmemory/`
- Ollama is managed separately with `brew services start ollama`

### 8. Real-operation E2E verification additions

**Decision:** Add a repeatable end-to-end verification script that exercises real memory save/search/export/delete flows and slot mutation flows using the live MCP shim, not just status checks.

**Why:**
- The earlier checks proved the runtime is alive, but live verification found a schema nuance in `memory_governance_delete` and confirmed slot APIs are operational.
- This gives future operators a concrete smoke test that validates persistence and cleanup after upgrades.

**Script:** `openspec/changes/agentmemory-integration/verify-e2e.sh`

**Coverage:**
- health endpoint
- MCP `tools/list`
- `memory_save`
- `memory_smart_search`
- `memory_export`
- `memory_governance_delete`
- slot create/get/append/replace/delete

## Verification Strategy

1. `verify-install.sh`: CLI version, credentials, Ollama service/model, `agentmemory doctor`
2. `verify-omniroute-ollama.sh`: live OmniRoute chat completion and live Ollama embedding dimension
3. `verify-mcp.sh`: REST health, viewer reachability, MCP stdio `tools/list` with 53 tools
4. `verify-hooks.sh`: Claude hook config count, installed hook scripts, audit endpoint
5. OpenSpec: `openspec validate agentmemory-integration --strict`

## Risks / Trade-offs

- **`dotenv` does NOT expand shell variable references** (`${VAR}`). All env values must be resolved literals in `~/.agentmemory/.env`.
- If OmniRoute is down, LLM-powered compression/consolidation can fail, but observations can still be captured.
- If Ollama is stopped, embeddings fail; `brew services start ollama` is the supported fix.
- Claude Code plugin marketplace remains the preferred upstream installation path, but explicit hooks are currently documented because they are easy to inspect and refresh.
- Codex Desktop plugin-local hooks may be silent; global `~/.codex/hooks.json` is the implemented workaround.

## Rollback Plan

```bash
agentmemory stop
npm uninstall -g @agentmemory/agentmemory @agentmemory/mcp
brew services stop ollama  # only if no other TDT tooling needs it
rm -rf ~/.agentmemory      # optional destructive cleanup
```

Remove the agentmemory entries from Claude, Codex, and pi user configs if fully uninstalling.

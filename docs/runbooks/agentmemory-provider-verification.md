# Runbook: agentmemory LLM + Embedding Providers

## Overview

The agentmemory runtime (`~/.agentmemory`) uses two independent providers that
must both be healthy for its LLM-backed features and vector recall to work:

- **LLM provider** — compression, summarization, graph extraction, consolidation.
- **Embedding service** — vector indexing for semantic recall.

Both failures are **silent**: `agentmemory status` reports capability presence
from configuration, not from working behavior. Verify with real signals (below).

## 1. Runtime Configuration

Provider settings live in `~/.agentmemory/.env`, loaded at boot by the launchd
unit `com.agentmemory.server`. The unit injects only `PATH`, `HOME`, `CI`, and
`AGENTMEMORY_URL`, so all keys and secrets must be **in `.env`**.

```dotenv
# LLM (must honor the system role; see section 2)
OPENAI_API_KEY=<omniroute key>
OPENAI_BASE_URL=http://localhost:20128/v1
OPENAI_MODEL=auto/best-coding

# Embeddings (local Ollama)
EMBEDDING_PROVIDER=openai
OPENAI_EMBEDDING_API_KEY=ollama
OPENAI_EMBEDDING_BASE_URL=http://localhost:11434/v1
OPENAI_EMBEDDING_MODEL=nomic-embed-text
OPENAI_EMBEDDING_DIMENSIONS=768

# Bounds (OmniRoute can be slow under load)
OPENAI_TIMEOUT_MS=120000
AGENTMEMORY_LLM_TIMEOUT_MS=120000
```

Back up before changes: `cp -p ~/.agentmemory/.env ~/.agentmemory/.env.pre-<label>-$(date -u +%Y%m%dT%H%M%SZ)`.
Restart: `launchctl kickstart -k gui/$(id -u)/com.agentmemory.server`.

## 2. LLM Provider Selection (system-role contract)

agentmemory always sends its structured-output instructions as a
`{role: "system"}` message and parses a fixed XML envelope from the reply
(`<observation>` containing `<type>` and `<title>`). The endpoint **must honor
the `system` role**.

- **Verified working**: OmniRoute `http://localhost:20128/v1` (OpenAI dialect).
- **Not compatible**: `api.phanmemvip.shop` — returns HTTP 200 but **drops the
  `system` role**, so the model replies conversationally and every parse fails.

Use an `auto/*` combo so routing survives a single upstream being disconnected.
A specific alias (e.g. `Claude-Fable.8-flash-high`) may 400 while its upstream is
offline: `"Unable to determine provider for model ..."`.

Base URL must be bare (no method path); the client appends `/chat/completions`.

## 3. Embedding Service (Ollama, login-supervised)

The embedding backend runs as a Homebrew-managed login service (same pattern as
other `homebrew.mxcl.*` services on this machine):

- Service label: `sh.brew.ollama` → `~/Library/LaunchAgents/sh.brew.ollama.plist`
  (`RunAtLoad=true`, `KeepAlive=true`).
- Model store: `~/.ollama/models` (persists across restarts; no re-download).
- Endpoint: `http://localhost:11434/v1`, model `nomic-embed-text`, 768 dims.

Commands:

```bash
brew services start ollama     # enable + start at login
brew services restart ollama   # restart
brew services stop ollama      # stop (and disable login start)
brew services list | grep ollama
```

## 4. Verification Procedure

**Embedding endpoint:**

```bash
curl -sS -X POST http://localhost:11434/v1/embeddings \
  -H 'Content-Type: application/json' \
  -d '{"model":"nomic-embed-text","input":"ping"}'
# expect dims == 768
```

**LLM system-role + XML contract:** send a request with a `system` instruction
and a `user` observation to `http://localhost:20128/v1/chat/completions`; expect
HTTP 200 whose content contains `<observation>` with `<type>` and `<title>`.

**Live capability signals** (the authoritative check):

- Server health: `GET http://localhost:3111/agentmemory/health` — inspect
  `functionMetrics` for `mem::compress` (success count must be positive and
  rising) and `circuitBreaker.state` (`closed`).
- Server log `~/.agentmemory/log/launchd-stderr.log`:
  - success: `Observation compressed {..., "qualityScore": N, "retried": false}`
  - success: `Memory saved {..., "type": ...}` with **no** adjacent embed warning
  - failure: `Compression failed`, `Failed to parse compression XML`,
    `vector-index add: embed failed — skipping`

**Trigger real work:**

```bash
# LLM compression path
echo '{"hookType":"post_tool_use","toolName":"Read","toolInput":{"file_path":"/tmp/x.ts"},"toolResponse":"read 40 lines","cwd":"/Users/androidteam/Developer","sessionId":"verify-1"}' \
  | AGENTMEMORY_URL=http://localhost:3111 node ~/.npm-global/lib/node_modules/@agentmemory/agentmemory/dist/hooks/post-tool-use.mjs
# Embedding path
curl -sS -X POST http://localhost:3111/agentmemory/remember \
  -H 'Content-Type: application/json' \
  -d '{"content":"verification probe","type":"fact"}'
```

## 5. Success Criteria

- Embedding endpoint returns a 768-length vector.
- New memory writes emit **no** `embed failed — skipping` warning.
- `mem::compress` reports a positive success count; new observations log
  `Observation compressed` with a quality score and `retried: false`.
- No new `Compression failed` / `Failed to parse compression XML` entries.

## 6. Rollback

Restore the `.env` backup and restart the launchd unit. If reverting supervision,
`brew services stop ollama`.

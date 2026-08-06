# agentmemory-feature-flags Specification

## ADDED Requirements

### Requirement: The .env template sets the B+ feature flag set
The committed `infrastructure/agentmemory.env.template` SHALL set the following flags by default: `AGENTMEMORY_TOOLS=all`, `GRAPH_EXTRACTION_ENABLED=true`, `SNAPSHOT_ENABLED=true`, `CONSOLIDATION_ENABLED=true` (which is default-on but asserted explicitly), `AGENTMEMORY_SLOTS=memory` (a slot name, not a boolean — the value `memory` is the named slot agentmemory claims), `AGENTMEMORY_REFLECT=true`, `AGENTMEMORY_INJECT_CONTEXT=true`, `LESSON_DECAY_ENABLED=true`, and `AGENTMEMORY_AGENT_SCOPE=shared`. The template SHALL set `EMBEDDING_PROVIDER=local` (free, ships with the package). The template SHALL NOT set `AGENTMEMORY_AUTO_COMPRESS=true`, SHALL NOT set `AGENTMEMORY_ALLOW_AGENT_SDK=true`, and SHALL NOT set `CLAUDE_MEMORY_BRIDGE=true`. Each of the asserted flags SHALL be present and uncommented in the generated `~/.agentmemory/.env`. **Note**: `AGENTMEMORY_REFLECT`, `LESSON_DECAY_ENABLED`, and `AGENTMEMORY_AGENT_SCOPE` were not found in the live `.env.example` at the time of research; they are set in the template on an ambitious basis and the `make agentmemory-doctor` check validates their effect empirically.

#### Scenario: All B+ flags are present in the generated .env
- **WHEN** the bootstrap script generates `~/.agentmemory/.env` from the template
- **THEN** `grep -E '^(AGENTMEMORY_TOOLS=all|GRAPH_EXTRACTION_ENABLED=true|SNAPSHOT_ENABLED=true|CONSOLIDATION_ENABLED=true|AGENTMEMORY_SLOTS=memory|AGENTMEMORY_REFLECT=true|AGENTMEMORY_INJECT_CONTEXT=true|LESSON_DECAY_ENABLED=true|AGENTMEMORY_AGENT_SCOPE=shared|EMBEDDING_PROVIDER=local)$' ~/.agentmemory/.env` returns 10 lines

#### Scenario: Disallowed flags are absent
- **WHEN** the bootstrap script generates `~/.agentmemory/.env` from the template
- **THEN** `grep -E '^(AGENTMEMORY_AUTO_COMPRESS=true|AGENTMEMORY_ALLOW_AGENT_SDK=true|CLAUDE_MEMORY_BRIDGE=true)$' ~/.agentmemory/.env` returns zero lines and any commented-out line containing those keys is treated as absent

### Requirement: LLM provider defaults to local Ollama with qwen2.5-coder:7b
The template SHALL default the LLM provider to a local Ollama server at `http://localhost:11434/v1` using `qwen2.5-coder:7b` as the model. The template SHALL include `OPENAI_API_KEY=ollama` (any non-empty placeholder, Ollama ignores the value), `OPENAI_BASE_URL=http://localhost:11434/v1`, and `OPENAI_MODEL=qwen2.5-coder:7b`. The template SHALL include `OPENAI_REASONING_EFFORT=none` to handle Ollama Cloud thinking models that may mirror the OpenAI reasoning schema. The bootstrap script SHALL detect a running Ollama server with a 2 s curl probe and SHALL emit a yellow warning (not a failure) if Ollama is not reachable.

#### Scenario: Ollama is reachable
- **WHEN** the bootstrap script runs and `curl -fsS http://localhost:11434/api/tags` returns 200
- **THEN** the script reports `LLM provider: Ollama at http://localhost:11434/v1 (qwen2.5-coder:7b)` and exits 0

#### Scenario: Ollama is unreachable
- **WHEN** the bootstrap script runs and `curl -fsS http://localhost:11434/api/tags` fails or times out at 2 s
- **THEN** the script emits a yellow warning `Ollama is not running; the Stop-hook compression pass will be a no-op until you start Ollama and pull qwen2.5-coder:7b` and continues with exit 0

#### Scenario: Developer overrides to OpenRouter
- **WHEN** a developer edits `~/.agentmemory/.env` to set `OPENAI_API_KEY=sk-or-...` and `OPENAI_BASE_URL=https://openrouter.ai/api/v1` and `OPENAI_MODEL=deepseek/deepseek-v4-pro` and restarts the server
- **THEN** the server uses OpenRouter as the LLM provider and `agentmemory-doctor` reports the active provider as `OpenRouter (deepseek/deepseek-v4-pro)` in green

### Requirement: B+ flags produce a verifiable external behavior change
Each enabled B+ feature SHALL produce an observable effect on the agentmemory server's behavior. A `make agentmemory-doctor` run after bootstrap SHALL assert each effect is present and SHALL exit non-zero if any of the asserted behaviors is missing.

#### Scenario: GRAPH_EXTRACTION_ENABLED produces a non-empty knowledge graph
- **WHEN** the server is running with `GRAPH_EXTRACTION_ENABLED=true` and at least 3 observations are recorded under `project=go-microservices-platform`
- **THEN** `POST /agentmemory/graph/query` with `{"query":"<any>"}` returns at least 1 node and the response includes a `nodes` array of length ≥ 1

#### Scenario: SNAPSHOT_ENABLED produces a commit
- **WHEN** the server is running with `SNAPSHOT_ENABLED=true` and a developer calls `memory_snapshot_create` via MCP
- **THEN** the tool returns a `snapshot_id` and `GET /agentmemory/snapshots/<snapshot_id>` returns the snapshot's metadata including a git commit hash

#### Scenario: AGENTMEMORY_SLOTS is editable
- **WHEN** the server is running with `AGENTMEMORY_SLOTS=memory` and a developer calls `memory_slot_set` with `{"slot":"project_context","value":"<text>"}` via MCP
- **THEN** the tool returns 200 and `memory_slot_get` with `{"slot":"project_context"}` returns the same text

#### Scenario: AGENTMEMORY_REFLECT populates pending_items
- **WHEN** the server is running with `AGENTMEMORY_REFLECT=true` and the Stop hook fires after a session with at least one new observation
- **THEN** the `pending_items` slot is updated within 30 s of the Stop hook firing

#### Scenario: LESSON_DECAY_ENABLED causes stale memory to be marked
- **WHEN** the server is running with `LESSON_DECAY_ENABLED=true` and a memory was last accessed more than 30 days ago
- **THEN** `GET /agentmemory/memories/<id>` includes `decay_score < 0.5` in its metadata

### Requirement: Shared agent scope is the default
The template SHALL set `AGENTMEMORY_AGENT_SCOPE=shared`, which means writes are tagged with `agentId` but recall does NOT filter by it. Every agent sees every other agent's writes, and the audit log records who said what. A developer MAY switch to `isolated` by editing `~/.agentmemory/.env`; the bootstrap script SHALL document this in a comment and SHALL NOT switch it without explicit developer action.

#### Scenario: Default is shared
- **WHEN** the generated `~/.agentmemory/.env` is inspected
- **THEN** the line `AGENTMEMORY_AGENT_SCOPE=shared` is present and uncommented

#### Scenario: Shared mode allows cross-agent recall
- **WHEN** the server is running with `AGENTMEMORY_AGENT_SCOPE=shared` and a developer runs `/recall <query>` from Claude Code
- **THEN** the response MAY include observations written by Cursor, Codex CLI, or any other agent in the project namespace, each tagged with its origin `agentId`

#### Scenario: Audit log records the origin
- **WHEN** a developer runs `GET /agentmemory/audit?limit=100` after a multi-agent session
- **THEN** each row includes an `agentId` field identifying the originating agent

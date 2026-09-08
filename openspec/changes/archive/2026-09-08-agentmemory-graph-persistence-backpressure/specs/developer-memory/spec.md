## MODIFIED Requirements

### Requirement: Agentmemory server as developer-memory layer

The project SHALL use rohitg00/agentmemory engine and @agentmemory/mcp version 0.9.29 as the shared developer-memory layer. Provider configuration SHALL use the shopapikey-backed LLM endpoint with consistent model naming and bounded timeouts. Graph extraction and persistence SHALL be bounded and failure-isolated so graph backlog or state-store timeout does not block observation capture or session completion.

#### Scenario: Agentmemory server is installed locally

- WHEN a developer runs agentmemory-bootstrap and agentmemory-up
- THEN the server starts on localhost:3111 and localhost:3113 with B+ feature flags
- AND agentmemory-doctor reports 0 red rows

#### Scenario: Agentmemory is wired to Cursor

- WHEN Cursor starts with the shared MCP Router configured
- THEN the Cursor tool palette shows the router-exposed AgentMemory tools
- AND Cursor has no separate direct agentmemory MCP server registration

#### Scenario: Agentmemory is wired to Claude Code

- WHEN Claude Code starts with the AgentMemory hooks and shared MCP Router configured
- THEN the Claude Code hooks fire on SessionStart, PreToolUse, PostToolUse, PreCompact, and Stop events
- AND memory_smart_search through MCP Router returns engine-backed memories

#### Scenario: Agentmemory is wired to Codex CLI

- WHEN Codex CLI starts with the AgentMemory hooks and shared MCP Router configured
- THEN Codex CLI hooks fire on SessionStart, UserPromptSubmit, PreToolUse, PostToolUse, PreCompact, and Stop

#### Scenario: Agentmemory is wired to OpenCode

- WHEN OpenCode starts with the shared MCP Router configured
- THEN the OpenCode tool list includes the router-exposed AgentMemory tools

#### Scenario: Agentmemory is wired to pi

- WHEN pi starts with the AgentMemory extension installed
- THEN the extension registers memory_health, memory_search, and memory_save tools

#### Scenario: Agentmemory is wired to Hermes

- WHEN Hermes starts with memory.provider: agentmemory in config and the agentmemory plugin enabled
- THEN the plugin provides lifecycle hooks and memory tools
- AND LLM compression uses fable-5 via shopapikey
- AND embeddings use nomic-embed-text locally
- AND the plugin gracefully degrades when the agentmemory server is unavailable

#### Scenario: Canonical AgentMemory engine is unavailable

- WHEN the AgentMemory boundary cannot reach the canonical engine health endpoint on loopback port 3111
- THEN shared-memory reads and writes fail with an engine-unavailable status
- AND no local fallback store accepts the operation

#### Scenario: Cross-client shared recall is verified

- WHEN two distinct authenticated test clients write uniquely tagged observations through MCP Router
- THEN the engine-backed results preserve distinct server-derived audit attribution
- AND caller-supplied identity fields cannot override the server-derived attribution

#### Scenario: Provider or graph persistence instability does not block session completion

- WHEN the LLM provider is returning 502 errors or timing out, or graph persistence is queued, deferred, or timing out
- THEN session end processing SHALL complete successfully
- AND observation capture SHALL continue uninterrupted
- AND summarization and graph attempts SHALL be logged as failed or deferred without blocking

#### Scenario: Graph backlog is bounded

- WHEN a session or queued workload contains more observations than the graph batch capacity
- THEN graph extraction SHALL use bounded batches and concurrency
- AND graph work SHALL not create unbounded memory pressure or delay session completion

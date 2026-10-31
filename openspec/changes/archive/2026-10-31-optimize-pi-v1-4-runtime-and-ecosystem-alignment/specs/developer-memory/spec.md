# developer-memory Specification Delta

## ADDED Requirements

### Requirement: Pi AgentMemory Extension Secret Fallback and Cache-Safe Prompt Injection

The Pi AgentMemory extension (`~/.pi/agent/extensions/agentmemory/index.js`) SHALL resolve `AGENTMEMORY_SECRET` from `process.env.AGENTMEMORY_SECRET` with a fallback reader for `~/.agentmemory/.env`, SHALL bound HTTP requests with a 2,500 ms timeout, and SHALL unconditionally append `TOOL_GUIDANCE` to `systemPromptOptions.promptGuidelines` while returning recalled context via a non-displayed custom message without overwriting `systemPrompt`.

#### Scenario: Authenticated recall and save succeed when AGENTMEMORY_SECRET is stripped from process.env
- **WHEN** Pi executes `memory_search` or `memory_save` in a child environment where `process.env.AGENTMEMORY_SECRET` is unset but `~/.agentmemory/.env` defines `AGENTMEMORY_SECRET`
- **THEN** the extension SHALL read `AGENTMEMORY_SECRET` from `~/.agentmemory/.env` and send `Authorization: Bearer <secret>` with a 2,500 ms `AbortSignal.timeout` to `http://localhost:3111/agentmemory/*`
- **AND** `memory_search` SHALL return engine-backed memories rather than failing with HTTP 401

#### Scenario: Pre-run memory recall preserves Pi 1.4.0 structured system prompt sections and prompt cache
- **WHEN** `before_agent_start` runs on a user prompt and `smart-search` returns matching memories
- **THEN** the handler SHALL append `TOOL_GUIDANCE` to `event.systemPromptOptions.promptGuidelines` (if not already present) before any early return and return `{ message: { customType: "agentmemory-recall", content: recallBlock, display: false } }`
- **AND** the handler SHALL NOT return a top-level `systemPrompt` property that sets `forceSystemPrompt` or invalidates the provider prompt cache across turns

#### Scenario: Custom message runs preserve promptGuidelines while skipping duplicate recall queries
- **WHEN** `before_agent_start` fires with `event.messageType === "custom"`
- **THEN** the handler SHALL still ensure `TOOL_GUIDANCE` is present in `event.systemPromptOptions.promptGuidelines` so system prompt sections do not diff
- **AND** the handler SHALL skip querying `smart-search` and SHALL NOT inject a duplicate `agentmemory-recall` message

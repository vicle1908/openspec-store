## Purpose

Provides efficient runtime behavior for long-lived and unattended full-access Hermes conversations so prompt caching, compression, delegation, and recovery remain useful without allowing repeated failures or excessive fan-out to consume unbounded resources.

## ADDED Requirements

### Requirement: Prompt-cache-safe changes SHALL be staged at session boundaries

Changes to toolsets, system-prompt inputs, profile context, or model/provider selection SHALL be applied at a new session or an explicitly supported reset boundary rather than mutating the active conversation's cached prefix.

#### Scenario: Tool policy changes
- **WHEN** an operator changes a built-in toolset or MCP tool selection
- **THEN** the change is recorded as requiring a fresh session/reset before it is considered active

#### Scenario: Active conversation continues
- **WHEN** a conversation continues without a reset after a configuration edit
- **THEN** the existing session retains its prior prompt/tool context and does not silently mix old and new tool schemas

### Requirement: Context compression SHALL remain enabled for long-lived sessions

The default profile SHALL retain automatic context compression and SHALL use the installed model's verified context capacity rather than guessing a context length from generic model names.

#### Scenario: Conversation approaches capacity
- **WHEN** the active context reaches the configured compression threshold
- **THEN** Hermes compresses the conversation according to its configured target ratio and preserves the continuation lineage

#### Scenario: Provider context is ambiguous
- **WHEN** the custom provider does not expose a reliable context limit
- **THEN** the operator verifies the provider limit before setting `model.context_length`, and Hermes does not claim a guessed value as authoritative

### Requirement: Unattended loops SHALL be circuit-breakable

The shared default profile SHALL enable tool-loop hard stops and SHALL configure finite positive values at `tool_loop_guardrails.loop_caps.max_web_searches` and `tool_loop_guardrails.loop_caps.max_subagents`.

#### Scenario: Repeated tool failure occurs
- **WHEN** the same failing tool call or same-tool failure reaches the configured hard-stop threshold
- **THEN** Hermes blocks further matching calls for that turn and returns an actionable diagnostic

#### Scenario: Search or delegation fan-out spirals
- **WHEN** a single turn reaches its web-search or subagent cap
- **THEN** the offending call is blocked and the turn stops cleanly rather than continuing until the general iteration budget is exhausted

#### Scenario: Cap keys are validated
- **WHEN** the optimized configuration is inspected
- **THEN** both cap values are present under `tool_loop_guardrails.loop_caps`, are greater than zero, and are not incorrectly written as top-level guardrail keys

### Requirement: Delegation SHALL be bounded and purposeful

The default profile SHALL use `delegation.max_concurrent_children=3`, `orchestrator_enabled=true`, `max_spawn_depth=2`, `child_timeout_seconds=0`, and `max_iterations=50`. A zero child timeout SHALL be treated as disabling the wall-clock timeout only, not as removing concurrency, iteration, loop, or stuck-child controls.

#### Scenario: Deprecated concurrency key is present
- **WHEN** Hermes loads a configuration containing `delegation.max_async_children`
- **THEN** migration removes the deprecated key and uses `delegation.max_concurrent_children` as the single effective cap

#### Scenario: Delegation reaches concurrency capacity
- **WHEN** a new background delegation would exceed the configured cap
- **THEN** Hermes rejects or falls back according to its supported behavior without silently queueing unbounded work

#### Scenario: Child exceeds policy
- **WHEN** a child agent exceeds its configured iteration or optional wall-clock policy
- **THEN** the parent receives a bounded failure summary and the child does not continue running indefinitely

#### Scenario: Nested orchestration is requested
- **WHEN** an authorized session requires a child agent to coordinate a further child within the configured depth
- **THEN** Hermes permits the nested delegation until the configured depth or concurrency cap is reached

### Requirement: Operational efficiency SHALL be observable

The operator SHALL be able to inspect per-turn tool activity, token/cost indicators where supported, delegation status, gateway logs, and session statistics without reading secret values.

#### Scenario: Reliability review is performed
- **WHEN** the operator audits the optimized installation after a representative workload
- **THEN** the audit can compare tool-loop warnings, provider timeouts, context failures, session growth, and delegation outcomes before and after the change

#### Scenario: A tool call fails
- **WHEN** a file mutation, provider call, MCP call, or gateway operation fails
- **THEN** the resulting diagnostic is distinguishable from a successful operation and does not rely solely on the model's closing summary

### Requirement: Full MCP capability SHALL use discoverable progressive disclosure

The default profile SHALL keep every authorized MCP and plugin operation enabled while deferring eligible non-core schemas through Hermes Tool Search. The catalog SHALL remain discoverable by name or server summary, and the bridge SHALL remain scoped to the session's granted toolsets.

#### Scenario: Large MCP catalog is assembled
- **WHEN** the profile exposes the verified MCP Router inventory
- **THEN** core Hermes tools remain eager, eligible MCP/plugin schemas defer, and `hermes prompt-size` records the fixed prompt budget without an inference call

#### Scenario: Deferred operation is needed
- **WHEN** an authorized session needs an MCP operation whose schema is not eager
- **THEN** it can find the operation with `tool_search`, load its exact schema with `tool_describe`, and invoke it through `tool_call` without bypassing the underlying policy or audit hooks

#### Scenario: Full-access discoverability is verified
- **WHEN** a fresh CLI or Telegram session is tested after tool changes
- **THEN** representative read-only and mutating MCP operations are discoverable by exact runtime name and no authorized operation is removed merely to reduce prompt size

### Requirement: Unattended cron SHALL be attributable, deliverable, and cost-observable

Every agent-backed cron job SHALL have an explicit delivery target, workdir, and provider/model policy. Jobs producing a fixed script-defined message without reasoning SHALL use supported script-only mode. Execution and delivery SHALL be verified from scheduler history and target receipt rather than inferred from schedule presence.

#### Scenario: Global model changes after job creation
- **WHEN** an unpinned job's snapshotted provider/model no longer matches the global default
- **THEN** the job fails closed without an inference call and alerts the operator to pin the intended provider/model

#### Scenario: Script-only watchdog fires
- **WHEN** a deterministic threshold or heartbeat condition requires a fixed notification
- **THEN** the job runs with `no_agent` and delivers non-empty stdout without paying for unnecessary inference

#### Scenario: Cron completion is verified
- **WHEN** a representative job finishes
- **THEN** cron history records terminal run status and the explicit Telegram target receives the final response; missing delivery remains a failure even if generation completed

### Requirement: Gateway completion and interruption recovery SHALL be bounded and visible

The default-profile Telegram gateway SHALL retain periodic long-turn notifications, finite inactivity warning/timeout, finite build wait, finite startup-restore inbound gate, finite interrupted-turn freshness, immediate bounded restart cleanup, and the durable final-response delivery ledger.

#### Scenario: Long task remains active
- **WHEN** a Telegram turn exceeds the notification interval while continuing to make progress
- **THEN** Hermes emits bounded “still working” feedback without terminating the active turn solely for elapsed wall time

#### Scenario: Gateway restarts after finalization but before acknowledgement
- **WHEN** a final response has a pending delivery obligation and the prior gateway owner is no longer alive
- **THEN** the new gateway retries within the ledger's bounded at-least-once policy and marks duplicate ambiguity honestly

#### Scenario: Interrupted work is stale
- **WHEN** the next message arrives after the configured auto-continue freshness window
- **THEN** Hermes does not revive the unrelated interrupted task merely because an old transcript marker exists

#### Scenario: Startup restore is pathologically slow
- **WHEN** resumed work exceeds the startup-restore drain timeout
- **THEN** the inbound gate releases while duplicate-agent protection remains active, so unrelated channels do not remain blocked indefinitely

### Requirement: Autonomous skill growth SHALL remain auditable and recoverable

The default profile SHALL retain autonomous skill writes and curator inactivity maintenance while keeping LLM consolidation opt-in. A real curator mutation SHALL require a valid pre-run skill snapshot, and archival SHALL remain reversible.

#### Scenario: Curator behavior is previewed
- **WHEN** the operator runs the supported curator dry-run
- **THEN** candidate stale/archive transitions are reported without mutating skills or invoking forced consolidation

#### Scenario: Automatic curation is eligible
- **WHEN** a real inactivity pass is due
- **THEN** Hermes creates the configured pre-run skill snapshot before any transition and does not run paid consolidation while `curator.consolidate=false`

#### Scenario: Archived skill is still required
- **WHEN** review finds that a skill was archived but remains useful
- **THEN** the operator can identify a verified curator snapshot or use the supported per-skill restore path before claiming the learning state recoverable

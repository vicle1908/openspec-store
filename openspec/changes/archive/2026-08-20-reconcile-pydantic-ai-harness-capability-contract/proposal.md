## Why

The current Pydantic AI Harness 0.23 integration contradicts its public guidance and archived acceptance claims: several capabilities are silently default-on, configuration fields are unread, conversation search is detached from runtime persistence, docs ToolGuardrails are not installed, and retained tests prove construction rather than production behavior. A single corrective contract is needed now so source, docs, specs, dependencies, and executable evidence describe the same supported behavior.

## What Changes

- **BREAKING:** Make harness behavior explicit at the public `build_agent(..., capabilities=[...])` composition boundary; remove hidden default activation of TieredCompaction, SystemReminders, and SpendLimits unless an existing normative default is deliberately ratified in the delta specs.
- Remove the unread harness-capability dictionaries from `AgentConfig` and their compatibility tests/docs; keep supported declarative capability composition in Pydantic AI `AgentSpec` rather than introducing a second configuration projection.
- Preserve caller-supplied capability identity, order, authority validation, and supported Pydantic AI composition semantics without private upstream access.
- Make ConversationSearch consume the same caller-owned SnapshotStore/StepPersistence store used by the runtime, default shared-store search to conversation scope, prove cross-conversation isolation, and fail construction when a declared shared-history source is unavailable rather than substituting a disconnected store.
- Install bounded write-path, shell-command, and result-redaction ToolGuardrails in docs-sync generation/full-sync production composition; bind them to the exact production tool names/arguments, reuse the canonical path resolver, and emit one redacted audit decision while preserving containment hooks, approval gates, and exactly-once write authority as the controlling security layers.
- Retain the `[dynamic-workflow]` extra only in agent-core when public `build_agent` composition, deterministic execution, and bounded runtime-authoring authority all pass; remove it from agent-harness and agent-docs-sync unless a direct supported consumer is added with behavioral compatibility evidence.
- Correct the DynamicWorkflow/Monty contract to the installed harness `0.23.0` requirement (`pydantic-monty>=0.0.19`) and eliminate stale `0.0.18` claims.
- Replace import/constructibility checks with public-boundary behavioral tests for compaction, reminders, priced spend enforcement, planning, shared-store conversation search, advisor consultation/fallback, and ToolGuardrail execution.
- Reconcile current historical compaction specs and harness documentation with the typed public API, canonical non-deprecated symbols, accepted constructor values, and executable snippets.
- Maintain a corrective ledger that references the five reviewed inconsistent archived dependency/capability changes without rewriting their archived artifacts.
- Treat `establish-agent-observability-contract` as the sole owner of telemetry activation, trace/log correlation, and evaluation linkage; this change only proves capability behavior and emits compatible evidence.

## Non-goals

- No upgrade beyond the frozen `pydantic-ai==2.32.0` and `pydantic-ai-harness==0.23.0` compatibility tuple.
- No LLM provider, credential, `TDT_HOME`, model-selection, or canonical profile precedence change.
- No replacement of LangGraph orchestration, DBOS scheduling, approval state, or docs-sync lifecycle identity.
- No implementation of the active observability change.
- No edits to archived change artifacts and no reuse of stale GitNexus risk counts as acceptance evidence.

## Capabilities

### New Capabilities

None. The upstream capabilities already exist; this change reconciles their workspace contract.

### Modified Capabilities

- `agent-core-capabilities`: Replace the newly archived default-on AgentRuntime capability requirements with explicit typed composition, shared persistence, and public behavioral acceptance.
- `agent-compaction`: Replace historical dictionary-based requirements with typed opt-in compaction and executable behavior requirements.
- `_standalone/harness-compaction`: Remove the obsolete `harness_config` contract and retain only typed composition and layering requirements.
- `agent-step-persistence`: Require ConversationSearch and continuation to share the caller-owned persistence source with conversation-scoped isolation when shared history is declared.
- `agent-guardrails`: Require docs-sync ToolGuardrails to target the exact production tools, reuse containment policy, and emit redacted audit evidence without weakening containment or approval authority.
- `_standalone/agent-docs-harness`: Align documentation requirements with the actual public module paths, supported extras, defaults, and composition examples.
- `agent-framework-verification`: Require behavioral, public-boundary, exact-identity evidence for each claimed harness capability and corrective archive ledger entry.

## Impact

- **agent-core owner:** `sdk.build_agent`, `BaseAgent`, `AgentRuntime`, capability factories, dependency extras, docs, and behavioral tests.
- **agent-docs-sync owner:** production capability assembly, ToolGuardrail factories/call sites, dependency extras, docs, and containment-aware behavioral tests.
- **agent-harness owner:** dependency-extra cleanup and compatibility verification; no new runtime ownership of upstream harness capabilities.
- **openspec-store owner:** seven delta-spec paths, corrective ledger, validation, sync, and archive evidence, including the current `agent-core-capabilities` main-spec correction.
- GitNexus currently reports LOW advisory blast radius, but its indexes are stale; apply must refresh or replace that evidence with current direct callers and focused tests before editing.
- This change depends on accepted results from `restore-agent-pydantic-quality-gates` and `enforce-openspec-archive-readiness-gates`; implementation begins only after both gates are available from the dedicated planning worktree.
- **integration coordinator:** run from `/Users/androidteam/Developer`, load this change from `/Users/androidteam/Developer/.worktrees/pydantic-ai-openspec-followups`, and treat agent-core, docs-sync, harness, and store as separately authorized writer packets.

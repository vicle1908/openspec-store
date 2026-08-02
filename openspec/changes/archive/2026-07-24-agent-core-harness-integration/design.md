## Context

agent-core is a shared agent runtime with 10 capability modules, 7 built-in tools, and a skill system. It uses pydantic-ai as its core engine and pydantic-ai-harness for capabilities (compaction, guardrails, subagents, planning). The skills directory is split across `.agents/skills/` (103 items) and `.claude/skills/` (54 items) with 28 identical overlaps. The system lacks DynamicWorkflow support for reactive orchestration.

**Verified current state:**
- `_ai/agent.py` wraps pydantic-ai Agent with `_build_harness_capabilities()` for opt-in harness features
- `AgentRuntime.__init__()` accepts `harness_config: dict[str, Any] | None = None` parameter
- `BaseAgent.__init__()` does NOT accept `harness_config` — this is a gap that needs fixing
- `skill_system/` provides agentskills.io-compatible loading + deterministic matching (60% keyword + 40% overlap + effectiveness multiplier)
- `memory/` has 3 layers: ContextMemory, ScratchMemory, PostgresMemory, plus FeedbackStore
- `orchestration/` uses LangGraph with Postgres checkpointing
- `config.yaml.example` does NOT have harness capability config sections (context_compaction, dynamic_workflow)
- No examples use `harness_config` — it's only documented in `docs/harness-integration.md`

## Goals / Non-Goals

**Goals:**
- Consolidate skills into single canonical directory (`.agents/skills/`)
- Add DynamicWorkflow capability for model-driven orchestration
- Add SubAgents capability for declarative sub-agent delegation
- Add Planning capability for task decomposition
- Replace tool_registry built-in tools with harness FileSystem + Shell
- Maintain backward compatibility — no breaking changes to existing agents

**Non-Goals:**
- Replacing LangGraph with DynamicWorkflow (both coexist)
- Rewriting the skill matcher or profile system
- Changing the memory facade API
- Changing the agent loop or ReAct pattern
- Adding harness CodeMode capability (future exploration)
- Replacing memory/context.py with harness compaction (complementary)

## Decisions

### Decision 1: Skills merge — `.agents/skills/` as canonical, symlink `.claude/skills/`

**Choice:** Move `.claude/skills/` content into `.agents/skills/`, replace directory with symlink.

**Alternatives considered:**
- Keep both directories, sync periodically → rejected (drift risk, maintenance burden)
- Make `.agents/skills/` a symlink to `.claude/skills/` → rejected (Claude Code owns `.claude/`, agent-core owns `.agents/`)
- Use a shared third directory → rejected (adds indirection, breaks existing paths)

**Rationale:** `.agents/skills/` is the agent-core canonical location. Claude Code reads `.claude/skills/` natively. A symlink gives Claude Code access to all skills while maintaining single source of truth.

**Verified:** 28 overlapping skills are identical (diff confirmed). 25 skills only in `.claude/skills/` need moving. 3 existing symlinks already work (commit-context, commit-history, forget).

### Decision 2: DynamicWorkflow via Monty sandbox

**Choice:** Add `pydantic-monty` + `pydantic-ai-harness[dynamic-workflow]` as dependencies. Wire into `_build_harness_capabilities()` as opt-in config block.

**Alternatives considered:**
- Roll custom code execution sandbox → rejected (Monty is purpose-built, Rust-compiled, battle-tested by Pydantic)
- Use Docker-based sandbox → rejected (heavy, slow startup, infrastructure overhead)
- Skip sandbox entirely → rejected (security requirement for model-written code)

**Rationale:** Monty is ~4.5MB, no CPython dependency, worker isolation via subprocesses, resource limits built in. It's the official Pydantic solution for this exact use case. pydantic-ai-harness requires `pydantic-monty>=0.0.16`. Monty v0.0.19 adds user-defined classes, async memory limits, and subprocess pool execution.

**Implementation details (Monty v0.0.19):**
- Monty supports: `asyncio`, `json`, `re`, `datetime`, `sys`, `os`, `typing`, `unicodedata`
- Monty v0.0.19 NOW SUPPORTS: user-defined classes, class decorators, `iter(callable, sentinel)`, encode/decode codecs
- Monty does NOT support: `match` statements, third-party libraries, full standard library
- Python requirement: `>=3.10` (agent-core requires `>=3.14`, compatible)
- Monty API: `AsyncMonty()` pool → `pool.checkout()` session → `session.feed_run(code, inputs, external_lookup)`
- `external_lookup`: dict mapping function names to host-side callables (renamed/changed in v0.0.19)
- Resource limits: memory usage, stack depth, execution time (configurable, async memory limits new in v0.0.19)
- Performance: subprocess pool execution, StringBuilder, regex optimizations
- New in v0.0.19: `resume_auto()` for iterative `feed_start` snapshots
- DynamicWorkflow API: `DynamicWorkflow(agents=[...], max_agent_calls=N, defer_loading=bool)`
- Model writes Python script → Monty executes in sandboxed worker subprocess
- Only last expression value returns to orchestrator context
- Token usage rolls up to parent run

### Decision 3: Harness compaction as optional layer

**Choice:** Context compaction is ALREADY IMPLEMENTED in `_build_harness_capabilities()`. No code changes needed — just documentation and config template updates.

**Existing implementation (in `_ai/agent.py:94-145`):**
- `context_compaction.strategy`: "summarizing" (default) or "sliding_window"
- `context_compaction.max_messages`: int (default 50)
- `context_compaction.max_tokens`: int|None (default None)
- `context_compaction.clamp_oversized`: bool → `ClampOversizedMessages`
- `context_compaction.clear_tool_results`: bool → `ClearToolResults`
- `context_compaction.deduplicate_reads`: bool → `DeduplicateFileReads`

**What's needed:**
- Add `context_compaction` section to `config.yaml.example`
- Add `dynamic_workflow` section to `config.yaml.example`
- Update harness-integration.md docs
- Add `harness_config` parameter to `BaseAgent.__init__()`

**Rationale:** ContextMemory handles working buffer (FIFO), harness compaction handles context window truncation (smart summarization). They operate at different layers.

### Decision 4: Profile system stays as-is

**Choice:** Keep existing profile system (scope, include, exclude, directories). No spec changes needed.

**Alternatives considered:**
- Simplify to just directories (no profiles) → rejected (each agent type needs different skills)
- Replace with harness repo_context → rejected (repo_context only injects CLAUDE.md, doesn't do skill matching)

**Rationale:** Profiles enable per-agent-type skill scoping (reviewer vs researcher vs jira-agent). The deterministic matcher + effectiveness tracking provides value over agent-decides-only.

### Decision 5: BaseAgent harness_config passthrough

**Choice:** Add `harness_config: dict[str, Any] | None = None` parameter to `BaseAgent.__init__()`. Pass it through to `AgentRuntime()`.

**Alternatives considered:**
- Use config.yaml global harness config → rejected (per-agent config is more flexible)
- Use AgentConfig dataclass → rejected (AgentConfig is for file-based loading, not programmatic use)

**Rationale:** `AgentRuntime` already accepts `harness_config`. `BaseAgent` just needs to pass it through. This is a 3-line change (parameter + passthrough).

### Decision 6: Replace tool_registry built-in tools with harness FileSystem + Shell

**Choice:** Replace agent-core's custom `tool_registry/builtins.py` (7 built-in tools) with harness FileSystem + Shell capabilities.

**Alternatives considered:**
- Keep custom built-in tools → rejected (harness has better security, path containment, allow/deny lists)
- Use harness FileSystem + Shell alongside built-in tools → rejected (redundant, confusing)
- Replace only some tools → rejected (inconsistent, partial security benefits)

**Rationale:** Harness FileSystem provides:
- Path containment (symlink resolution, TOCTTOU prevention)
- Binary detection (no binary data in model context)
- Optimistic concurrency (expected_hash for stale overwrites)
- Pattern filtering (allowed/denied/protected patterns)
- 8 tools: read_file, write_file, edit_file, list_directory, search_files, find_files, create_directory, file_info

Harness Shell provides:
- Allow/deny lists for commands
- Env control (replace inherited env, denied_env_patterns)
- Background process management (start/check/stop)
- Automatic cleanup on exit
- 4 tools: run_command, start_command, check_command, stop_command

**Migration:** Replace `ToolRegistry(include_builtins=True)` with `FileSystem(root_dir='.')` + `Shell(cwd='.')` capabilities. Update tool adapters in `_ai/tools.py`.

### Decision 7: Add SubAgents capability for declarative delegation

**Choice:** Add harness SubAgents capability for declarative sub-agent delegation.

**Alternatives considered:**
- Keep DynamicWorkflow only → rejected (DynamicWorkflow is reactive, SubAgents is declarative)
- Build custom delegation tool → rejected (harness SubAgents has isolation, usage rollup, failure handling)

**Rationale:** SubAgents provides:
- Single `delegate_task(agent_name, task)` tool for parent agent
- Isolation: each sub-agent gets own message history
- Usage aggregation: token usage shared with parent
- Tool inheritance: optional inherit_tools=True
- Shared capabilities: guardrails, memory, etc.
- Failure handling: soft vs hard errors, contain_errors
- Disk-based loading: markdown agent definitions in `.agents/`

**API:** `SubAgents(agents=[SubAgent(agent=child_agent, name='...', description='...')])`

### Decision 8: Add Planning capability for task decomposition

**Choice:** Add harness Planning capability for task decomposition before execution.

**Alternatives considered:**
- Skip planning → rejected (complex tasks benefit from structured plans)
- Custom planning implementation → rejected (harness Planning is cache-safe, simple)

**Rationale:** Planning provides:
- `write_plan` tool for model to write structured plans
- Steps with statuses: pending, in_progress, completed, cancelled
- Cache-safe: plan injected after cache breakpoint
- Per-run, observable via last write_plan tool return

**API:** `Planning(guidance='Optional system prompt guidance')`

### Decision 9: Harness capabilities vs agent-core custom implementations

**Analysis:** pydantic-ai-harness provides capabilities that overlap with agent-core's custom modules. Here's the comparison:

```
┌──────────────────────────────────────────────────────────────────────┐
│  HARNESS CAPABILITY       │  AGENT-CORE CUSTOM     │  ACTION        │
├───────────────────────────┼────────────────────────┼────────────────┤
│  FileSystem               │  tool_registry         │  REPLACE       │
│  (read/write/edit/search) │  (read_file, write_    │  This change   │
│                           │  file, grep_search)    │                │
├───────────────────────────┼────────────────────────┼────────────────┤
│  Shell                    │  tool_registry         │  REPLACE       │
│  (run/start/check/stop)   │  (shell_execute)       │  This change   │
├───────────────────────────┼────────────────────────┼────────────────┤
│  SubAgents                │  (none custom)         │  ADD           │
│  (delegation)             │                        │  This change   │
├───────────────────────────┼────────────────────────┼────────────────┤
│  Planning                 │  (none custom)         │  ADD           │
│  (task decomposition)     │                        │  This change   │
├───────────────────────────┼────────────────────────┼────────────────┤
│  DynamicWorkflow          │  (none custom)         │  ADD           │
│  (model orchestration)    │                        │  This change   │
├───────────────────────────┼────────────────────────┼────────────────┤
│  Memory                   │  memory/               │  KEEP BOTH     │
│  (notebook + search)      │  (3-layer)             │  Complementary │
├───────────────────────────┼────────────────────────┼────────────────┤
│  Repo Context             │  skill_system/         │  KEEP BOTH     │
│  (CLAUDE.md injection)    │  (agentskills.io)      │  Complementary │
├───────────────────────────┼────────────────────────┼────────────────┤
│  SlidingWindow/Compaction │  memory/context.py     │  KEEP BOTH     │
│  (context truncation)     │  (bounded FIFO)        │  Complementary │
├───────────────────────────┼────────────────────────┼────────────────┤
│  InputGuard/OutputGuard   │  resilience/           │  KEEP BOTH     │
│  (validation)             │  (circuit breaker)     │  Different scope│
├───────────────────────────┼────────────────────────┼────────────────┤
│  CodeMode                 │  (none custom)         │  FUTURE        │
│  (sandboxed execution)    │                        │                │
├───────────────────────────┼────────────────────────┼────────────────┤
│  Tool Output Mgmt         │  (output_overflow)     │  ALREADY DONE  │
├───────────────────────────┼────────────────────────┼────────────────┤
│  Cache Monitoring         │  (cache_monitoring)    │  ALREADY DONE  │
├───────────────────────────┼────────────────────────┼────────────────┤
│  Limit Warnings           │  (limit_warnings)      │  ALREADY DONE  │
└───────────────────────────┴────────────────────────┴────────────────┘
```

**Summary:**
- **REPLACE**: FileSystem, Shell (better security, features)
- **ADD**: SubAgents, Planning, DynamicWorkflow (new capabilities)
- **KEEP BOTH**: Memory, Repo Context, Compaction, Guardrails (complementary)
- **ALREADY DONE**: Tool Output Mgmt, Cache Monitoring, Limit Warnings
- **FUTURE**: CodeMode (requires exploration)

## Risks / Trade-offs

**[Risk] Monty Python subset limitations** → Monty supports a curated subset of Python (no classes yet, no third-party libs). DynamicWorkflow scripts must stay within this subset. Mitigation: Document supported features, provide examples, test with representative workflows.

**[Risk] Monty ~4.5MB binary dependency** → Increases package size. Mitigation: It's a compiled Rust binary, not a Python wheel tree. Acceptable for the capability it provides.

**[Risk] Symlink fragility across platforms** → Windows has limited symlink support. Mitigation: TDT workspace is macOS-only (Darwin 25.5.0). If Windows support is needed later, use a file-copy script instead.

**[Risk] Skill deduplication during merge** → 28 identical skills could diverge if edited independently before merge. Mitigation: Verify content is identical before merging (already confirmed via diff).

**[Trade-off] Two orchestration systems** → LangGraph + DynamicWorkflow adds complexity. Mitigation: Clear decision criteria (deterministic vs reactive), documented examples for each.

## Migration Plan

1. **Phase 1: Skills merge** (low risk, no code changes)
   - Move 25 `.claude/skills/`-only items to `.agents/skills/`
   - Remove 28 duplicate items from `.claude/skills/`
   - Replace `.claude/skills/` directory with symlink
   - Verify all skills accessible from both paths

2. **Phase 2: Monty dependency** (medium risk, new dependency)
   - Add `pydantic-monty` + harness[dynamic-workflow] to pyproject.toml
   - Run `uv sync` to install
   - Verify Monty binary works on macOS

3. **Phase 3: DynamicWorkflow config** (low risk, opt-in)
   - Add `dynamic_workflow` config block to `_build_harness_capabilities()`
   - Add tests for config parsing and capability instantiation
   - Verify opt-in: agents without config continue working unchanged

4. **Phase 4: Harness compaction config** (low risk, opt-in)
   - Add `context_compaction` config block to `_build_harness_capabilities()`
   - Wire compaction capabilities to agent runtime
   - Add tests for compaction strategies

**Rollback:** Each phase is independently reversible. Remove symlink, revert pyproject.toml changes, remove config blocks.

## Open Questions

- Should DynamicWorkflow be enabled by default for new agents, or always opt-in?
- Should Monty resource limits (memory, stack, time) be configurable via agent-core config?
- Should we add a `DynamicWorkflow` flavor for easy agent specialization?

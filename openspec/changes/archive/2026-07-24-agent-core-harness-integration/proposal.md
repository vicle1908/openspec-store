## Why

agent-core has built custom implementations for capabilities that pydantic-ai-harness already provides. The harness has better security (path containment, allow/deny lists, env control), better abstractions (declarative sub-agents, planning, notebook memory), and newer features (DynamicWorkflow, CodeMode). Meanwhile, the skills directory is fragmented across `.agents/skills/` (103 items) and `.claude/skills/` (54 items) with 28 identical overlaps.

This change consolidates the skills directory, adds missing harness capabilities (DynamicWorkflow, SubAgents, Planning), replaces high-overlap custom code with harness equivalents (FileSystem, Shell), and documents the full harness integration — reducing duplication while expanding agent capabilities.

## What Changes

- **Skills directory consolidation**: Merge `.claude/skills/` into `.agents/skills/`, create symlink `.claude/skills/ → .agents/skills/`. Moves 25 ECC-only skills to canonical location, removes 28 duplicate entries.
- **DynamicWorkflow integration**: Add `pydantic-monty` + `pydantic-ai-harness[dynamic-workflow]` dependencies. Wire DynamicWorkflow config into `_build_harness_capabilities()`.
- **SubAgents integration**: Add harness SubAgents capability for declarative sub-agent delegation with isolation, usage rollup, and failure handling.
- **Planning integration**: Add harness Planning capability for task decomposition before execution.
- **FileSystem + Shell replacement**: Replace agent-core's custom `tool_registry/` built-in tools with harness FileSystem + Shell capabilities for better security and features.
- **BaseAgent harness_config passthrough**: Add `harness_config` parameter to `BaseAgent.__init__()` so harness capabilities can be passed programmatically.
- **Config additions**: New `dynamic_workflow`, `subagents`, `planning`, `filesystem`, `shell` config sections in `config.yaml.example`. Document existing `context_compaction` config.
- **Documentation**: Update harness-integration.md with all capabilities, Monty, and migration guide.

## Capabilities

### New Capabilities
- `dynamic-workflow`: Model-driven orchestration via Monty sandbox — orchestrator agent writes Python script where sub-agents are async functions, executed in single tool call with asyncio.gather parallelism.
- `subagents`: Declarative sub-agent delegation — parent agent delegates tasks to named child agents with isolation, usage rollup, failure handling, and disk-based agent loading.
- `planning`: Task decomposition — model writes structured plans with steps (pending/in_progress/completed/cancelled) before execution.
- `filesystem`: Sandboxed file operations — read/write/edit/search with path containment, binary detection, optimistic concurrency, and pattern filtering.
- `shell`: Sandboxed shell execution — run/start/check/stop with allow/deny lists, env control, background processes, and automatic cleanup.

### Modified Capabilities
- `agent-runtime`: Adding `harness_config` parameter to `BaseAgent.__init__()` for programmatic harness capability access. Adding `dynamic_workflow`, `subagents`, `planning`, `filesystem`, `shell` handling in `_build_harness_capabilities()`.

### Already Implemented (no changes needed)
- `harness-compaction`: Context compaction already implemented in `_build_harness_capabilities()` (lines 94-145). Just needs config.yaml.example documentation.
- `tool-output-mgmt`: OverflowingToolOutput already implemented.
- `cache-monitoring`: CacheStabilityMonitor already implemented.
- `limit-warnings`: LimitWarner already implemented.

### Replaced Capabilities (retired custom code)
- `tool_registry/builtins`: Replaced by harness FileSystem + Shell capabilities. The 7 built-in tools (read_file, write_file, shell_execute, grep_search, git_diff, http_request, json_query) are replaced by harness equivalents with better security.

### Out of Scope (future work)
- Replace `memory/context.py` with harness SlidingWindow/Compaction (different approaches, complementary)
- Add harness CodeMode capability (requires Monty, future exploration)
- Add harness Memory notebook capability (complementary to 3-layer architecture)

## Impact

- **Dependencies**: New — `pydantic-monty>=0.0.16` (~4.5MB Rust binary)
- **agent-core/agent_base/agent.py**: Add `harness_config` parameter + passthrough (3 lines)
- **agent-core/_ai/agent.py**: Add `dynamic_workflow`, `subagents`, `planning`, `filesystem`, `shell` handling in `_build_harness_capabilities()` (~60 lines)
- **agent-core/tool_registry/builtins.py**: Retire built-in tools (replaced by harness capabilities)
- **agent-core/pyproject.toml**: Add Monty dependency
- **agent-core/config.yaml.example**: Add `dynamic_workflow`, `subagents`, `planning`, `filesystem`, `shell` sections
- **agent-core/docs/harness-integration.md**: Add all capabilities + migration guide
- **Skills directories**: `.claude/skills/` becomes symlink to `.agents/skills/`
- **25 skill files**: Moved from `.claude/skills/` to `.agents/skills/`
- **28 skill files**: Deleted from `.claude/skills/` (duplicates)
- **No breaking changes**: Existing agents continue working; all harness capabilities are opt-in via config
- **No impact on mobile apps**: Changes are agent-core + skills only

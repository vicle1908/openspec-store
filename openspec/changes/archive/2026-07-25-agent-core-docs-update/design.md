## Context

agent-core recently added harness capabilities integration (DynamicWorkflow, SubAgents, Planning, FileSystem, Shell) via pydantic-ai-harness v0.10.0. The documentation needs to be updated to reflect these additions and provide complete configuration guidance.

**Current state:**
- harness-integration.md: Missing FileSystem and Shell parameters
- configuration.md: Only brief mention of harness integration
- architecture.md: _ai/ module not in capability stack diagram
- builtin-tools.md: No mention of harness alternatives

## Goals / Non-Goals

**Goals:**
- Complete documentation for all harness capabilities with all parameters
- Document all harness config keys in configuration.md
- Update architecture.md to reflect current module structure (_ai/ module)
- Clarify relationship between built-in tools and harness capabilities
- Provide parameter tables for FileSystem and Shell sections

**Non-Goals:**
- Rewrite documentation structure
- Add new documentation files
- Update code examples beyond what's needed for new parameters
- Change existing documentation format

## Decisions

### Decision 1: Update harness-integration.md with missing parameters

**Choice:** Add parameter tables for FileSystem and Shell sections with all documented parameters.

**FileSystem parameters to add:**
- max_read_lines (int, default 2000) - max lines per read_file
- max_search_results (int, default 1000) - max search results
- max_find_results (int, default 1000) - max find results

**Shell parameters to add:**
- max_output_chars (int, default 50000) - output cap returned to model
- persist_cwd (bool, default false) - make cd sticky across calls
- allow_interactive (bool, default false) - allow TTY-style commands

**Rationale:** These parameters are implemented in the code but not documented. Developers need to know about them to configure the capabilities properly.

### Decision 2: Add harness config section to configuration.md

**Choice:** Add a new "harness capabilities" section documenting all 14 capability config keys with examples.

**Config keys to document:**
- dynamic_workflow: agents, max_agent_calls, defer_loading
- context_compaction: strategy, max_messages, max_tokens, clamp_oversized, clear_tool_results, deduplicate_reads
- subagents: agents, inherit_tools
- planning: guidance, cache_ttl
- filesystem: root_dir, allowed_patterns, denied_patterns, protected_patterns, max_read_lines, max_search_results, max_find_results
- shell: cwd, allowed_commands, denied_commands, denied_operators, default_timeout, max_output_chars, persist_cwd, allow_interactive
- And existing capabilities: guardrails, step_persistence, repo_context, output_overflow, cache_monitoring, limit_warnings, docs_access, durable_execution

**Rationale:** The config.yaml.example has these sections but configuration.md doesn't reference them. Developers reading the config reference need to know about harness capabilities.

### Decision 3: Update architecture.md capability stack

**Choice:** Add _ai/ module to the capability stack diagram and add harness capabilities to module summaries.

**Changes:**
- Add _ai/ module between agent_base and CLI in capability stack diagram
- Add module summary for _ai/ explaining harness capability integration
- Update dependency rules to include _ai/ module

**Rationale:** The _ai/ module is where all harness capability integration happens. It should be visible in the architecture diagram.

### Decision 4: Add alternatives note to builtin-tools.md

**Choice:** Add a note explaining that harness FileSystem/Shell provide alternatives with better security features.

**Content to add:**
- Harness FileSystem provides: path containment, binary detection, optimistic concurrency, pattern filtering
- Harness Shell provides: allow/deny lists, env control, background processes, automatic cleanup
- When to use built-in vs harness tools

**Rationale:** Developers should know about the harness alternatives when deciding which tools to use.

## Risks / Trade-offs

**[Risk] Documentation drift** → Documentation could become outdated again if new capabilities are added. Mitigation: Add a note in harness-integration.md about keeping docs in sync with implementation.

**[Risk] Parameter defaults may change** → Default values documented might change in future versions. Mitigation: Clearly mark defaults as current values, not guarantees.

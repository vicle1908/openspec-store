## 1. Skills Directory Consolidation

- [x] 1.1 Verify `.claude/skills/`-only skills are unique (not already in `.agents/skills/`)
- [x] 1.2 Move 26 `.claude/skills/`-only items to `.agents/skills/` (agents, backend-patterns, bun-runtime, coding-standards, continuous-learning, continuous-learning-v2, ecc-guide, ecc-tools-cost-audit, eval-harness, frontend-patterns, frontend-slides, git-workflow, gitnexus-pr-review, golang-patterns, golang-testing, java-coding-standards, postgres-patterns, python-patterns, python-testing, react-patterns, react-performance, react-testing, security-review, security-scan, tdd-workflow, verification-loop)
- [x] 1.3 Remove 27 duplicate items from `.claude/skills/` (verified: 20 identical, 7 had older versions in .claude/)
- [x] 1.4 Remove `.claude/skills/` directory
- [x] 1.5 Create symlink: `.claude/skills/ → ../../.agents/skills`
- [x] 1.6 Verify symlink works: `ls .claude/skills/ | wc -l` shows 137 items
- [x] 1.7 Verify Claude Code can read skills via symlink path
- [x] 1.8 Verify agent-core skill loader reads from `.agents/skills/` unchanged

## 2. Monty Dependency Setup

- [x] 2.1 Add `pydantic-monty` to `agent-core/pyproject.toml` dependencies: `"pydantic-monty>=0.0.18,<0.0.19"` (pinned to v0.0.18 due to MontyRepl compatibility with harness v0.10.0)
- [x] 2.2 Verify pydantic-ai-harness `[dynamic-workflow]` extra is available (current dep: `"pydantic-ai-harness>=0.10.0,<1"`)
- [x] 2.3 Run `uv sync` in agent-core to install Monty binary (~4.5MB Rust binary)
- [x] 2.4 Verify Monty v0.0.18 works: `python -c "import pydantic_monty; print(pydantic_monty.__version__)"` — **Pinned to v0.0.18 due to MontyRepl compatibility**
- [x] 2.5 Verify Monty v0.0.18 has MontyRepl: `python -c "from pydantic_monty import MontyRepl; print('ok')"` — MontyRepl exists in v0.0.18
- [x] 2.6 Verify DynamicWorkflow import works: `python -c "from pydantic_ai_harness.dynamic_workflow import DynamicWorkflow; print('ok')"` — **Works with Monty v0.0.18**
- [x] 2.7 Run existing tests to verify no regressions: `uv run pytest tests/ -q` — All tests pass

## 3. BaseAgent harness_config Passthrough

- [x] 3.1 Add `harness_config: dict[str, Any] | None = None` parameter to `BaseAgent.__init__()` in `agent-core/src/agent_core/agent_base/agent.py` (after line 81, alongside `source_file`)
- [x] 3.2 Store `self._harness_config = harness_config` in constructor body
- [x] 3.3 Pass `harness_config=self._harness_config` to `AgentRuntime()` constructor call (line ~150-157)
- [x] 3.4 Verify backward compatibility: agents without `harness_config` continue working unchanged (parameter defaults to None)
- [x] 3.5 Add test in `tests/test_agent_base.py` to verify harness_config passthrough

## 4. DynamicWorkflow Config Integration

- [x] 4.1 Add `dynamic_workflow` config key handling to `_build_harness_capabilities()` in `agent-core/src/agent_core/_ai/agent.py` (insert after line ~258, before durable_execution section at line ~259)
- [x] 4.2 Add docstring entry for `dynamic_workflow` in `_build_harness_capabilities()` docstring (line ~75)
- [x] 4.3 Import `DynamicWorkflow` from `pydantic_ai_harness.dynamic_workflow` with try/except ImportError
- [x] 4.4 Parse config fields: `agents` (list, default []), `max_agent_calls` (int, optional), `defer_loading` (bool, default False)
- [x] 4.5 Instantiate `DynamicWorkflow(agents=agents, max_agent_calls=max_agent_calls, defer_loading=defer_loading)` and append to capabilities list
- [x] 4.6 Add tests for DynamicWorkflow config parsing in `tests/test_harness_integration.py`:
  - test_dynamic_workflow_empty_config: `{"dynamic_workflow": {}}` → 1 capability
  - test_dynamic_workflow_with_max_agent_calls: `{"dynamic_workflow": {"max_agent_calls": 5}}` → 1 capability
  - test_dynamic_workflow_import_error: mock ImportError → 0 capabilities, warning logged
- [x] 4.7 Add `dynamic_workflow` section to `config.yaml.example` with usage comments:
  ```yaml
  # DynamicWorkflow: model-driven orchestration via Monty sandbox
  # dynamic_workflow:
  #   agents: []           # sub-agents accessible as async functions
  #   max_agent_calls: 10  # hard ceiling on sub-agent invocations
  #   defer_loading: false # keep catalog out of prompt until loaded
  ```

## 5. Harness Compaction Config Integration (ALREADY IMPLEMENTED)

**Note:** Context compaction is already fully implemented in `_build_harness_capabilities()` (lines 94-145). No code changes needed — just config template and docs updates.

- [x] 5.1 Verify existing compaction code in `_build_harness_capabilities()` works correctly (lines 94-145):
  - strategy: "summarizing" → SummarizingCompaction
  - strategy: "sliding_window" → SlidingWindow
  - clamp_oversized: true → ClampOversizedMessages
  - clear_tool_results: true → ClearToolResults
  - deduplicate_reads: true → DeduplicateFileReads
- [x] 5.2 Add `context_compaction` section to `config.yaml.example` with all options documented — Done in task 4.7
- [x] 5.3 Verify existing tests cover compaction (test_harness_integration.py lines 19-37):
  - test_compaction_summarizing ✓
  - test_compaction_sliding_window ✓
  - test_compaction_clamp_oversized ✓
  - test_compaction_clear_tool_results ✓
- [x] 5.4 Add missing tests for compaction sub-features:
  - test_compaction_deduplicate_reads
  - test_compaction_multiple_sub_features (all sub-features combined)
  - test_compaction_custom_max_part_chars
- [x] 5.5 Verify agents without `context_compaction` config continue working unchanged

## 6. SubAgents Config Integration (ALREADY IMPLEMENTED, needs config parsing)

**Note:** SubAgents is already instantiated in `_build_harness_capabilities()` (line 186-193) but with no config parsing. Needs enhancement.

- [x] 6.1 Enhance `subagents` config handling in `_build_harness_capabilities()` to parse config fields
- [x] 6.2 Parse config fields: `agents` (list, default []), `inherit_tools` (bool, default False), `shared_capabilities` (list, default [])
- [x] 6.3 Update instantiation to pass parsed config: `SubAgents(agents=agents, inherit_tools=inherit_tools)`
- [x] 6.4 Add tests for SubAgents config parsing in `tests/test_harness_integration.py`:
  - test_subagents_empty_config (existing, verify still works)
  - test_subagents_with_inherit_tools
  - test_subagents_with_shared_capabilities
- [x] 6.5 Add `subagents` section to `config.yaml.example`:
  ```yaml
  # SubAgents: declarative sub-agent delegation
  # subagents:
  #   agents: []              # list of child agent configs
  #   inherit_tools: false    # inherit parent tools
  #   shared_capabilities: [] # capabilities shared with children
  ```

## 7. Planning Config Integration (ALREADY IMPLEMENTED, needs config parsing)

**Note:** Planning is already instantiated in `_build_harness_capabilities()` (line 195-203) but with no config parsing. Needs enhancement.

- [x] 7.1 Enhance `planning` config handling in `_build_harness_capabilities()` to parse config fields
- [x] 7.2 Parse config fields: `guidance` (str, optional), `cache_ttl` (str, default "5m")
- [x] 7.3 Update instantiation to pass parsed config: `Planning(guidance=guidance, cache_ttl=cache_ttl)`
- [x] 7.4 Add tests for Planning config parsing in `tests/test_harness_integration.py`:
  - test_planning_empty_config (existing, verify still works)
  - test_planning_with_guidance
  - test_planning_with_cache_ttl
- [x] 7.5 Add `planning` section to `config.yaml.example`:
  ```yaml
  # Planning: task decomposition before execution
  # planning:
  #   guidance: ""            # optional system prompt guidance
  #   cache_ttl: "5m"         # plan cache TTL
  ```

## 8. FileSystem + Shell Integration (NEW capabilities)

**Note:** FileSystem and Shell are NOT implemented yet. These are new capabilities to add.

**FileSystem API (verified):**
```python
FileSystem(
    root_dir: str | Path = '.',
    allowed_patterns: Sequence[str] = [],
    denied_patterns: Sequence[str] = [],
    protected_patterns: Sequence[str] = ['.git/*', '.env', '*.pem', '*.key', '**/secrets*'],
    max_read_lines: int = 2000,
    max_search_results: int = 1000,
    max_find_results: int = 1000,
)
```

**Shell API (verified):**
```python
Shell(
    cwd: str | Path = '.',
    allowed_commands: Sequence[str] = [],
    denied_commands: Sequence[str] = ['rm', 'rmdir', 'mkfs', 'dd', 'shutdown', 'reboot'],
    denied_operators: Sequence[str] = [],
    default_timeout: float = 30.0,
    max_output_chars: int = 50000,
    persist_cwd: bool = False,
    allow_interactive: bool = False,
    env: Mapping[str, str] | None = None,
    denied_env_patterns: Sequence[str] = [],
)
```

- [x] 8.1 Add `filesystem` config key handling to `_build_harness_capabilities()` in `agent-core/src/agent_core/_ai/agent.py`
- [x] 8.2 Import `FileSystem` from `pydantic_ai_harness` with try/except ImportError
- [x] 8.3 Parse config fields: `root_dir` (str, default "."), `allowed_patterns` (list), `denied_patterns` (list), `protected_patterns` (list), `max_read_lines` (int), `max_search_results` (int), `max_find_results` (int)
- [x] 8.4 Instantiate `FileSystem(root_dir=root_dir, ...)` and append to capabilities list
- [x] 8.5 Add `shell` config key handling to `_build_harness_capabilities()` in `agent-core/src/agent_core/_ai/agent.py`
- [x] 8.6 Import `Shell` from `pydantic_ai_harness` with try/except ImportError
- [x] 8.7 Parse config fields: `cwd` (str, default "."), `allowed_commands` (list), `denied_commands` (list), `denied_operators` (list), `default_timeout` (float, default 30.0), `max_output_chars` (int), `persist_cwd` (bool), `allow_interactive` (bool)
- [x] 8.8 Instantiate `Shell(cwd=cwd, ...)` and append to capabilities list
- [x] 8.9 Add tests for FileSystem + Shell config parsing in `tests/test_harness_integration.py`:
  - test_filesystem_empty_config
  - test_filesystem_with_patterns
  - test_filesystem_with_custom_limits
  - test_shell_empty_config
  - test_shell_with_allow_deny
  - test_shell_with_custom_timeout
  - test_filesystem_import_error
  - test_shell_import_error
- [x] 8.10 Add `filesystem` and `shell` sections to `config.yaml.example`:
  ```yaml
  # FileSystem: sandboxed file operations
  # filesystem:
  #   root_dir: "."           # sandbox root
  #   allowed_patterns: []    # allowlist globs (empty = allow all)
  #   denied_patterns: []     # denylist globs
  #   protected_patterns: []  # read-only globs (defaults to .git, .env, secrets)
  #   max_read_lines: 2000    # max lines per read_file
  #   max_search_results: 1000 # max search results
  #   max_find_results: 1000  # max find results

  # Shell: sandboxed shell execution
  # shell:
  #   cwd: "."                # working directory
  #   allowed_commands: []    # allowlist (mutually exclusive with denied)
  #   denied_commands: []     # denylist (defaults to destructive commands)
  #   denied_operators: []    # blocked shell operators
  #   default_timeout: 30.0   # seconds per run_command
  #   max_output_chars: 50000 # output cap returned to model
  #   persist_cwd: false      # make cd sticky across calls
  #   allow_interactive: false # allow TTY-style commands
  ```
- [x] 8.11 Add example in `agent-core/examples/harness_filesystem.py` showing FileSystem usage
- [x] 8.12 Add example in `agent-core/examples/harness_shell.py` showing Shell usage

## 9. Documentation Updates

- [x] 9.1 Update `agent-core/docs/harness-integration.md` (after line 176):
  - Add DynamicWorkflow section with API, config, and model-written script examples
  - Add Monty v0.0.18 sandbox section with supported Python features
  - Add SubAgents section with API, delegation, isolation, failure handling
  - Add Planning section with API, plan structure, cache-safe injection
  - Add FileSystem section with API, path containment, pattern filtering
  - Add Shell section with API, allow/deny lists, env control
  - Add config.yaml.example reference for all capabilities
- [x] 9.2 Add DynamicWorkflow example to `agent-core/examples/dynamic_workflow.py`:
  - Show orchestrator agent with reviewer + summarizer sub-agents
  - Show model-written script with asyncio.gather parallelism
  - Show budget enforcement with max_agent_calls
- [x] 9.3 Add SubAgents example to `agent-core/examples/subagents.py`:
  - Show parent agent with child agents
  - Show delegation tool usage
  - Show failure handling
- [x] 9.4 Add Planning example to `agent-core/examples/planning.py`:
  - Show agent with Planning capability
  - Show plan creation and status updates
- [x] 9.5 Add FileSystem + Shell example to `agent-core/examples/fileshell.py`:
  - Show FileSystem with pattern filtering
  - Show Shell with allow/deny lists
  - Show migration from built-in tools
- [x] 9.6 Update `agent-core/README.md`:
  - Add Monty to dependencies table (line ~14): `"pydantic-monty>=0.0.18,<0.0.19"`
  - Add DynamicWorkflow, SubAgents, Planning, FileSystem, Shell to capabilities table
  - Add `harness_config` parameter to BaseAgent quick start example (line ~75-85)
- [x] 9.7 Update `agent-core/docs/configuration.md` with new config keys:
  - Add `harness_config` section explaining how to pass harness capabilities
  - Add `dynamic_workflow` config reference
  - Add `subagents` config reference
  - Add `planning` config reference
  - Add `filesystem` config reference
  - Add `shell` config reference
  - Add `context_compaction` config reference (note: already implemented)
  - Add migration guide: built-in tools → harness capabilities

## 10. Integration Testing

- [x] 10.1 Create a test agent with DynamicWorkflow enabled and verify it can run:
  ```python
  agent = BaseAgent(
      name="orchestrator",
      gateway=gateway,
      tool_registry=registry,
      harness_config={"dynamic_workflow": {"max_agent_calls": 5}},
  )
  ```
- [x] 10.2 Create a test agent with compaction enabled and verify context is compacted:
  ```python
  agent = BaseAgent(
      name="compacted",
      gateway=gateway,
      tool_registry=registry,
      harness_config={"context_compaction": {"strategy": "summarizing", "max_messages": 30}},
  )
  ```
- [x] 10.3 Create a test agent with SubAgents enabled and verify delegation works
- [x] 10.4 Create a test agent with Planning enabled and verify plan creation works
- [x] 10.5 Create a test agent with FileSystem + Shell enabled and verify file/shell operations work
- [x] 10.6 Test DynamicWorkflow + compaction together
- [x] 10.7 Test DynamicWorkflow + LangGraph coexistence
- [x] 10.8 Test SubAgents + Planning together
- [x] 10.9 Test FileSystem + Shell with pattern filtering
- [x] 10.10 Run full test suite: `uv run pytest tests/ -q` (329+ tests) — All tests pass
- [x] 10.11 Run type check: `uv run mypy src/agent_core/ --strict` — Passes
- [x] 10.12 Run lint: `uv run ruff check src/ tests/` — Passes

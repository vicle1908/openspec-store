## 1. Update harness-integration.md

- [x] 1.1 Add max_read_lines parameter to FileSystem section with description "max lines per read_file (default: 2000)"
- [x] 1.2 Add max_search_results parameter to FileSystem section with description "max search results (default: 1000)"
- [x] 1.3 Add max_find_results parameter to FileSystem section with description "max find results (default: 1000)"
- [x] 1.4 Add parameter table for FileSystem section with all 7 parameters
- [x] 1.5 Add max_output_chars parameter to Shell section with description "output cap returned to model (default: 50000)"
- [x] 1.6 Add persist_cwd parameter to Shell section with description "make cd sticky across calls (default: false)"
- [x] 1.7 Add allow_interactive parameter to Shell section with description "allow TTY-style commands (default: false)"
- [x] 1.8 Add parameter table for Shell section with all 8 parameters

## 2. Update configuration.md

- [x] 2.1 Add "harness capabilities" section after skills section
- [x] 2.2 Document dynamic_workflow config with agents, max_agent_calls, defer_loading parameters
- [x] 2.3 Document subagents config with agents, inherit_tools parameters
- [x] 2.4 Document planning config with guidance, cache_ttl parameters
- [x] 2.5 Document filesystem config with root_dir, allowed_patterns, denied_patterns, protected_patterns, max_read_lines, max_search_results, max_find_results parameters
- [x] 2.6 Document shell config with cwd, allowed_commands, denied_commands, denied_operators, default_timeout, max_output_chars, persist_cwd, allow_interactive parameters
- [x] 2.7 Add reference to config.yaml.example for full configuration and harness-integration.md for detailed usage

## 3. Update architecture.md

- [x] 3.1 Add _ai/ module to capability stack diagram between agent_base and CLI
- [x] 3.2 Add _ai/ module summary explaining harness capability integration
- [x] 3.3 Update dependency rules to include _ai/ module depends on agent_base
- [x] 3.4 Add harness capabilities to module summaries list

## 4. Update builtin-tools.md

- [x] 4.1 Add "Alternatives" section at end of document
- [x] 4.2 Explain harness FileSystem provides better security (path containment, binary detection, optimistic concurrency, pattern filtering)
- [x] 4.3 Explain harness Shell provides better security (allow/deny lists, env control, background processes)
- [x] 4.4 Add guidance on when to use built-in vs harness tools
- [x] 4.5 Add reference to harness-integration.md for details

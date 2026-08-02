## Why

The agent-core documentation is missing key information about the recently added harness capabilities integration:

1. **harness-integration.md** is missing parameters for FileSystem and Shell capabilities:
   - FileSystem: max_read_lines, max_search_results, max_find_results
   - Shell: max_output_chars, persist_cwd, allow_interactive

2. **configuration.md** lacks a complete harness capabilities config section:
   - Only mentions harness integration briefly
   - Missing config keys for DynamicWorkflow, FileSystem, Shell, etc.

3. **architecture.md** doesn't reflect the _ai/ module in the capability stack:
   - The _ai/ module is where all harness capability integration happens
   - Not visible in the capability stack diagram
   - Not listed in module summaries

4. **builtin-tools.md** doesn't mention harness FileSystem/Shell as alternatives:
   - Developers should know about harness alternatives with better security
   - No guidance on when to use built-in vs harness tools

## What Changes

- **harness-integration.md**: Add missing FileSystem and Shell parameters with documentation
- **configuration.md**: Add complete harness capabilities config section with all 14 capability config keys
- **architecture.md**: Update capability stack diagram to include _ai/ module and add harness capabilities to module summaries
- **builtin-tools.md**: Add note about harness FileSystem/Shell as alternatives with security benefits

## Capabilities

### Modified Capabilities
- `documentation`: Update existing documentation files to reflect current implementation

## Impact

- **Files modified**: 4 documentation files in agent-core/docs/
- **No code changes**: Documentation only
- **No breaking changes**: Additive information only
- **No new dependencies**: Documentation updates only

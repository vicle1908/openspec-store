# tool-registry Specification

## Purpose
TBD - created by archiving change agent-core-builtin-toolkit. Update Purpose after archive.
## Requirements
### Requirement: ToolRegistry supports auto-registration of built-in tools
The system MUST allow `ToolRegistry` to auto-register the built-in tool set via an opt-out flag, with the default being to include them.

#### Scenario: Default registry includes built-in tools
- **WHEN** `ToolRegistry()` is constructed without arguments
- **THEN** all 7 built-in tools (shell_execute, read_file, write_file, grep_search, git_diff, http_request, json_query) are registered automatically

#### Scenario: include_builtins=False produces an empty registry
- **WHEN** `ToolRegistry(include_builtins=False)` is constructed
- **THEN** no built-in tools are registered and `list_tools()` returns an empty list

#### Scenario: User-registered tools coexist with built-ins
- **WHEN** a custom tool is registered on a default registry that already has built-ins
- **THEN** both built-in and custom tools are available and `list_tools()` returns the union

#### Scenario: User can override a built-in by name
- **WHEN** a user calls `register(MyReadFile(), replace=True)` where `MyReadFile.metadata.name == "read_file"`
- **THEN** the custom implementation replaces the built-in and is used in subsequent executions

#### Scenario: Legacy aliases remain available during migration
- **WHEN** default built-ins are registered
- **THEN** compatibility aliases `shell` -> `shell_execute` and `grep` -> `grep_search` are accepted for lookup and execution

#### Scenario: Metadata listing is canonical
- **WHEN** `list_tools()` is called with built-ins enabled
- **THEN** canonical names are returned (`shell_execute`, `grep_search`) and aliases are omitted from public metadata


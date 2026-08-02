# tools Specification

## Purpose
Re-implements the seven built-in tools as `@agent.tool()` functions with pydantic-ai v2, preserving aliases, `ToolRegistryFacade`, and argument validation.
## Requirements
### Requirement: TOOL-1: Seven Builtin Tools as @agent.tool()

The following seven tools SHALL be re-implemented as `@agent.tool()` functions in `_ai/tools.py`. Each function SHALL accept `RunContext[AgentRuntimeDeps]` as first parameter and return `str`:

1. `read_file` — read file contents from disk
2. `write_file` — write content to a file
3. `grep_search` — search for patterns in files
4. `git_diff` — show git diff between revisions
5. `http_request` — make HTTP requests
6. `shell_execute` — execute shell commands
7. `json_query` — query structured data with JSONPath

#### Scenario: read_file tool execution

- **GIVEN** `read_file` is registered as an `@agent.tool()` on the agent
- **WHEN** the model calls `read_file(path="/tmp/test.txt")`
- **THEN** the file contents are returned as a `str`

#### Scenario: write_file tool execution

- **GIVEN** `write_file` is registered as an `@agent.tool()` on the agent
- **WHEN** the model calls `write_file(path="/tmp/out.txt", content="hello")`
- **THEN** the file `/tmp/out.txt` contains `"hello"`

### Requirement: TOOL-2: Tool Aliases

The following tool aliases SHALL be preserved by registering the same function under multiple names:

- `shell` → `shell_execute`
- `grep` → `grep_search`

#### Scenario: shell alias resolves to shell_execute

- **GIVEN** `shell_execute` is registered under both `shell_execute` and `shell` names
- **WHEN** the model calls the tool named `shell`
- **THEN** the `shell_execute` function is invoked

### Requirement: TOOL-3: ToolRegistryFacade

A `ToolRegistryFacade` SHALL be provided in `tool_registry/registry.py` for diagnostics and introspection.

`ToolRegistryFacade` SHALL be read-only. It SHALL NOT be used by the agent runtime.

`ToolRegistryFacade` SHALL provide `list_tools()` and `get_tool()`.

#### Scenario: ToolRegistryFacade lists tools

- **GIVEN** `ToolRegistryFacade` is instantiated
- **WHEN** `list_tools()` is called
- **THEN** a list of `ToolMetadata` objects is returned

### Requirement: TOOL-4: ToolArgument Validation

Tool argument validation SHALL be handled by pydantic-ai's automatic validation via the `@agent.tool()` decorator, not by custom `ToolRegistry.execute()`.

#### Scenario: Invalid tool args raise ValidationError handled by pydantic-ai

- **GIVEN** the model calls `read_file(path=123)` with a non-string argument
- **WHEN** the `@agent.tool()` function signature declares `path: str`
- **THEN** pydantic-ai handles the validation error and retries the tool call


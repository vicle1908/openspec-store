# builtin-tools Specification

## Purpose
Defines built-in tool implementations for common file, search, git, HTTP, and JSON primitives with safety guards, input validation, and workspace-scoped sandboxing.
## Requirements
### Requirement: Built-in tools provide common file, search, git, and HTTP primitives
The system MUST ship built-in tool implementations for the most common agent operations: shell_execute, read_file, write_file, grep_search, git_diff, http_request, and json_query.

#### Scenario: Tool names are canonical and stable
- **WHEN** built-ins are exposed through the registry
- **THEN** the public names are `shell_execute`, `read_file`, `write_file`, `grep_search`, `git_diff`, `http_request`, and `json_query`

#### Scenario: Legacy aliases continue to resolve
- **WHEN** existing code calls `shell` or `grep`
- **THEN** the registry resolves them to `shell_execute` and `grep_search` respectively without changing behavior

#### Scenario: read_file returns file contents under size limit
- **WHEN** `read_file` is called with a path within the workspace and the file size is under the configured limit
- **THEN** the tool returns the file contents as a string in `ToolResult.output`

#### Scenario: read_file supports line ranges
- **WHEN** `read_file` is called with `start_line` and `end_line`
- **THEN** the tool returns only that inclusive line slice and preserves line numbering in metadata

#### Scenario: read_file rejects oversized files
- **WHEN** `read_file` is called and the file exceeds `max_size_bytes` (default 1 MiB)
- **THEN** the tool returns a `ToolResult` with `success=False` and an error message indicating the size limit

#### Scenario: write_file refuses paths outside workspace root
- **WHEN** `write_file` is called with a path that resolves outside the detected workspace root
- **THEN** the tool returns `success=False` with an error indicating the path is out of bounds

#### Scenario: grep_search caps result count
- **WHEN** `grep_search` is called with a pattern that matches more than `max_results` (default 100) lines
- **THEN** the tool returns the first `max_results` matches with a truncation indicator

#### Scenario: grep_search skips binary files
- **WHEN** `grep_search` scans a file detected as binary
- **THEN** the file is skipped and the result metadata notes the omission

#### Scenario: grep_search supports regex and literal mode
- **WHEN** `grep_search` is called with `use_regex=false`
- **THEN** the pattern is treated as a literal string instead of a regular expression

#### Scenario: git_diff returns unified diff for a range
- **WHEN** `git_diff` is called with `from_ref` and `to_ref`
- **THEN** the tool returns the unified diff text from `git diff <from>..<to>` in `ToolResult.output`

#### Scenario: git_diff can filter files
- **WHEN** `git_diff` is called with a file filter
- **THEN** the diff output includes only matching paths

#### Scenario: http_request enforces timeout
- **WHEN** `http_request` is called with a URL that does not respond within the configured timeout
- **THEN** the tool returns `success=False` with a timeout error

#### Scenario: http_request blocks private-network destinations
- **WHEN** `http_request` resolves a URL or redirect target into loopback, link-local, private, multicast, or metadata IP ranges
- **THEN** the request is rejected before any bytes are sent to the destination

#### Scenario: http_request rejects unsafe redirects
- **WHEN** `http_request` follows a redirect to a non-HTTPS scheme or a disallowed destination
- **THEN** the redirect is blocked and the tool returns a security error

#### Scenario: http_request truncates large responses
- **WHEN** the response body exceeds the configured output limit
- **THEN** the tool returns a truncated payload with an explicit truncation marker in metadata

#### Scenario: http_request supports authenticated requests through secrets
- **WHEN** `http_request` is called with `auth_secret_key`
- **THEN** the tool resolves headers from `settings.secrets` without exposing secret values in args or audit logs

#### Scenario: json_query evaluates JMESPath expressions
- **WHEN** `json_query` is called with valid JSON and a valid JMESPath expression
- **THEN** the tool returns the expression result in `ToolResult.output`

#### Scenario: json_query rejects invalid expressions
- **WHEN** `json_query` is called with a malformed or unsupported expression
- **THEN** the tool returns `success=False` with a parse or evaluation error message

### Requirement: Built-in tools follow the safety-guard pattern of ShellExecutor
The system MUST apply input validation, output truncation, and dangerous-pattern detection to all built-in tools that touch the filesystem, shell, or network.

#### Scenario: write_file rejects dangerous path components
- **WHEN** `write_file` receives a path containing `..` traversal segments resolving outside the workspace
- **THEN** the tool blocks the write and returns an error before opening the file

#### Scenario: http_request sanitizes redirects
- **WHEN** `http_request` follows a redirect to a non-HTTPS scheme or a private IP
- **THEN** the tool blocks the redirect and returns a security error

### Requirement: Built-in tools are independently testable
The system MUST provide unit tests for every built-in tool covering happy path, validation failures, and safety-guard enforcement.

#### Scenario: Each built-in has dedicated tests
- **WHEN** the test suite is run
- **THEN** each of the 6 built-in tools has at least one happy-path test and at least one safety-guard test


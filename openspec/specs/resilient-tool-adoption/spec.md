## Purpose

This specification defines requirements for Resilient Tool Adoption.

## Requirements

### Requirement: External-call tools SHALL use @resilient_tool decorator

Tools that make external calls (HTTP, subprocess) SHALL be decorated with `@resilient_tool()` from `agent_core.resilience.decorators` to provide automatic retry and circuit breaker functionality. This replaces manual retry logic in `on_tool_error` hooks.

#### Scenario: CheckLinksTool has retry on HTTP failures
- **WHEN** `CheckLinksTool` makes an HTTP HEAD request that fails with `ConnectionError` or `TimeoutError`
- **THEN** the tool SHALL retry up to 2 times with exponential backoff
- **AND** after 3 consecutive failures, the circuit breaker SHALL open and block further calls for 30 seconds

#### Scenario: GitDiffTool has retry on subprocess failures
- **WHEN** `GitDiffTool` runs a git subprocess that fails with `TimeoutExpired`
- **THEN** the tool SHALL retry up to 1 time

#### Scenario: StateTool has retry on subprocess failures
- **WHEN** `StateTool` runs a git subprocess that fails with `TimeoutExpired`
- **THEN** the tool SHALL retry up to 1 time

#### Scenario: Pure file I/O tools do not use resilient_tool
- **WHEN** a tool only performs file I/O (read_doc, write_doc, scanner, classifier, enforcer)
- **THEN** the tool SHALL NOT be decorated with `@resilient_tool`
- **AND** no retry or circuit breaker overhead SHALL be added

### Requirement: on_tool_error retry hook SHALL be removed

The manual `on_tool_error` hook in `agent.py` that retries `check_links` and `git_diff` on transient errors SHALL be removed from hook registration. The `@resilient_tool` decorator replaces this functionality with proper retry + circuit breaker.

#### Scenario: Agent builder does not register on_tool_error
- **WHEN** `build_doc_sync_agent()` is called
- **THEN** the `on_tool_error` hook SHALL NOT be registered
- **AND** tools decorated with `@resilient_tool` SHALL handle their own retry

### Requirement: Tools using resilient_tool SHALL be importable from SDK

The `@resilient_tool` decorator SHALL be importable from `agent_core.sdk` for consumer use.

#### Scenario: Consumer imports resilient_tool from SDK
- **WHEN** a consumer runs `from agent_core.sdk import resilient_tool`
- **THEN** the import SHALL resolve correctly

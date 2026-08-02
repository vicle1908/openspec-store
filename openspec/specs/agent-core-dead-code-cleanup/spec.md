## Purpose

This specification defines requirements for Agent Core Dead Code Cleanup.

## Requirements

### Requirement: Orchestration module status annotation
The `agent_core.orchestration` module SHALL be annotated to clarify its integration status.

#### Scenario: External consumer awareness
- **WHEN** a developer reads `agent_core/orchestration/__init__.py`
- **THEN** the module docstring SHALL state that it is used externally by `agent-docs-sync` but not wired into `BaseAgent`'s own run loop
- **AND** the module SHALL NOT be marked as `EXPERIMENTAL` (it has an active external consumer)

### Requirement: Generated output not tracked in git
The `src/reports/` directory SHALL not be tracked in git.

#### Scenario: Gitignore update
- **WHEN** the cleanup is applied
- **THEN** `src/reports/` SHALL be added to `.gitignore`
- **AND** `git rm --cached` SHALL be applied to all files under `src/reports/`

### Requirement: Duplicate deployment config removed
The `deployments/scheduler/pyproject.toml` SHALL be removed.

#### Scenario: Duplicate file removal
- **WHEN** the cleanup is applied
- **THEN** `deployments/scheduler/pyproject.toml` SHALL not exist
- **AND** the scheduler Dockerfile SHALL continue to function (it copies from the main `pyproject.toml`)

### Requirement: Stale verification constants updated
Verification scripts SHALL have correct manifest and schedule counts.

#### Scenario: Manifest count correction
- **WHEN** `scripts/verify_scheduler.py` is read
- **THEN** `EXPECTED_MANIFESTS` SHALL be 4 (matching the 4 repos in `entrypoint.sh`)

#### Scenario: Post-deploy manifest count correction
- **WHEN** `scripts/post_deploy_verify.py` is read
- **THEN** `EXPECTED_MANIFESTS` SHALL be 4

### Requirement: Documentation accuracy
`AGENTS.md` SHALL reflect accurate test counts and current dependency status.

#### Scenario: Test count accuracy
- **WHEN** `AGENTS.md` is read
- **THEN** the test count SHALL match the actual number of test functions in `tests/`

#### Scenario: Dependency conflict warning accuracy
- **WHEN** `AGENTS.md` mentions the `opentelemetry-sdk` vs `pydantic-ai` conflict
- **THEN** the warning SHALL be removed if the conflict has been resolved, or updated if it still exists

### Requirement: Durable pipeline example updated
`examples/durable_pipeline.py` SHALL use the current scheduler API pattern.

#### Scenario: Singleton engine usage
- **WHEN** `examples/durable_pipeline.py` is read
- **THEN** it SHALL use `get_engine()` singleton pattern instead of standalone `SchedulerEngine` instantiation

### Requirement: Cross-repo compatibility preserved
All proposed removals SHALL NOT break any external consumer of agent-core.

#### Scenario: agent-docs-sync compatibility
- **WHEN** the cleanup is applied
- **THEN** `agent-docs-sync` SHALL continue to import `LLMGateway`, `LiteLLMGateway`, `BaseAgent`, `HookRegistry`, `Flavor`, `ToolRegistry`, `BaseTool`, `ToolMetadata`, `ToolResult`, `WorkflowBuilder`, `WorkflowEngine`, `EdgeDescriptor`, `NodeDescriptor`, `NodeKind`, `EdgeCondition`, `configure_logging`, and `GatewayError` without errors
- **AND** `agent-docs-sync` SHALL NOT need any code changes

#### Scenario: No phantom imports introduced
- **WHEN** the cleanup is applied
- **THEN** `uv run python -c "import agent_core"` SHALL succeed
- **AND** no `ImportError` or `ModuleNotFoundError` SHALL occur for any preserved public API

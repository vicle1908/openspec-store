## Context

The TDT ecosystem spans 20+ Python repos with shared dependencies. Version drift has accumulated over time. This change upgrades all dependencies to latest validated versions in a single coordinated effort with comprehensive verification.

## Decisions

### 1. Single change with phased implementation

All upgrades are bundled into one change but implemented in dependency order: low-risk first (floors, legacy), then medium-risk (opentelemetry), then high-risk (pydantic-ai, atlassian). This allows early verification of low-risk changes before tackling high-risk ones.

### 2. pydantic-ai upgrade strategy

pydantic-ai <2.19 → >=2.31.0,<2.32 is a 12-version jump. The key APIs used are:
- `Agent`, `AgentSpec` (agent-core config_loader)
- `AbstractCapability`, `Hooks` (agent-core hooks)
- `RunContext` (agent-core tool_collection)
- `Model`, `infer_model`, `AnthropicModel` (agent-core models)

The upgrade will be tested with the full test suite. If API breaks are found, they will be fixed in-scope.

### 3. atlassian-python-api upgrade strategy

atlassian-python-api 3.x → 5.x is a major version bump. The upgrade will be tested with jira-skill's test suite. If breaking changes are found, they will be addressed in-scope.

### 4. opentelemetry-sdk upgrade strategy

opentelemetry-sdk <1.40.0 → >=1.40.0,<1.45.0 is a minor version bump. The API is stable. Ceiling will be raised to allow latest.

### 5. Verification approach

Each upgrade is verified with:
1. `uv sync` — dependency resolution succeeds
2. `uv run pytest` — full test suite passes
3. `uv run mypy src/ --strict` — type checking passes
4. `uv run ruff check .` — linting passes

### 6. Rollback strategy

Each upgrade can be independently reverted by reverting the pyproject.toml change and running `uv sync`.

## Migration Plan

1. Bump dependency floors (redis, croniter, uvicorn, fastapi)
2. Remove 2 legacy typing imports
3. Upgrade opentelemetry-sdk ceiling
4. Upgrade pydantic-ai ceiling (with test verification)
5. Upgrade atlassian-python-api (with test verification)
6. Run full verification across all repos
7. Commit and archive

## Why

The TDT ecosystem has accumulated significant dependency version drift across 20+ Python repos. Critical packages like pydantic-ai are pinned to <2.19 while the latest is 2.31.0 (12 minor versions behind). opentelemetry-sdk is pinned to <1.40.0 while latest is 1.44.0. atlassian-python-api is pinned to <4.0.0 while latest is 5.0.3. Additionally, pre-commit hook versions are outdated, 1 deprecated Union import exists in code-daily-scan, and 2 deprecated asyncio.get_event_loop() calls exist in jira-kanban-from-spreadsheet.

## What Changes

- **pydantic-ai**: Update ceiling from <2.19 to >=2.31.0,<2.32 across agent-core, agent-harness, agent-docs-sync
- **opentelemetry-sdk**: Update ceiling from <1.40.0 to >=1.40.0,<1.45.0 across agent-core, agent-harness; bump ai-review floor to >=1.40.0
- **atlassian-python-api**: Update from <4.0.0 to >=5.0.0,<6.0.0 across tdt-core, jira-skill (major version bump)
- **Dependency floors**: Bump floors to latest for redis (>=8.0.0 in jira-skill, ops-automation-suite), croniter (>=6.0.0 in tdt-core), uvicorn (>=0.50.0 in tdt-core, ai-review), fastapi (>=0.140.0 in tdt-core, ai-review)
- **Pre-commit hooks**: Already updated (ruff v0.16.3, uv 0.12.5) — verification included
- **Legacy cleanup**: Fix 1 deprecated Union import in code-daily-scan, fix 2 deprecated asyncio.get_event_loop() in jira-kanban-from-spreadsheet
- **pydantic-ai-harness compatibility**: Verify pydantic-ai-harness==0.11.0 works with pydantic-ai 2.31.x

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- All Python repos use latest validated dependency versions
- Pre-commit hooks aligned with latest GitHub releases
- Legacy patterns removed

## Impact

### Scope

6 target repos (tdt-core, agent-core, agent-harness, agent-docs-sync, ai-harness-skills, ai-review) plus jira-skill (atlassian-python-api), code-daily-scan (Union import), jira-kanban-from-spreadsheet (asyncio), ops-automation-suite (redis floor).

### Risk

- **pydantic-ai 12-version jump**: HIGH — API changes likely, requires full test suite
- **pydantic-ai-harness pin**: MEDIUM — verify 0.11.0 compatibility with 2.31.x
- **atlassian-python-api major bump**: MEDIUM — breaking changes possible
- **opentelemetry minor bump**: LOW — stable API
- **Floor bumps**: LOW — no breaking changes

### Non-goals

- Do not change Python version requirement
- Do not add new dependencies
- Do not refactor code for new syntax (separate change)
- Do not modify business logic
- Do not upgrade langgraph, langfuse, mlflow, aiohttp (separate changes if needed)

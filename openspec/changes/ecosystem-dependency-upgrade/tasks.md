## 1. Low-Risk Dependency Floors

- [x] 1.1 Bump redis floor from >=5.0.0 to >=8.0.0 in jira-skill and ops-automation-suite
- [x] 1.2 Bump croniter floor from >=1.4.0 to >=6.0.0 in tdt-core scheduler
- [x] 1.3 Bump uvicorn floor from >=0.30.0 to >=0.50.0 in tdt-core scheduler and ai-review
- [x] 1.4 Bump fastapi floor from >=0.115.0 to >=0.140.0 in tdt-core and ai-review
- [x] 1.5 Fix 1 deprecated Union import in code-daily-scan (from typing import Union → use X | Y)
- [x] 1.6 Fix 2 deprecated asyncio.get_event_loop() calls in jira-kanban-from-spreadsheet (→ asyncio.get_running_loop())
- [x] 1.7 Verify pydantic-ai-harness==0.11.0 compatibility with pydantic-ai >=2.31.0
- [x] 1.8 Run `uv sync` and verify dependency resolution across all repos
- [x] 1.9 Run full test suite across all 6 target repos

## 2. opentelemetry-sdk Upgrade

- [x] 2.1 Update opentelemetry-sdk ceiling from <1.40.0 to >=1.40.0,<1.45.0 in agent-core and agent-harness
- [x] 2.2 Bump ai-review opentelemetry-sdk floor from >=1.39 to >=1.40.0
- [ ] 2.3 Run `uv sync` and verify dependency resolution
- [ ] 2.4 Run full test suite across agent-core, agent-harness, and ai-review
- [ ] 2.5 Verify no breaking API changes in tracing.py and metrics code

## 3. pydantic-ai Upgrade

- [x] 3.1 Update pydantic-ai ceiling from <2.19 to >=2.31.0,<2.32 in agent-core, agent-harness, agent-docs-sync
- [x] 3.2 Verify pydantic-ai-harness==0.11.0 compatibility with pydantic-ai 2.31.x
- [x] 3.3 Run `uv sync` and verify dependency resolution
- [x] 3.4 Run full test suite across all 3 affected repos
- [x] 3.5 Fix any API breakage from the 12-version jump
- [x] 3.6 Verify Agent, AgentSpec, Model, infer_model, AnthropicModel APIs work correctly

## 4. atlassian-python-api Upgrade

- [x] 4.1 Update atlassian-python-api from <4.0.0 to >=5.0.0,<6.0.0 in tdt-core and jira-skill
- [x] 4.2 Run `uv sync` and verify dependency resolution
- [x] 4.3 Run full test suite across tdt-core and jira-skill
- [x] 4.4 Fix any breaking changes from the major version bump

## 5. Final Verification

- [x] 5.1 Run full test suite across all 6 target repos
- [x] 5.2 Run mypy strict across all 6 target repos
- [x] 5.3 Run ruff check across all 6 target repos
- [x] 5.4 Verify pre-commit hook versions are current (ruff v0.16.3, uv 0.12.5, gitleaks v8.30.1)
- [x] 5.5 Run OpenSpec validation
- [x] 5.6 Commit all changes
- [x] 5.7 Archive the change

# Proposal: SHB Dependency Modernization and Feature Integration

## Why
The 12 repositories in the Saigon - Hanoi Commercial Joint Stock Bank (`shb`) autonomous agent ecosystem (`~/Developer/shb/`) currently execute with a 100% green test baseline (115/115 passing tests on Python 3.14) but rely on fragmented, older dependency constraints (such as `pydantic-ai>=2.51.0`, `fastapi>=0.115.0`, `uvicorn>=0.34.0`, and disparate `pydantic`/`rich`/`typer` pins). Modernizing these dependencies to their latest stable PyPI releases aligns the ecosystem with upstream official standards:
- **Pydantic AI v2 (2.53.0)**: Unlocks static/dynamic instruction caching separation (`@agent.instructions` vs `@agent.system_prompt`), stable `AgentRunResult` serialization, and typed `RunContext` dependency evaluation.
- **FastAPI (0.142.2) & Starlette (1.7.0)**: Migrates legacy startup/shutdown event handlers to modern `@asynccontextmanager` application lifespan contexts, eliminating Starlette test client deprecation warnings.
- **Mypy (2.4.0) & Ruff (0.16.10)**: Upgrades the developer toolchain for native Python 3.14 AST type inference, TypeIs narrowing, and strict async context manager verification.

## What Changes
- **Pydantic AI 2.53.0 Upgrade**: Upgrade `pydantic-ai` from `>=2.51.0` to `>=2.53.0` in `shb-agent-core`, integrating streaming partial structured output validation and dynamic system prompt dependency evaluation.
- **FastAPI 0.142.2 & Uvicorn 0.54.0 Modernization**: Upgrade `fastapi` (from `>=0.115.0` to `>=0.142.2`) and `uvicorn` (from `>=0.34.0` to `>=0.54.0`) in `shb-webhook-receiver`, migrating lifespan event handling and eliminating Starlette test client deprecation warnings.
- **Ecosystem Pin Standardization**: Standardize lower-bound dependency constraints across all 12 repositories to latest stable baselines: `pydantic>=2.13.5`, `typer>=0.27.2`, `rich>=15.0.0`, `pyyaml>=6.0.3`, and `python-dotenv>=1.2.4`.
- **Toolchain Modernization**: Upgrade dev dependencies across all 12 packages to `mypy>=2.4.0`, `ruff>=0.16.10`, and `pytest-mock>=3.16.0`.
- **Lockfile Synchronization**: Run `uv sync --upgrade` in all 12 repositories to produce freshly locked and reproducible virtual environments.

## Capabilities

### Modified Capabilities
- `shb-agent-runtime`: Update autonomous ReAct execution engine requirements to enforce Pydantic AI `>=2.53.0` with streaming structured validation and typed dependency isolation.
- `shb-webhook-ingress`: Update webhook receiver requirements to mandate FastAPI `>=0.142.2` with async lifespan context management and Starlette 0.45+ test client integration.
- `shb-core-foundation`: Update configuration and security foundation requirements to enforce `python-dotenv>=1.2.4` and unified `pydantic>=2.13.5` models.

## Impact
- **Repositories**: All 12 SHB repositories under `~/Developer/shb/`.
- **Dependencies**: `pydantic-ai`, `fastapi`, `uvicorn`, `python-dotenv`, `pytest-mock`, `mypy`, `ruff`, `pyyaml`, `pydantic`, `typer`, `rich`.
- **APIs & Runtime**: Zero breaking changes to public CLI interfaces (`shb`, `shb-agent`, `shb-harness`, `shb-mcp`, etc.) or banking tool contracts. Backward-compatible clean-break upgrade.

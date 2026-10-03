# Design: SHB Dependency Modernization and Feature Integration

## Context
See `proposal.md` for motivation and scope. The SHB ecosystem encompasses 12 independent repositories under `~/Developer/shb/` running on Python 3.14 and managed via `uv`. The current test baseline is 115/115 passing tests across all repositories. However, dependency lower bounds are fragmented and several key packages (`pydantic-ai`, `fastapi`, `uvicorn`, `mypy`) lag behind latest stable PyPI releases.

## Goals / Non-Goals

**Goals:**
- Upgrade external runtime dependencies to current stable releases: `pydantic-ai>=2.53.0`, `fastapi>=0.142.2`, `uvicorn>=0.54.0`, `python-dotenv>=1.2.4`.
- Standardize uniform baseline constraints across all 12 `pyproject.toml` files (`pydantic>=2.13.5`, `typer>=0.27.2`, `rich>=15.0.0`, `pyyaml>=6.0.3`).
- Upgrade developer toolchain (`mypy>=2.4.0`, `ruff>=0.16.10`, `pytest-mock>=3.16.0`).
- Integrate new upstream capabilities: Pydantic AI streaming partial structured validation and dynamic prompt dependency refresh, FastAPI Starlette 0.45+ lifespan handlers, and Mypy 2.4 Python 3.14 AST support.
- Maintain 100% test pass rate across all 12 repositories under `-p no:cacheprovider`.

**Non-Goals:**
- Upgrading to unreleased or experimental alpha/beta packages.
- Modifying underlying banking business rules (such as the 50,000,000 VND maker-checker threshold or NAPAS247 CRC algorithms).
- Introducing new external services outside the existing stack.

## Decisions

### 1. Phased 3-Tier Upgrade Sequence
- **Decision**: Execute dependency upgrades in three sequential tiers:
  - *Tier 1: Toolchain & Linters* (`ruff>=0.16.10`, `mypy>=2.4.0`, `pytest-mock>=3.16.0`).
  - *Tier 2: Core Foundation & Infrastructure* (`shb-core`, `python-dotenv>=1.2.4`, `pyyaml>=6.0.3`, `fastapi>=0.142.2`, `uvicorn>=0.54.0`).
  - *Tier 3: Agent Core & Harness Orchestration* (`shb-agent-core`, `pydantic-ai>=2.53.0`, `shb-agent-harness`, `shb-mcp-servers`).
- **Rationale**: Isolates breaking syntax/type issues before touching core agent reasoning and LangGraph DAG execution.
- **Alternatives Considered**: Monolithic simultaneous upgrade of all 12 repos at once (rejected: harder to isolate regression origins).

### 2. Adoption of FastAPI Async Lifespan Protocol
- **Decision**: Migrate `shb-webhook-receiver` lifespan handling to `@asynccontextmanager` Lifespan protocol supported in FastAPI 0.142.2 and Starlette 0.45+, resolving legacy `httpx` deprecation warnings in test client executions.
- **Rationale**: Deprecated startup/shutdown event handlers emit warnings and will be removed in future Starlette versions.
- **Alternatives Considered**: Suppressing `StarletteDeprecationWarning` in pytest flags (rejected: violates "do not work around" policy).

### 3. Leverage Pydantic AI 2.53.0 Streaming & Dependency Validation
- **Decision**: Utilize Pydantic AI 2.53.0 enhanced `RunContext` dependency injection and structured validation hooks for banking tools.
- **Rationale**: Provides stronger type safety for banking transaction queries and runtime context injection.
- **Alternatives Considered**: Retaining 2.51.0 constraints (rejected: leaves ecosystem on older runtime).

## Risks / Trade-offs

- **[Risk: Pydantic AI 2.53.0 model schema or TestModel changes]** → Run `test_agent.py` and `test_banking_tools.py` with `TestModel` after sync to verify deterministic offline execution remains intact.
- **[Risk: Starlette 0.45+ TestClient behavior shifts in FastAPI]** → Verify `test_webhook.py` using `httpx` async client or updated Starlette test client.
- **[Risk: Mypy 2.4 stricter type checking on Python 3.14 generics]** → Run `uv run mypy src/` across all 12 repos with explicit type annotations where inferred types tighten.

## Migration Plan

1. **Pre-upgrade baseline verification**: Confirm all 115 tests pass.
2. **Tier 1 Toolchain update**: Update `ruff`, `mypy`, `pytest-mock` in all `pyproject.toml` files, execute `uv sync`, run lint checks.
3. **Tier 2 Core & Ingress update**: Update `shb-core` and `shb-webhook-receiver`, update lifespan handlers, execute `uv sync` and run tests.
4. **Tier 3 Agent & Harness update**: Update `shb-agent-core`, `shb-agent-harness`, `shb-mcp-servers`, execute `uv sync` and run agent reasoning tests.
5. **Full ecosystem verification**: Run comprehensive test suite across all 12 repositories and verify CLI entrypoints (`shb doctor`, `shb-agent tools-list`, `shb-harness list-stages`, `shb-mcp list-tools`).

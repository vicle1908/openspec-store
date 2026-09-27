# Design: SHB Ecosystem Syntax Modernization and Deprecation Remediation

## Context

A comprehensive codebase audit across the 12 repositories of the Saigon - Hanoi Bank (SHB) ecosystem (`~/Developer/shb/`) revealed 74 occurrences of deprecated patterns, legacy typing constructs (PEP 585 / PEP 604), timezone-naive UTC datetime calls (`datetime.utcnow()`), Pydantic v1 methods, unchained exception handling (`B904`), long CLI options (>100 chars), and unused imports. All repositories run on Python 3.14 via `uv`. Modernizing these patterns aligns the code with modern Python clean-break standards, eliminates future Python version runtime deprecation warnings, and ensures robust exception tracing across banking CLI tools and micro-agents.

See `proposal.md` for motivation and scope boundaries.

## Official Documentation Comparison Matrix

| Technology / Standard | Legacy Pattern in Codebase | Latest Official Standard | Target Specification |
|---|---|---|---|
| **Python Datetime** (Python 3.12+) | `datetime.utcnow()` | `datetime.now(timezone.utc)` | PEP 615 / Python 3.12+ stdlib docs |
| **Python Typing** (PEP 585) | `from typing import List, Dict, Set, Tuple` | Builtin `list[...]`, `dict[...]`, `set[...]`, `tuple[...]` | PEP 585 / Python 3.9+ typing docs |
| **Python Typing** (PEP 604) | `from typing import Optional, Union` | Pipe union syntax `T \| None`, `A \| B` | PEP 604 / Python 3.10+ typing docs |
| **Exception Handling** (PEP 3134 / B904) | `raise ValueError(...)` inside `except` | Explicit chaining: `raise ... from err` or `from None` | Python 3.11+ traceback standards |
| **Pydantic Validation** (Pydantic v2.10+) | `@validator("field")` | `@field_validator("field")` with `@classmethod` | Pydantic v2 Migration Guide |
| **Pydantic Copying** (Pydantic v2.10+) | `model.copy()` | `model.model_copy()` | Pydantic v2 Migration Guide |
| **Typer CLI Options** (Typer 0.9.0+) | Inline long default options (>100 chars) | Wrapped `typer.Option(...)` or `Annotated` | Typer official parameter docs |
| **Docker Compose** (Compose Spec) | Obsolete `version: '3.8'` | Omitted `version:` attribute (already clean) | Docker Compose Specification |
| **FastAPI Ingress** (FastAPI 0.115+) | Obsolete `@app.on_event` | `lifespan` context manager (already clean) | FastAPI Events & Lifespan docs |

## Goals / Non-Goals

**Goals:**
- Migrate all `from typing import List, Dict, Set, Tuple` to builtin collections (`list`, `dict`, `set`, `tuple`) per PEP 585 across active production code.
- Migrate all `from typing import Optional, Union` to native pipe syntax (`X | None`, `A | B`) per PEP 604.
- Replace all `datetime.utcnow()` instantiations with `datetime.now(timezone.utc)`.
- Replace legacy Pydantic v1 `@validator` with `@field_validator` and `@classmethod` signatures.
- Add explicit exception chaining (`raise ... from err` or `raise ... from None`) in exception handlers to comply with `B904`.
- Reformat `shb-jira-tools/src/shb_jira/cli.py` to resolve Ruff `E501` line length violations (>100 chars).
- Remove empty f-strings (`F541`) and unused imports (`F401`) across production source modules.
- Preserve 100% test passing rate (81/81 unit tests passing) without regressions.

**Non-Goals:**
- Modifying intentionally non-compliant test fixtures under `shb-agent-skills/skills/hexagonal-compliance-skill/tests/fixtures/python-noncompliant/` which exist specifically to test anti-pattern static detection rules.
- Introducing new third-party dependencies or altering public SDK interfaces.
- Re-architecting domain service logic or database schemas.

## Decisions

### Decision 1: Target Production Packages First, Keep Intentional Anti-Pattern Fixtures Intact
- **Rationale**: The `hexagonal-compliance-skill` in `shb-agent-skills` contains test fixtures specifically named `python-noncompliant` that are used to assert that the compliance scanner correctly flags `datetime.utcnow()` and legacy imports. Mutating those test fixtures would break the test suite's assertion of negative cases. The compliant fixture (`python-compliant/domain/entities/user.py`), integration tests, and all production library packages (`src/`) must be modernized.
- **Alternatives considered**:
  - Global find-and-replace across all files: Rejected because it would invalidate negative compliance test suites.

### Decision 2: Automated Ruff Fixes Combined with ast-grep Structural Refactoring
- **Rationale**: Ruff's `--select UP006,UP007,UP035 --fix` accurately handles standard typing import modernizations (PEP 585 and PEP 604) without introducing syntax errors. Structural AST changes (`datetime.now(timezone.utc)`, Pydantic v2 decorators, and exception chaining) are applied via targeted edits and validated with test execution.
- **Alternatives considered**:
  - Manual edits across 74 sites: Error-prone and slower.
  - Blind regex search-and-replace: Can break multiline signatures or string literals.

### Decision 3: Zero .pytest_cache Pollution Standard
- **Rationale**: All test runs continue enforcing `-p no:cacheprovider` to prevent scrap directories from polluting repository roots.

## Risks / Trade-offs

- **[Risk] Type hint changes affecting Pydantic runtime parsing** → *Mitigation*: Run full test suite (`uv run pytest`) after every package edit; Pydantic v2 natively supports PEP 585 and PEP 604 syntax.
- **[Risk] Timezone-aware vs naive datetime comparison in tests** → *Mitigation*: Ensure entities generating `timezone.utc` timestamps are compared against timezone-aware references in test assertions.

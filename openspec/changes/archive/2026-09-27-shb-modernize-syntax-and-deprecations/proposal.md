# Proposal: SHB Ecosystem Syntax Modernization and Deprecation Remediation

## Why

Comprehensive AST and static lint analysis across all 12 repositories of the Saigon - Hanoi Bank (SHB) ecosystem (`~/Developer/shb/`) revealed 74 occurrences of deprecated idioms and legacy syntax when evaluated against modern official standards (Python 3.12+/3.14 stdlib, PEP 585, PEP 604, PEP 3134, Pydantic v2.10+, and Typer 0.9+). These include deprecated `datetime.utcnow()` (scheduled for removal in Python 3.14+), legacy `typing` imports (`List`, `Dict`, `Set`, `Tuple`, `Optional`, `Union`), Pydantic v1 legacy validators (`@validator`) and copy methods (`.copy()`), unchained exception raises in `except` blocks (`B904`), long CLI options causing Ruff `E501` line length violations, and dead imports/empty f-strings. Modernizing these repositories ensures long-term runtime compatibility, eliminates future Python version deprecation warnings, and upholds high-assurance banking compliance.

## What Changes

- **PEP 585 & PEP 604 Modernization**: Replace legacy `typing` constructs (`List`, `Dict`, `Set`, `Tuple`, `Optional`, `Union`) with native builtin types (`list`, `dict`, `set`, `tuple`) and pipe union syntax (`X | None`, `A | B`) across all active production code in `shb-core`, `shb-agent-core`, `shb-browser-cli`, and `shb-agent-skills`.
- **UTC Datetime Migration**: Replace deprecated `datetime.utcnow()` with timezone-aware `datetime.now(timezone.utc)` in entity definitions and compliant test fixtures per PEP 615.
- **Pydantic v2 Standardization**: Upgrade legacy Pydantic v1 `@validator` decorators to Pydantic v2 `@field_validator` with `@classmethod` signatures, and replace legacy `.copy()` with `.model_copy()` or standard dictionary copy.
- **Exception Chaining (`B904`)**: Ensure exceptions raised within `except` blocks use explicit chaining (`raise ... from err` or `raise ... from None`) to maintain traceable error causality across banking CLI commands and SDK clients.
- **CLI Formatting and Lint Cleanup**: Reformat long CLI option signatures in `shb-jira-tools` to adhere to the 100-character line limit (`E501`) and Typer parameter conventions; eliminate unused imports (`F401`) and redundant empty f-strings (`F541`) in `shb-core`, `shb-observability`, `shb-webhook-receiver`, and `shb-ai-review`.
- **Specification Update**: Amend canonical `shb-ecosystem-tooling` specification to formalize strict modern syntax, zero-deprecation quality gates, and exception chaining across all SHB repositories.

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `shb-ecosystem-tooling`: Updates `Requirement: Python Packaging and Quality Standardization` and adds `Requirement: Codebase Deprecation and Anti-Pattern Elimination` prohibiting deprecated Python stdlib APIs, legacy typing imports, and unchained exceptions across the SHB organization.

## Impact

- **Affected Code**: All Python production packages under `~/Developer/shb/` (`shb-core`, `shb-agent-core`, `shb-agent-harness`, `shb-ai-harness-skills`, `shb-agent-skills`, `shb-browser-cli`, `shb-ai-review`, `shb-webhook-receiver`, `shb-jira-tools`, `shb-mcp-servers`, `shb-observability`).
- **Dependencies**: No external runtime dependency additions; leverages existing Python 3.14 builtins and Pydantic v2.
- **Testing**: All 81 unit tests across the SHB ecosystem must continue to pass with zero regressions.

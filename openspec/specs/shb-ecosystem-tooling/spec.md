# shb-ecosystem-tooling Specification

## Purpose
Establishes multi-repository layout standards, Python package tooling, quality verification gates, and code intelligence registration for Saigon - Hanoi Bank (SHB).

## Requirements

### Requirement: Independent Multi-Repository Directory Structure
The `shb` organization SHALL reside at `~/Developer/shb/` as an organizational directory where each child repository is an independent Git repository possessing its own `.git` directory, version control history, and lifecycle.

#### Scenario: Repository isolation verification
- **WHEN** Git status is checked within any repository under `~/Developer/shb/`
- **THEN** the repository operates as an independent Git work tree without treating neighboring repositories as submodules or parent directories

### Requirement: Python Packaging and Quality Standardization
All Python repositories in the `shb` ecosystem SHALL use `uv` for dependency management with Python version requirements `>=3.14`, Ruff for linting and formatting (line length 100), strict Mypy type checking, and modern Python clean-break syntax including PEP 585 builtin generic types (`list`, `dict`, `set`, `tuple`), PEP 604 union types (`T | None`, `A | B`), timezone-aware UTC datetimes (`datetime.now(timezone.utc)`), and Pydantic v2 validation contracts.

#### Scenario: Dependency synchronization and test execution
- **WHEN** an engineer executes `uv sync` followed by `uv run pytest` in any SHB repository
- **THEN** virtual environments are provisioned with pinned dependencies and the test suite executes successfully without root cache pollution

#### Scenario: Clean-break typing and syntax validation
- **WHEN** static analysis via Ruff (`UP006`, `UP007`, `UP035`) is executed across any SHB repository
- **THEN** zero violations SHALL be reported for deprecated `typing.List`, `typing.Dict`, `typing.Optional`, or `typing.Union` constructs

#### Scenario: Line length and CLI parameter formatting
- **WHEN** static analysis checks line length compliance across all CLI entrypoints
- **THEN** zero violations of Ruff `E501` (>100 characters) SHALL exist
- **AND** Typer CLI options SHALL be structured using wrapped parameters or `Annotated` definitions

### Requirement: Code Intelligence and Knowledge Refresh Registration
The SHB repositories SHALL be registered in `~/Developer/scripts/knowledge-refresh/knowledge-refresh-inventory.tsv` to ensure inclusion in nightly GitNexus code intelligence and Graphify knowledge graph indexing, and every active repository SHALL maintain up-to-date semantic and structural knowledge indices.

#### Scenario: Knowledge refresh inventory verification
- **WHEN** the knowledge refresh audit script `knowledge-status.sh` is executed
- **THEN** all 12 active SHB repositories are reported as valid managed targets eligible for automated indexing

#### Scenario: GitNexus semantic index freshness
- **WHEN** `gitnexus status` is executed within any SHB repository root
- **THEN** the analyzer SHALL report status as up-to-date and matching the current repository HEAD commit

#### Scenario: Global knowledge graph registration
- **WHEN** `graphify global list` is executed
- **THEN** all 12 SHB repositories SHALL appear in the global graph registry with non-zero node counts

### Requirement: In-Repository Knowledge Configuration and Git Hygiene
Every SHB repository SHALL include an in-repo `.gitnexusrc` configuration file specifying local embedding models and concurrency parameters, SHALL maintain a tracked `graphify-out/graph.json` AST knowledge graph with automated merge drivers, and SHALL configure `.gitignore` to prevent tracking of LadybugDB vector indexes.

#### Scenario: GitNexus configuration presence
- **WHEN** inspecting the root of any SHB repository
- **THEN** a `.gitnexusrc` file SHALL exist containing `embeddings: true`, `embeddingBaseUrl` pointing to Ollama, and `embeddingModel` set to `nomic-embed-text`

#### Scenario: Graphify hook and gitignore hygiene
- **WHEN** Git operations occur within any SHB repository
- **THEN** the `.gitnexus/` directory SHALL be ignored by `.gitignore`
- **AND** `graphify-out/graph.json` SHALL be tracked in version control while `graphify-out/20*/` snapshots are ignored
- **AND** a Graphify post-commit hook SHALL be installed in `.git/hooks/`

### Requirement: Developer Toolchain Standardization and Feature Enablement
Development across the SHB ecosystem SHALL standardize on modernized developer tooling with all feature capabilities enabled, specifically Notion CLI (`ntn`) v0.23.10+, Graphify v0.9.69+ with complete optional extras, GitNexus v1.6.12+ with native vector support, and AgentMemory v0.9.29+ with B+ flags activated.

#### Scenario: Notion CLI setup verification
- **WHEN** `ntn doctor` is executed in the developer environment
- **THEN** it SHALL verify CLI version v0.23.10 or higher, valid workspace resolution, and successful Workers and Public API authentication

#### Scenario: AgentMemory full feature activation
- **WHEN** `agentmemory doctor` is executed
- **THEN** all 9 server diagnostics SHALL pass including observation compression, knowledge graph extraction, memory consolidation, and context injection

### Requirement: Codebase Deprecation and Anti-Pattern Elimination
All Python source files and operational test fixtures across the SHB organization SHALL eliminate deprecated Python standard library calls, legacy Pydantic v1 methods, and unchained exception raises within `except` blocks.

#### Scenario: Timezone-aware UTC datetime enforcement
- **WHEN** inspecting datetime instantiations across SHB source and compliant test entity definitions
- **THEN** zero occurrences of deprecated `datetime.utcnow()` or `datetime.utcfromtimestamp()` SHALL exist
- **AND** all UTC timestamps SHALL be generated via `datetime.now(timezone.utc)`

#### Scenario: Explicit exception chaining
- **WHEN** an exception is raised within an `except` handler in any SHB application or CLI entrypoint
- **THEN** the exception SHALL explicitly chain the root cause using `from err` or `from None` per Python `B904` standards

#### Scenario: Pydantic v2 decorator and model method compliance
- **WHEN** Pydantic models and validation logic are defined in SHB repositories
- **THEN** field and model validations SHALL use `@field_validator` or `@model_validator`
- **AND** model serialization and copying SHALL use `.model_dump()`, `.model_dump_json()`, or `.model_copy()` rather than deprecated v1 methods

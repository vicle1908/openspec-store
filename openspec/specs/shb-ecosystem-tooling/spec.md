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
All Python repositories in the `shb` ecosystem SHALL use `uv` for dependency management with Python version requirements `>=3.14`, Ruff for linting and formatting (line length 100), and strict Mypy type checking.

#### Scenario: Dependency synchronization and test execution
- **WHEN** an engineer executes `uv sync` followed by `uv run pytest` in any SHB repository
- **THEN** virtual environments are provisioned with pinned dependencies and the test suite executes successfully without root cache pollution

### Requirement: Code Intelligence and Knowledge Refresh Registration
The SHB repositories SHALL be registered in `~/Developer/scripts/knowledge-refresh/knowledge-refresh-inventory.tsv` to ensure inclusion in nightly GitNexus code intelligence and Graphify knowledge graph indexing.

#### Scenario: Knowledge refresh inventory verification
- **WHEN** the knowledge refresh audit script `knowledge-status.sh` is executed
- **THEN** the active SHB repositories are reported as valid managed targets eligible for automated indexing

# UV Ecosystem Standardization

**Capability:** uv-ecosystem-standardization
**Status:** Implemented (2026-07-25)
**Date:** 2026-07-25

## Purpose

Enforce uv package manager practices across all TDT Python repositories for consistent dependency management, environment configuration, and developer experience.

## Requirements

### Requirement: uv.lock presence
All Python repos with pyproject.toml SHALL have a committed uv.lock file.

#### Scenario: Missing uv.lock
- **WHEN** a Python repo has pyproject.toml but no uv.lock
- **THEN** `uv sync` is run to generate uv.lock, and it is committed

### Requirement: .python-version presence
All Python repos with pyproject.toml SHALL have a .python-version file matching requires-python.

#### Scenario: Missing .python-version
- **WHEN** a Python repo has pyproject.toml but no .python-version
- **THEN** a .python-version file is created with the appropriate Python version

### Requirement: AGENTS.md uv practices
All Python repos SHALL have a uv practices section in AGENTS.md.

#### Scenario: Missing uv practices
- **WHEN** a Python repo's AGENTS.md lacks uv practices
- **THEN** a uv practices section is added with standard commands

### Requirement: No pip references in active docs
Active documentation SHALL NOT reference `pip install`.

#### Scenario: Pip reference found
- **WHEN** an active .md doc contains `pip install`
- **THEN** the reference is replaced with `uv add`

### Requirement: Standard [tool.uv] configuration
All Python repos SHALL have consistent [tool.uv] in pyproject.toml.

#### Scenario: Missing or inconsistent config
- **WHEN** a Python repo lacks or has non-standard [tool.uv]
- **THEN** the standard config is added or updated

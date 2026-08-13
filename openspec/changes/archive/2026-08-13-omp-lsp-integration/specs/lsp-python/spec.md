## Purpose
Configure pyright/basedpyright for the `agent-core` and `tdt-core` Python repositories with project-appropriate type-checking strictness, shared Python version targeting, and correct source paths so type errors are caught early and formatting is consistent.

## ADDED Requirements

### Requirement: project-level lsp.json existence
Both `agent-core/.omp/lsp.json` and `tdt-core/.omp/lsp.json` SHALL exist with Python-specific LSP overrides that extend the user-level defaults.

#### Scenario: both project-level configs present
- **WHEN** the agent opens a Python file in `agent-core/` or `tdt-core/`
- **THEN** the corresponding `.omp/lsp.json` SHALL be loaded and merged on top of `~/.omp/agent/lsp.json`

#### Scenario: project-level config missing
- **WHEN** the agent opens a Python file in `agent-core/` or `tdt-core/` and the project-level `.omp/lsp.json` does not exist
- **THEN** only user-level defaults SHALL apply and a warning SHALL be logged

### Requirement: agent-core strict type checking
`agent-core/.omp/lsp.json` SHALL configure pyright/basedpyright with `typeCheckingMode` set to `'strict'`.

#### Scenario: strict diagnostics in agent-core
- **WHEN** a Python file in `agent-core/` is opened or edited
- **THEN** pyright/basedpyright SHALL perform strict type checking and report all type errors, including optional-missing and unused imports

#### Scenario: strict mode catches subtle type issues
- **WHEN** a developer writes code in `agent-core/` that uses an `Optional` without narrowing
- **THEN** pyright/basedpyright SHALL emit a type error diagnostic

### Requirement: tdt-core basic type checking
`tdt-core/.omp/lsp.json` SHALL configure pyright/basedpyright with `typeCheckingMode` set to `'basic'`.

#### Scenario: basic diagnostics in tdt-core
- **WHEN** a Python file in `tdt-core/` is opened or edited
- **THEN** pyright/basedpyright SHALL perform basic type checking and report high-confidence type errors only

#### Scenario: basic mode ignores low-confidence issues
- **WHEN** a developer writes code in `tdt-core/` with a low-confidence type ambiguity
- **THEN** pyright/basedpyright SHALL NOT emit a diagnostic for that issue under basic mode

### Requirement: python.version shared
Both `agent-core/.omp/lsp.json` and `tdt-core/.omp/lsp.json` SHALL set `python.version` to `'3.14'`.

#### Scenario: version targeting applied
- **WHEN** the Python language server starts for either project
- **THEN** it SHALL target Python 3.14 semantics for type checking and completions

### Requirement: python.analysis.extraPaths include src/
Both project-level configs SHALL set `python.analysis.extraPaths` to include the project's `src/` directory so imports from `src/` are resolved correctly.

#### Scenario: src/ import resolution in agent-core
- **WHEN** a Python file in `agent-core/` imports a module from `agent-core/src/`
- **THEN** pyright/basedpyright SHALL resolve the import and provide completions and diagnostics for it

#### Scenario: src/ import resolution in tdt-core
- **WHEN** a Python file in `tdt-core/` imports a module from `tdt-core/src/`
- **THEN** pyright/basedpyright SHALL resolve the import and provide completions and diagnostics for it

### Requirement: auto-format on save
WHEN a Python file is saved, it SHALL be formatted by the matching language server (ruff or basedpyright) per the user-level `formatOnWrite: true` default.

#### Scenario: ruff formatting
- **WHEN** a Python file in either project is saved and ruff is the configured formatter
- **THEN** the file SHALL be formatted by ruff before the write completes

#### Scenario: basedpyright formatting fallback
- **WHEN** a Python file in either project is saved and ruff is not available but basedpyright is
- **THEN** the file SHALL be formatted by basedpyright before the write completes

### Requirement: pyright fallback when not installed
WHEN pyright/basedpyright is not found on the system, auto-detection SHALL fall back to basedpyright or pylsp without crashing.

#### Scenario: pyright binary missing
- **WHEN** the agent starts and neither `pyright` nor `basedpyright` is found on `$PATH`
- **THEN** auto-detection SHALL fall back to basedpyright, then to pylsp, and log a warning if none are found

#### Scenario: basedpyright found, pyright not
- **WHEN** the agent starts and `basedpyright` is on `$PATH` but `pyright` is not
- **THEN** basedpyright SHALL be used as the primary language server

#### Scenario: both pyright and basedpyright missing
- **WHEN** the agent starts and neither `pyright` nor `basedpyright` is found but `pylsp` is
- **THEN** pylsp SHALL be used as the primary language server and a warning SHALL be logged recommending pyright/basedpyright installation

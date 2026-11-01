## Purpose
Configure pyright/basedpyright for the `agent-core` and `tdt-core` Python repositories with project-appropriate type-checking strictness, shared Python version targeting, and correct source paths so type errors are caught early and formatting is consistent.

## Requirements

### Requirement: project-level lsp.json existence

User-level `~/.omp/agent/lsp.json` SHALL provide the canonical Python LSP configuration (`basedpyright` and `ruff` with `python.version: "3.15"` and `python.analysis.extraPaths: ["src"]`) across all workspace Python repositories, while optional project-level `.omp/lsp.json` files merge on top when present without dirtying tracked git worktrees.

#### Scenario: both project-level configs present
- **WHEN** the agent opens a Python file in a repository that defines `.omp/lsp.json`
- **THEN** the project-level `.omp/lsp.json` SHALL be loaded and merged on top of `~/.omp/agent/lsp.json`

#### Scenario: project-level config missing
- **WHEN** the agent opens a Python file in `tdt/agent-core/` or `tdt/tdt-core/` and no project-level `.omp/lsp.json` exists
- **THEN** the user-level `~/.omp/agent/lsp.json` (`basedpyright` + `ruff`, `python.version: "3.15"`) SHALL apply cleanly without warnings

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

User-level `~/.omp/agent/lsp.json` (and any optional project-level Python `.omp/lsp.json` override) SHALL set `python.version` to `'3.15'` to match the workspace CPython `3.15.1` (`requires-python >=3.15`) standard.

#### Scenario: version targeting applied
- **WHEN** the Python language server (`basedpyright`) starts for any workspace Python project
- **THEN** it SHALL target Python `3.15` semantics for type checking, hover, and completions

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

### Requirement: cwd-only root marker detection

OMP LSP startup root-marker detection (`wZ(cwd, server.rootMarkers)`) is cwd-only; `~/.omp/agent/lsp.json` SHALL include `".git"` and `".claude"` in `rootMarkers` for `basedpyright` and `ruff` so Python language servers activate both inside individual Python repositories and from the `/Users/androidteam/Developer` multi-repo root.

#### Scenario: basedpyright activates from project dir
- **WHEN** the agent launches from `~/Developer/tdt/agent-core/` or a standalone git repository
- **THEN** `pyproject.toml` or `.git` exists in cwd and `basedpyright` and `ruff` SHALL be active

#### Scenario: basedpyright filtered from workspace root
- **WHEN** the agent launches from `/Users/androidteam/Developer/` (which contains `.claude` and `.git`)
- **THEN** `basedpyright` and `ruff` SHALL match the `.claude`/`.git` root markers in `~/.omp/agent/lsp.json` and attach sub-repository folders dynamically on file open

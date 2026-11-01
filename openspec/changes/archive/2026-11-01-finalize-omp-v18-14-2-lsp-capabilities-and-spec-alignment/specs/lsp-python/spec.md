# lsp-python Specification Delta

## MODIFIED Requirements

### Requirement: project-level lsp.json existence

User-level `~/.omp/agent/lsp.json` SHALL provide the canonical Python LSP configuration (`basedpyright` and `ruff` with `python.version: "3.15"` and `python.analysis.extraPaths: ["src"]`) across all workspace Python repositories, while optional project-level `.omp/lsp.json` files merge on top when present without dirtying tracked git worktrees.

#### Scenario: both project-level configs present
- **WHEN** the agent opens a Python file in a repository that defines `.omp/lsp.json`
- **THEN** the project-level `.omp/lsp.json` SHALL be loaded and merged on top of `~/.omp/agent/lsp.json`

#### Scenario: project-level config missing
- **WHEN** the agent opens a Python file in `tdt/agent-core/` or `tdt/tdt-core/` and no project-level `.omp/lsp.json` exists
- **THEN** the user-level `~/.omp/agent/lsp.json` (`basedpyright` + `ruff`, `python.version: "3.15"`) SHALL apply cleanly without warnings

### Requirement: python.version shared

User-level `~/.omp/agent/lsp.json` (and any optional project-level Python `.omp/lsp.json` override) SHALL set `python.version` to `'3.15'` to match the workspace CPython `3.15.1` (`requires-python >=3.15`) standard.

#### Scenario: version targeting applied
- **WHEN** the Python language server (`basedpyright`) starts for any workspace Python project
- **THEN** it SHALL target Python `3.15` semantics for type checking, hover, and completions

### Requirement: cwd-only root marker detection

OMP LSP startup root-marker detection (`wZ(cwd, server.rootMarkers)`) is cwd-only; `~/.omp/agent/lsp.json` SHALL include `".git"` and `".claude"` in `rootMarkers` for `basedpyright` and `ruff` so Python language servers activate both inside individual Python repositories and from the `/Users/androidteam/Developer` multi-repo root.

#### Scenario: basedpyright activates from project dir
- **WHEN** the agent launches from `~/Developer/tdt/agent-core/` or a standalone git repository
- **THEN** `pyproject.toml` or `.git` exists in cwd and `basedpyright` and `ruff` SHALL be active

#### Scenario: basedpyright filtered from workspace root
- **WHEN** the agent launches from `/Users/androidteam/Developer/` (which contains `.claude` and `.git`)
- **THEN** `basedpyright` and `ruff` SHALL match the `.claude`/`.git` root markers in `~/.omp/agent/lsp.json` and attach sub-repository folders dynamically on file open

## Purpose
Establish user-level LSP defaults at `~/.omp/agent/lsp.json` so every project inherits consistent editor behavior—real-time diagnostics, auto-formatting on save, and automatic idle shutdown—without per-repo setup.

## Requirements

### Requirement: user-level lsp.json existence
`~/.omp/agent/lsp.json` SHALL exist at agent startup and SHALL contain all user-level LSP defaults described in this spec. If the file does not exist on first launch, it SHALL be created with the default values below.

#### Scenario: lsp.json missing on first launch
- **WHEN** the agent starts and `~/.omp/agent/lsp.json` does not exist
- **THEN** the file SHALL be created with the default LSP configuration and the editor SHALL continue without error

#### Scenario: lsp.json already present
- **WHEN** the agent starts and `~/.omp/agent/lsp.json` already exists
- **THEN** the existing file SHALL be loaded without modification

### Requirement: diagnosticsOnWrite default
`diagnosticsOnWrite` SHALL default to `true` so diagnostics refresh whenever a file is written to disk.

#### Scenario: diagnostics refresh on save
- **WHEN** a file is saved (written)
- **THEN** the matching language server SHALL re-analyze the file and report diagnostics in real-time

### Requirement: diagnosticsOnEdit override
`diagnosticsOnEdit` SHALL be set to `true`, overriding the framework default of `false`, so diagnostics appear as the user types.

#### Scenario: real-time diagnostics while editing
- **WHEN** a file is edited (unsaved buffer change)
- **THEN** the matching language server SHALL emit diagnostics in real-time without requiring an explicit save

### Requirement: formatOnWrite override
`formatOnWrite` SHALL be set to `true`, overriding the framework default of `false`, so files are auto-formatted on save.

#### Scenario: auto-format on save
- **WHEN** a file is saved
- **THEN** it SHALL be auto-formatted by the matching language server before the write completes

#### Scenario: formatOnWrite with unsaved edits
- **WHEN** a file has unsaved edits and is not yet saved
- **THEN** formatting SHALL NOT be triggered automatically

### Requirement: idleTimeoutMs shutdown
`idleTimeoutMs` SHALL be set to `300000` (5 minutes). When a language server receives no requests or notifications for this duration, it SHALL be shut down to reclaim resources.

#### Scenario: server idle shutdown
- **WHEN** a language server has been idle for 5 minutes with no document activity
- **THEN** the server process SHALL be terminated

#### Scenario: server activity resets idle timer
- **WHEN** a language server is about to idle-shutdown and receives a new request or notification
- **THEN** the idle timer SHALL reset and the server SHALL remain running

### Requirement: official OMP config hierarchy

OMP SHALL merge LSP config from five sources (lowest to highest precedence): `~/lsp.json`, plugin configs, `~/.omp/agent/lsp.json`, `<cwd>/.omp/lsp.json`, and `<cwd>/lsp.json`, while reading runtime diagnostic and formatting flags (`lsp.enabled`, `lsp.diagnosticsOnWrite`, `lsp.diagnosticsOnEdit`, `lsp.formatOnWrite`) from `~/.omp/agent/config.yml`.

#### Scenario: config merge order
- **WHEN** an agent opens a file
- **THEN** OMP SHALL merge server configs from all five levels, with higher-precedence overriding lower

#### Scenario: cwd-only root markers
- **WHEN** the agent launches from the multi-repo workspace root (`/Users/androidteam/Developer/`)
- **THEN** servers in `~/.omp/agent/lsp.json` whose `rootMarkers` include `.git` and `.claude` (`gopls`, `basedpyright`, `ruff`, `sourcekit-lsp`, `yaml-language-server`) SHALL pass startup cwd root-marker detection

### Requirement: project-scoped LSP activation

`~/.omp/agent/lsp.json` SHALL declare `gopls` (`/Users/androidteam/go/bin/gopls`), `basedpyright` (`/opt/homebrew/bin/basedpyright-langserver`), `ruff` (`/opt/homebrew/bin/ruff`, `isLinter: true`), `sourcekit-lsp` (`/usr/bin/sourcekit-lsp`), and `yaml-language-server` (`/Users/androidteam/.local/bin/yaml-language-server`) with `.git` and `.claude` in `rootMarkers` so `xd://lsp` activates from both individual project directories and `/Users/androidteam/Developer`.

#### Scenario: LSP active from project dir
- **WHEN** the agent launches from a project directory or opens a sub-repository file
- **THEN** OMP SHALL attach the sub-repository workspace folder dynamically via `workspace/didChangeWorkspaceFolders` and merge any project-local `.omp/lsp.json` overrides

#### Scenario: LSP inactive from workspace root
- **WHEN** the agent launches from `/Users/androidteam/Developer/` and queries `xd://lsp` with `{"action": "status"}`
- **THEN** `gopls`, `basedpyright`, `ruff`, `sourcekit-lsp`, and `yaml-language-server` SHALL report `(ready)` while servers without matching binaries or root markers remain inactive

### Requirement: User-Level Python 3.15 Target Alignment in lsp.json

`~/.omp/agent/lsp.json` SHALL configure `servers.basedpyright.settings["python.version"]` as `"3.15"` alongside `gopls`, `ruff`, `sourcekit-lsp`, and `yaml-language-server`, and `~/.omp/agent/config.yml` SHALL set `lsp: { enabled: true, diagnosticsOnWrite: true, diagnosticsOnEdit: true, formatOnWrite: true }`.

#### Scenario: basedpyright user-level config targets Python 3.15
- **WHEN** `/Users/androidteam/.omp/agent/lsp.json` and `/Users/androidteam/.omp/agent/config.yml` are parsed
- **THEN** `servers.basedpyright.settings["python.version"]` SHALL equal `"3.15"` and `idleTimeoutMs` SHALL equal `300000`
- **AND** `config.yml` SHALL set `lsp.enabled`, `lsp.diagnosticsOnWrite`, `lsp.diagnosticsOnEdit`, and `lsp.formatOnWrite` to `true`

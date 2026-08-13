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
OMP merges LSP config from five sources (lowest to highest precedence): `~/lsp.json` (home), plugin configs, `~/.omp/agent/lsp.json` (user config dir), `<cwd>/.omp/lsp.json` (cwd config dir), `<cwd>/lsp.json` (cwd root). Project and cwd sources do not walk ancestors. Root-marker detection at startup is cwd-only.

#### Scenario: config merge order
- **WHEN** an agent opens a file
- **THEN** OMP SHALL merge configs from all five levels, with higher-precedence overriding lower

#### Scenario: cwd-only root markers
- **WHEN** the agent launches from a workspace root (e.g. `~/Developer/`)
- **THEN** LSP servers whose rootMarkers do not match cwd files SHALL be filtered out
- **AND** the `lsp` tool SHALL report "No language servers configured"

### Requirement: project-scoped LSP activation
LSP is project-scoped. The agent MUST launch from inside a project directory (e.g. `~/Developer/agent-core/`) for LSP to activate. The `--add-dir` flag adds workspace directories but does NOT change cwd for LSP config resolution.

#### Scenario: LSP active from project dir
- **WHEN** the agent launches from `~/Developer/agent-core/`
- **THEN** `agent-core/.omp/lsp.json` SHALL be loaded and merged on user-level defaults
- **AND** basedpyright SHALL be available with project-specific settings

#### Scenario: LSP inactive from workspace root
- **WHEN** the agent launches from `~/Developer/` (workspace root)
- **THEN** no `.omp/lsp.json` exists at that level
- **AND** the `lsp` tool SHALL report no servers configured
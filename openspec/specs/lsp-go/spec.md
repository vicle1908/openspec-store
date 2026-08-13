## Purpose
Configure gopls for the `go-microservices` monorepo with strict static analysis, gofumpt formatting, expanded analysis checks, and integration-test build flags so Go code is validated and formatted consistently across all eight services.

## Requirements

### Requirement: go-microservices lsp.json existence
`go-microservices/.omp/lsp.json` SHALL exist with Go-specific LSP overrides that extend the user-level defaults. This file is project-scoped and applies only to the `go-microservices` repository.

#### Scenario: project-level lsp.json present
- **WHEN** the agent opens a file inside `go-microservices/`
- **THEN** `go-microservices/.omp/lsp.json` SHALL be loaded and merged on top of `~/.omp/agent/lsp.json`

#### Scenario: project-level lsp.json missing
- **WHEN** the agent opens a file inside `go-microservices/` and `go-microservices/.omp/lsp.json` does not exist
- **THEN** only user-level defaults SHALL apply and a warning SHALL be logged

### Requirement: gopls staticcheck enabled
The gopls configuration within `go-microservices/.omp/lsp.json` SHALL set `staticcheck` to `true`.

#### Scenario: static analysis on Go files
- **WHEN** a Go file in `go-microservices/` is opened, edited, or saved
- **THEN** gopls SHALL run staticcheck and surface any violations as diagnostics

### Requirement: gopls gofumpt formatting enabled
The gopls configuration SHALL set `gofumpt` to `true` so gofumpt (stricter gofmt) is used as the formatter.

#### Scenario: gofumpt formatting on save
- **WHEN** a Go file in `go-microservices/` is saved
- **THEN** the file SHALL be formatted by gofumpt via gopls

### Requirement: gopls analyses expanded
The gopls configuration SHALL set `analyses` to include at minimum `shadow`, `unusedwrite`, and `appendAssign`.

#### Scenario: shadow analysis catches variable shadowing
- **WHEN** a Go file contains a variable that shadows an outer binding
- **THEN** gopls SHALL emit a diagnostic for the shadow

#### Scenario: unusedwrite detects unused writes
- **WHEN** a Go file assigns a value that is never read
- **THEN** gopls SHALL emit a diagnostic for the unused write

#### Scenario: appendAssign flags suspicious append
- **WHEN** a Go file appends to a slice and the result is not assigned back
- **THEN** gopls SHALL emit a diagnostic for the suspicious append

### Requirement: gopls buildFlags include integration tag
The gopls configuration SHALL set `buildFlags` to include `-tags=integration` so test files using the `integration` build tag are included in analysis.

#### Scenario: integration test files are analyzed
- **WHEN** a Go test file in `go-microservices/` is gated behind `//go:build integration`
- **THEN** gopls SHALL include it in diagnostics and type checking

### Requirement: gopls formatting, type checking, and static analysis on edit
When editing Go code in `go-microservices/`, gopls SHALL provide static analysis, formatting, and type checking simultaneously.

#### Scenario: full LSP experience on Go edit
- **WHEN** a developer edits a Go file in `go-microservices/`
- **THEN** gopls SHALL provide completions, diagnostics (static analysis + type errors), and format-on-save

### Requirement: gopls fallback when not installed
WHEN gopls is not found on the system, auto-detection SHALL fall back to the built-in default gopls configuration without crashing.

#### Scenario: gopls binary missing
- **WHEN** the agent starts and `gopls` is not found on `$PATH`
- **THEN** auto-detection SHALL fall back to the built-in default gopls config and log a warning, and no Go diagnostics SHALL be generated until gopls is installed

#### Scenario: gopls binary present
- **WHEN** the agent starts and `gopls` is found on `$PATH`
- **THEN** gopls SHALL be launched with the configuration from `go-microservices/.omp/lsp.json`
### Requirement: cwd-only root marker detection
OMP LSP config resolution SHALL be cwd-only. Root markers (e.g. `go.mod`, `go.work`) MUST exist in the agent's working directory for gopls to activate. Project-level `.omp/lsp.json` SHALL be loaded only when the agent launches from within the project directory.

#### Scenario: gopls activates from project dir
- **WHEN** the agent launches from `~/Developer/go-microservices/`
- **THEN** `go.mod` exists in cwd
- **AND** gopls SHALL be available with staticcheck, gofumpt, and integration build flags

#### Scenario: gopls filtered from workspace root
- **WHEN** the agent launches from `~/Developer/` (no `go.mod` in cwd)
- **THEN** gopls SHALL be filtered out by rootMarker detection
- **AND** the `lsp` tool SHALL report no Go servers configured
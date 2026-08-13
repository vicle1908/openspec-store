## Why

OMP ships with 14 LSP actions, 40+ built-in server configs, and auto-detection — but the current configuration has zero LSP customization. No `lsp.json` exists at user level or project level. Running on defaults means `diagnosticsOnEdit` is false (no real-time feedback), `formatOnWrite` is false (no auto-formatting), and no server-specific settings exist for Go (`gopls`) or Python (`pyright`/`basedpyright`).

## What Changes

1. Create `~/.omp/agent/lsp.json` with user-level LSP settings (global `diagnosticsOnEdit: true`, `formatOnWrite: true`).
2. Add Go-specific `gopls` settings: staticcheck enabled, gofumpt formatting, analyses tuning.
3. Add Python-specific `pyright`/`basedpyright` settings: type checking mode, python version, import formatting.
4. Create `go-microservices/.omp/lsp.json` with Go project overrides (gopls workspace settings, build tags, test mode).
5. Create `agent-core/.omp/lsp.json` with Python project overrides (venv path, import source).
6. Create `tdt-core/.omp/lsp.json` with Python project overrides (venv path, import source).
7. Add `lsp.diagnosticsOnEdit` and `lsp.formatOnWrite` to `~/.omp/agent/config.yml`.

## Capabilities

### New Capabilities

- `omp-config/lsp-user`: User-level LSP configuration (`~/.omp/agent/lsp.json`) — global diagnostics and formatting defaults.
- `omp-config/lsp-go`: Go project LSP settings — `gopls` analysis, formatting, and workspace configuration for `go-microservices`.
- `omp-config/lsp-python`: Python project LSP settings — `pyright`/`basedpyright` type checking and import resolution for `agent-core` and `tdt-core`.

## Ownership

- **Owner**: User (OMP config is personal workspace configuration).
- **Affected files**:
  - `~/.omp/agent/lsp.json` (user-level LSP defaults)
  - `~/.omp/agent/config.yml` (diagnosticsOnEdit, formatOnWrite flags)
  - `~/Developer/go-microservices/.omp/lsp.json` (Go project overrides)
  - `~/Developer/agent-core/.omp/lsp.json` (Python project overrides)
  - `~/Developer/tdt-core/.omp/lsp.json` (Python project overrides)

## Non-Goals

- Configuring LSP for TypeScript, Swift, or Kotlin (future work).
- Modifying OMP source code.
- Adding new language servers not in the built-in 40+ list.
- Changing model role assignments.
- Modifying `models.yml`, provider credentials, or the adapter infrastructure.
- Updating `CLAUDE.md`, skills, or memory configuration.

# Proposal: Organize Workspace by First-Class Organization Namespaces

## Why

The developer workspace at `~/Developer/` and specifications in `openspec-store` contain projects, client configurations, and archives from multiple distinct organizations (`tdt`, `vds`, `ascend`, `ghtk`, `fpt`, and shared platform engineering). Mixing repositories flatly at the workspace root or relying on ad-hoc functional categorization (`apps/`, `legacy/`) obscures enterprise ownership boundaries, introduces cross-tenant collision risks, and complicates access governance. Establishing **first-class organization namespaces** directly at `~/Developer/` creates a uniform, two-tier hierarchy: `~/Developer/<organization>/<repository>/<files-and-folders>` without intermediate wrapper directories.

## What Changes

1. **First-Class Organization Hierarchy (Flat Repositories per Organization)**:
   Every organization namespace houses its project codebases directly and flatly within its organization folder:
   ```
   ~/Developer/
   ├── <organization-namespace>/
   │   ├── <repository-1>/
   │   └── <repository-2>/
   ```
2. **Explicit Organization Taxonomies & Repositories Placement**:
   - `platform/`: Universal engineering platform & shared tooling:
     - `claude-code-provider-adapter` (Anthropic->OpenAI provider adapter)
     - `go-microservices` (Greenfield Go monorepo)
     - `qi-bridge` (Go Qi proxy)
     - `mcp-router` (Node.js/pnpm MCP hub)
     - `openspec-store` (Shared OpenSpec store)
     - `prime-agent`, `hermes-webui`, `goose-docs`
   - `tdt/`: Technology Development Team & Phillip Securities platform:
     - Mobile clients: `poems-mobile3-android`, `poems-mobile3-ios`, `poems-mobile3-docs`
     - Python Core Agent Services (18 repositories): `agent-core`, `tdt-core`, `tdt-observability`, `tdt-scheduler`, `tdt-sheets`, `agent-docs-sync`, `agent-harness`, `ai-harness-skills`, `ai-review`, `jira-skill`, `jira-daily-reports`, `jira-epic-report`, `jira-kanban-from-spreadsheet`, `webhook-receiver`, `ops-automation-suite`, `browser-cli`, `code-daily-scan`, `realtime`
     - Operations & setup tooling: `tdt-tools`, `bootstrap-nexus`
   - `vds/`: Viettel Digital Services:
     - Standalone automation tool: `viettel-excel-updater`
     - Component service repositories: `DOPS-project`, `EKYC-project`, `INSURANCE-project`, `LEP-project`, `LIB-project`, `PAR-project`, `SAVING-project`, `WHO-project`
   - `ascend/`: Ascend Money / TrueMoney:
     - `ascend-configs` (regional device and proxy configurations)
     - `tmz-case-challenge` (TrueMoney deliverable models and slide decks)
   - `ghtk/`: Giao Hàng Tiết Kiệm:
     - 6 checkouts: `ghtk-android-drawables`, `ghtk-catalog-v2`, `ghtk-detekt`, `ghtk-project-assets`, `ghtk-scripts`, `ghtk-training-cicd`
   - `fpt/`: FPT Information System:
     - `fpt-ingenico` (payment integration rules, detekt configurations, diagrams)
   - `shared/` (or Workspace Meta-Roots): Universal workspace assets:
     - `data/`, `scripts/`, `wiki/`, `docs/`, `sensitive-quarantine/`
3. **OpenSpec Store Alignment**: Scoping capability specifications by organization prefixes (`specs/tdt/<capability>`, `specs/platform/<capability>`, `specs/vds/<capability>`).
4. **Credential Quarantine Mirroring**: Enforce tenant segregation in `sensitive-quarantine/<org>/` (`ascend/`, `vds/`, `tdt/`, `platform/`).
5. **Path & Pipeline Invariant Preservation**: Provide compatibility layer or update configuration bindings for `rclone bisync` (`~/.config/rclone/tdt-filters.txt`), GitNexus indexes (`scripts/knowledge-refresh/knowledge-refresh-inventory.tsv`), and active LaunchAgents.

## Capabilities

### New Capabilities
- `organization-namespaces`: Enforces organization namespaces as first-class citizens directly under `~/Developer/`, mandates the flat `<organization>/<repository>/` layout, and specifies multi-tenant isolation rules.

### Modified Capabilities
(none)

## Impact

- **Affected Systems**: Workspace root filesystem hierarchy, `AGENTS.md`, `CLAUDE.md`, `docs/WORKSPACE_TOPOLOGY.md`.
- **Pipeline Integrity**:
  - `rclone bisync` paths for TDT Python checkouts are explicitly migrated to `tdt/<repo>` or preserved via root symlinks.
  - `scripts/knowledge-refresh/knowledge-refresh-inventory.tsv` is updated to reflect new repository paths.
- **Tenant Isolation**: Clean segregation prevents cross-organizational secret leakage and eliminates naming collisions across independent organizations.

# Technical Design: Organize Workspace by First-Class Organization Namespaces

## Context

The `~/Developer/` workspace has evolved across multiple client engagements and platforms, encompassing repositories and historical assets from `tdt`, `vds`, `ascend`, `ghtk`, `fpt`, and cross-cutting platform infrastructure. Prior domain clustering separated code by lifecycle status, but left enterprise ownership boundaries implicit and fragmented.

This design elevates **organization namespaces to first-class citizens** at the root of `~/Developer/`, establishing a flat two-tier hierarchy across all organizations:
```
~/Developer/
├── <organization-namespace>/
│   ├── <repository-1>/
│   └── <repository-2>/
```
Repositories sit directly and flatly within their organization directory without intermediate wrapper folders.

## Goals / Non-Goals

**Goals:**
- Enforce first-class organization directories directly under `~/Developer/`: `platform/`, `tdt/`, `vds/`, `ascend/`, `ghtk/`, `fpt/`.
- Maintain a flat two-tier hierarchy: every repository resides directly inside its owning organization folder (`<organization>/<repository>/`).
- Place `claude-code-provider-adapter` under `platform/`.
- Ensure mobile client repositories (`poems-mobile3-android`, `poems-mobile3-ios`, `poems-mobile3-docs`), all 18 Python services, and ops-tools reside directly under `tdt/`.
- Place VDS projects and tools flatly inside `vds/` (`viettel-excel-updater`, `EKYC-project`, `SAVING-project`, `INSURANCE-project`, `LEP-project`, `PAR-project`, `WHO-project`, `LIB-project`, `DOPS-project`).
- Place Ascend, GHTK, and FPT assets flatly inside their respective organization folders (`ascend/`, `ghtk/`, `fpt/`).
- Provide compatibility bridges (or atomic updates) for automated pipelines: `rclone bisync` (`~/.config/rclone/tdt-filters.txt`), GitNexus 20-repo index inventory (`scripts/knowledge-refresh/knowledge-refresh-inventory.tsv`), and LaunchAgents.
- Mirror organization namespaces within `sensitive-quarantine/<org>/` to guarantee strict multi-tenant credential isolation.

**Non-Goals:**
- Altering internal Git commit histories or branch states of any repository.
- Introducing redundant intermediate folders (e.g. `repositories/`).
- Mutating remote cloud storage targets without verification.

## Decisions

### Decision 1: Direct Two-Tier Organization Hierarchy (Flat per Org)
- **Choice**:
  Every repository in `~/Developer/` must reside directly under its respective `<organization>/` folder:
  1. `platform/`: Universal engineering platform & shared tooling:
     - `claude-code-provider-adapter` (Anthropic->OpenAI provider adapter)
     - `go-microservices` (Greenfield Go monorepo)
     - `qi-bridge` (Go Qi proxy)
     - `mcp-router` (Node.js/pnpm MCP transport hub)
     - `openspec-store` (Shared OpenSpec store)
     - `prime-agent`, `hermes-webui`, `goose-docs`
  2. `tdt/`: Technology Development Team & Phillip Securities platform:
     - Mobile clients: `poems-mobile3-android`, `poems-mobile3-ios`, `poems-mobile3-docs`
     - 18 Python core services: `agent-core`, `tdt-core`, `tdt-observability`, `tdt-scheduler`, `tdt-sheets`, `agent-docs-sync`, `agent-harness`, `ai-harness-skills`, `ai-review`, `jira-skill`, `jira-daily-reports`, `jira-epic-report`, `jira-kanban-from-spreadsheet`, `webhook-receiver`, `ops-automation-suite`, `browser-cli`, `code-daily-scan`, `realtime`
     - Operations & setup tooling: `tdt-tools`, `bootstrap-nexus`
  3. `vds/`: Viettel Digital Services:
     - `viettel-excel-updater` (standalone automation tool)
     - Projects: `DOPS-project`, `EKYC-project`, `INSURANCE-project`, `LEP-project`, `LIB-project`, `PAR-project`, `SAVING-project`, `WHO-project`
  4. `ascend/`: Ascend Money / TrueMoney:
     - `ascend-configs` (regional device and Charles proxy configurations)
     - `tmz-case-challenge` (TrueMoney deliverable models and slide decks)
  5. `ghtk/`: Giao Hàng Tiết Kiệm:
     - 6 repositories: `ghtk-android-drawables`, `ghtk-catalog-v2`, `ghtk-detekt`, `ghtk-project-assets`, `ghtk-scripts`, `ghtk-training-cicd`
  6. `fpt/`: FPT Information System:
     - `fpt-ingenico` (payment integration rules, detekt configurations, diagrams)
  7. `shared/` (or Workspace Meta-Roots):
     - `data/`, `scripts/`, `wiki/`, `docs/`, `sensitive-quarantine/`
- **Rationale**: Direct `<organization>/<repository>/` nesting keeps path depths shallow, eliminates redundant path segments, ensures clean tab-completion, and establishes clear enterprise boundaries.

### Decision 2: Pipeline Path Compatibility & Migration Strategy
- **Choice**:
  For active daemons referencing paths (`rclone bisync`, GitNexus, LaunchAgents):
  - Update `scripts/knowledge-refresh/knowledge-refresh-inventory.tsv` to point to `/Users/androidteam/Developer/platform/<repo>` and `/Users/androidteam/Developer/tdt/<repo>`.
  - Update `~/.config/rclone/tdt-filters.txt` or configure symlinks from `~/Developer/<repo>` $\rightarrow$ `~/Developer/tdt/<repo>` during transition to ensure zero downtime.
- **Rationale**: Guarantees zero disruption to background sync jobs or knowledge index generation while the directory restructuring lands.

### Decision 3: OpenSpec Store Multi-Tenant Alignment
- **Choice**:
  - Main specs in `openspec-store/openspec/specs/` align to organization prefixes:
    `tdt/*` (e.g. `tdt-core`, `tdt-observability`, `agent-*`, `poems-mobile3-*`)
    `platform/*` (e.g. `platform-architecture`, `claude-code-provider-adapter`, `order-service`, `k8s-*`)
    `vds/*`, `ascend/*`, `ghtk/*`
- **Rationale**: Enforces single-organization ownership of specifications and prevents naming collisions across client architectures.

## Risks / Trade-offs

- **[Risk] Broken relative path bindings in local tools** → *Mitigation:* Conduct automated grep audits of shell configs (`~/.zshrc`), LaunchAgents, and inventory files; provide transitional symlinks where needed.
- **[Risk] Git tracking detachment during directory moves** → *Mitigation:* Use atomic filesystem moves (`mv`) or `git mv` so embedded `.git` metadata trees remain fully intact.
- **[Risk] GitNexus index invalidation** → *Mitigation:* Simultaneously update `scripts/knowledge-refresh/knowledge-refresh-inventory.tsv` and trigger index validation.

## Migration Plan

1. **Phase 1: Inventory & Pre-flight Snapshot**: Catalog all repository paths and create pre-migration layout snapshot.
2. **Phase 2: Organization Namespace Scaffolding**: Create first-class root directories (`platform/`, `tdt/`, `vds/`, `ascend/`, `ghtk/`, `fpt/`).
3. **Phase 3: Client Organization Relocations**:
   - Move GHTK checkouts $\rightarrow$ `ghtk/`
   - Move VDS repositories & tools $\rightarrow$ `vds/`
   - Move Ascend configs & challenge assets $\rightarrow$ `ascend/`
   - Move FPT assets $\rightarrow$ `fpt/`
4. **Phase 4: Platform & TDT Ecosystem Migration**:
   - Move platform repositories and `claude-code-provider-adapter` $\rightarrow$ `platform/`
   - Move TDT services, mobile clients (`poems-mobile3-*`), and ops-tools $\rightarrow$ `tdt/`
   - Create root backwards-compatible symlinks or update configuration bindings.
5. **Phase 5: Pipeline & Config Updates**:
   - Update `scripts/knowledge-refresh/knowledge-refresh-inventory.tsv`.
   - Update `~/.config/rclone/tdt-filters.txt`.
   - Update `docs/WORKSPACE_TOPOLOGY.md`, `AGENTS.md`, and `CLAUDE.md`.
6. **Phase 6: Post-Migration Verification**:
   - Run `knowledge-status.sh --json` and test builds (`go vet`, `pytest`).

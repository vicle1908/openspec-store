# Tasks: Organize Workspace by First-Class Organization Namespaces

## 1. Multi-Tenant Inventory and Safety Audit

- [x] 1.1 Audit all assets across `~/Developer/` and `openspec-store` matching organization tokens (`tdt`, `vds`, `ascend`, `ghtk`, `fpt`, `platform`) and record inventory in `evidence/organization-inventory.json`.
- [x] 1.2 Verify active dependencies and pipeline path bindings (`~/.config/rclone/tdt-filters.txt`, `scripts/knowledge-refresh/knowledge-refresh-inventory.tsv`, LaunchAgents) to prepare path mapping and transitional symlinks.

## 2. First-Class Organization Scaffolding

- [x] 2.1 Create first-class organization root directories (`platform/`, `tdt/`, `vds/`, `ascend/`, `ghtk/`, `fpt/`) under `~/Developer/` and verify directory creation with `test -d`.

## 3. Staged Repository Relocations (Flat per Org)

- [x] 3.1 Relocate GHTK repositories (6 repos) into `ghtk/<repo>/` and verify presence with `ls ghtk`.
- [x] 3.2 Relocate VDS assets (`viettel-excel-updater` and projects from `vds-content-migration`) into `vds/<repo>/` and verify presence with `ls vds`.
- [x] 3.3 Relocate Ascend configurations and deliverables (`ascend-configs` and `tmz-case-challenge`) into `ascend/<repo>/` and verify presence with `ls ascend`.
- [x] 3.4 Relocate FPT integration assets (`fpt-ingenico`) into `fpt/<repo>/` and verify presence with `ls fpt`.
- [x] 3.5 Relocate platform repositories including `claude-code-provider-adapter`, `go-microservices`, `qi-bridge`, `mcp-router`, `openspec-store`, `prime-agent`, `hermes-webui`, and `goose-docs` into `platform/<repo>/` and verify presence with `ls platform`.
- [x] 3.6 Relocate TDT ecosystem repositories (POEMS mobile clients `poems-mobile3-android`, `poems-mobile3-ios`, `poems-mobile3-docs`, 18 Python repos, `tdt-tools`, `bootstrap-nexus`) into `tdt/<repo>/` and verify presence with `ls tdt`.

## 4. Pipeline Configuration and Transitional Compatibility

- [x] 4.1 Create root backwards-compatibility symlinks (`~/Developer/<repo>` $\rightarrow$ `~/Developer/<org>/<repo>`) or update active bindings to prevent disruption to background tooling.
- [x] 4.2 Update `scripts/knowledge-refresh/knowledge-refresh-inventory.tsv` with new repository paths (`platform/<repo>` and `tdt/<repo>`) and verify with `knowledge-status.sh --json`.
- [x] 4.3 Update `~/.config/rclone/tdt-filters.txt` to reflect the `tdt/` prefix for all 18 Python services and verify filter matching.

## 5. Credential Quarantine Organization Mirroring

- [x] 5.1 Ensure `~/Developer/sensitive-quarantine/` subdirectories strictly mirror organization namespaces (`sensitive-quarantine/ascend/`, `sensitive-quarantine/vds/`, `sensitive-quarantine/tdt/`, `sensitive-quarantine/platform/`) with mode `0700` directories and `0600` secret files.

## 6. Workspace Documentation and Verification

- [x] 6.1 Update `docs/WORKSPACE_TOPOLOGY.md`, `AGENTS.md`, and `CLAUDE.md` to document the first-class organization flat hierarchy (`<organization>/<repo>`).
- [x] 6.2 Run smoke tests across active services (`go vet ./...` in `platform/qi-bridge`, `pytest` in `tdt/agent-core`) to verify build readiness.
- [x] 6.3 Run `openspec validate organize-workspace-by-organization-namespaces --strict --store openspec-store` and verify 100% strict compliance.

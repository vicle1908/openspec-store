# Spec Delta: organization-namespaces

## ADDED Requirements

### Requirement: Workspace meta-roots placement
The developer workspace at `~/Developer/` SHALL maintain universal operational meta-roots (`docs/`, `scripts/`, `wiki/`, `data/`, `sensitive-quarantine/`) and auxiliary domain roots (`apps/`, `ai-tooling/`, `study/`, `migration-archives/`, `legacy/`) directly at the workspace root, and SHALL NOT encapsulate them inside an intermediate `shared/` directory.

#### Scenario: Discovering workspace meta-roots
- **WHEN** developer tooling, scripts, or agents inspect the workspace root `~/Developer/`
- **THEN** `docs/`, `scripts/`, `wiki/`, `data/`, and `sensitive-quarantine/` SHALL resolve directly under `~/Developer/`
- **AND** no intermediate `~/Developer/shared/` path SHALL be required or assumed

#### Scenario: Validating auxiliary domain directories
- **WHEN** auxiliary projects such as standalone apps, study materials, or migration archives are created or referenced
- **THEN** they SHALL reside in their respective top-level domain roots (`apps/`, `study/`, `migration-archives/`, `ai-tooling/`, `legacy/`)
- **AND** they SHALL NOT mix unclassified into organization namespaces (`tdt/`, `vds/`, `platform/`)

### Requirement: Tooling and script path resolution invariants
Automated workspace maintenance scripts, LaunchAgents, and knowledge synchronization pipelines SHALL resolve repository paths dynamically or reference canonical two-tier organization paths (`~/Developer/<organization>/<repository>`), and SHALL NOT depend on deprecated flat workspace paths.

#### Scenario: Discovering OpenSpec specifications for knowledge cataloging
- **WHEN** `sync-notion-knowledge.sh` or automated catalog generators scan for governed capability specifications
- **THEN** the script SHALL resolve `openspec-store` at its canonical location `~/Developer/platform/openspec-store`
- **AND** all active capability specifications under `openspec/specs/**/spec.md` SHALL be discovered and cataloged without returning an empty set

#### Scenario: Handling missing or moved repository targets
- **WHEN** a script encounters an inventory path that does not exist at the historical flat root
- **THEN** the script SHALL fail closed with an explicit descriptive error indicating the missing canonical path
- **AND** it SHALL NOT emit a false-positive success or silent zero-count output

#### Scenario: Validating approved knowledge refresh inventory digest
- **WHEN** `refresh-knowledge-indexes.sh` verifies inventory integrity against the approval digest
- **THEN** `knowledge-refresh-inventory.tsv` and `knowledge-refresh-approval.sha256` SHALL match with identical canonical 20-repo paths and valid SHA-256 approval digests across both `~/Developer/scripts/knowledge-refresh/` and `platform/openspec-store/scripts/knowledge-refresh/`
- **AND** `refresh-knowledge-indexes.sh --check` SHALL exit successfully with return code 0

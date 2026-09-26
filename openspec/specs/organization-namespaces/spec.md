# organization-namespaces Specification

## Purpose
Defines the first-class organization namespace hierarchy, repository placement rules, multi-tenant boundaries, and naming standards across the developer workspace and OpenSpec store.

## Requirements

### Requirement: First-class organization namespace hierarchy
The developer workspace at `~/Developer/` SHALL establish organization namespaces (`tdt`, `vds`, `ascend`, `ghtk`, `fpt`, `platform`) as direct first-class children of the workspace root, and all project repositories SHALL reside directly and flatly within their corresponding organization directory using the two-tier structure `~/Developer/<organization>/<repository>/` without intermediate `repositories/` subfolders.

#### Scenario: Enforcing two-tier organization hierarchy
- **WHEN** repositories or projects are organized or instantiated in the workspace
- **THEN** they SHALL reside directly inside their designated first-class organization namespace folder (`tdt/`, `vds/`, `ascend/`, `ghtk/`, `fpt/`, or `platform/`)
- **AND** project repositories SHALL NOT sit under an intermediate `repositories/` subfolder or unclassified at `~/Developer/`

### Requirement: Repository placement within organization namespaces
Every repository SHALL belong to exactly one first-class organizational namespace based on enterprise ownership and operational boundary.

#### Scenario: Categorizing repositories by organization
- **WHEN** repositories are mapped to organization namespaces
- **THEN** POEMS mobile clients (`poems-mobile3-android`, `poems-mobile3-ios`, `poems-mobile3-docs`), all 18 Python services, and ops-tools SHALL reside directly under `tdt/`
- **AND** `claude-code-provider-adapter`, `go-microservices`, `qi-bridge`, `mcp-router`, `openspec-store`, `prime-agent`, `hermes-webui`, and `goose-docs` SHALL reside directly under `platform/`
- **AND** VDS service repositories and utilities SHALL reside directly under `vds/`
- **AND** Ascend configurations and deliverables SHALL reside directly under `ascend/`
- **AND** GHTK repositories SHALL reside directly under `ghtk/`
- **AND** FPT integrations SHALL reside directly under `fpt/`

### Requirement: OpenSpec capability organization prefixing
New capabilities introduced into `openspec-store` that are specific to a single organization SHALL carry an explicit organization namespace segment (`specs/<org>/<capability>/spec.md` or `specs/<org>-<capability>/spec.md`), while shared platform capabilities SHALL carry `platform/` or `platform-*`.

#### Scenario: Scoping new OpenSpec capabilities
- **WHEN** a new capability specification is registered in `openspec-store`
- **THEN** it SHALL declare its owning organizational namespace
- **AND** capabilities specific to TDT SHALL use `tdt-*` or `tdt/*`
- **AND** capabilities specific to core platform infrastructure SHALL use `platform-*` or `platform/*`

### Requirement: Credential quarantine organizational mirroring
Sensitive credentials and certificates quarantined under `~/Developer/sensitive-quarantine/` SHALL mirror the first-class organizational taxonomy and enforce restricted file permissions.

#### Scenario: Storing quarantined credentials by organization
- **WHEN** private credentials or TLS certificates are discovered and quarantined
- **THEN** they SHALL be stored in an organization-specific subdirectory (`sensitive-quarantine/<org>/`)
- **AND** directories SHALL be restricted to mode `0700` and secret files to mode `0600`

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

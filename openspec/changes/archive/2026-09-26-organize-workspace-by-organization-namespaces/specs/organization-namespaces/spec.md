## Purpose

Defines the first-class organization namespace hierarchy, repository placement rules, multi-tenant boundaries, and naming standards across the developer workspace and OpenSpec store.

## ADDED Requirements

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

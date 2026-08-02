# operational-runbooks Specification

## Purpose

Establishes a runbook directory and template for per-service operational procedures, enabling operators to quickly diagnose and recover from common failure modes.

## Requirements

> **Status**: PARTIAL. docs/runbooks/README.md with template exists; per-service runbooks and discoverable index are partial.

### Requirement: Runbook directory and template exist

> **Status**: IMPLEMENTED. docs/runbooks/README.md exists with standardized template sections.

The project SHALL provide `docs/runbooks/README.md` containing a runbook template with standardized sections: Service Overview, Health Checks, Common Failure Modes, Rollback Procedure, Escalation Contacts, and Related Specs.

#### Scenario: New service runbook follows template
- **WHEN** an operator creates a new runbook at `docs/runbooks/<service-name>.md`
- **THEN** the runbook includes all sections defined in the template from `README.md`

### Requirement: README.md documents runbook conventions

> **Status**: IMPLEMENTED. README.md documents format, naming conventions, and contribution process.

The `docs/runbooks/README.md` SHALL document the expected format, naming conventions, and contribution process for new runbooks.

#### Scenario: Developer reads runbook conventions
- **WHEN** a developer reads `docs/runbooks/README.md`
- **THEN** they can understand the naming convention, required sections, and how to add a new service runbook

### Requirement: Runbooks are discoverable

> **Status**: PARTIAL. The root index and shared local CDC runbook exist; root per-service runbook coverage remains incomplete.

The `docs/runbooks/README.md` SHALL include an index that distinguishes root
per-service runbooks, shared platform procedures, and links to service-local
runbooks where those are the current owner documentation. Each entry SHALL
identify the service or procedure, its canonical path, and whether it is
implemented, shared, service-local, or planned.

#### Scenario: Operator finds available runbooks
- **WHEN** an operator navigates to `docs/runbooks/`
- **THEN** the README lists every available root or shared runbook with a valid link and lists all eight services with an explicit status

#### Scenario: Service-local runbook is not misclassified
- **WHEN** a service has an operational document under `services/<service>/docs/`
- **THEN** the root index links to that path as service-local guidance rather than claiming a root `docs/runbooks/<service>.md` exists

#### Scenario: Missing runbook remains visible
- **WHEN** a service has no complete operational runbook
- **THEN** the index marks it planned or partial and does not represent the platform as having complete runbook coverage

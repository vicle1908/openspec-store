# Spec Delta

## MODIFIED Requirements

### Requirement: Independent Multi-Repository Directory Structure

The `shb` organization SHALL reside at `~/Developer/shb/` as an organizational directory where each child repository is an independent Git repository possessing its own `.git` directory, version control history, and lifecycle, officially incorporating `shb-schedule` as the 13th ecosystem repository alongside the existing 12 SHB repositories.

#### Scenario: Repository isolation verification
- **WHEN** Git status is checked within any repository under `~/Developer/shb/`
- **THEN** the repository operates as an independent Git work tree without treating neighboring repositories as submodules or parent directories

#### Scenario: Ecosystem inventory includes scheduler repository
- **WHEN** the SHB repository catalog or multi-repo inventory is resolved
- **THEN** `shb-schedule` SHALL be recognized as a first-class repository located at `~/Developer/shb/shb-schedule/`
- **AND** the existing 12 repositories SHALL remain independently addressable workload targets

## ADDED Requirements

### Requirement: Standardized Durable Scheduling

The SHB ecosystem SHALL use `shb-schedule` as the sole official recurring execution engine. Recurring jobs SHALL be declared as `shb-schedule/v1` manifests and SHALL execute through the canonical scheduler ownership boundary. SHB workloads SHALL remain implemented in SHB-owned repositories and SHALL NOT import TDT scheduler or TDT documentation-sync packages.

#### Scenario: Scheduled job execution via shb-schedule
- **WHEN** a recurring ecosystem task such as documentation synchronization, compliance scanning, or settlement reconciliation is configured
- **THEN** it SHALL be declared as a YAML manifest in `~/.shb/schedules/` conforming to `shb-schedule/v1`
- **AND** it SHALL execute through the active `shb-schedule` owner
- **AND** it SHALL use an SHB-native workload boundary

#### Scenario: TDT isolation verification
- **WHEN** the scheduler package and flagship workload dependencies are inspected
- **THEN** no runtime import or filesystem dependency on `tdt-core`, `tdt-scheduler`, `~/Developer/tdt/`, or `~/.tdt/` SHALL exist

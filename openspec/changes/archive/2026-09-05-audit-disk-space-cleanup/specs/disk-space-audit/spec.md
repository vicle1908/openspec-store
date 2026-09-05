## Purpose

Provide a filesystem-aware, read-only inventory that distinguishes reclaimable artifacts from user data and managed application state.

## ADDED Requirements

### Requirement: Read-only filesystem inventory
The audit SHALL report filesystem/device boundaries and SHALL exclude nonstandard, network, and FUSE mounts from the primary filesystem totals.

#### Scenario: Separate mount is present
- **WHEN** a path such as a Nicegram wrapper is mounted separately
- **THEN** the audit reports its filesystem independently and does not combine its capacity with the primary data volume.

### Requirement: Evidence-based candidate ranking
The audit SHALL report candidate paths with measured allocated size, modification date when available, and a risk classification without treating free capacity as reclaimable data.

#### Scenario: Large old regular file exists
- **WHEN** a bounded per-root scan finds a regular file at least 1 GiB old by the selected age threshold
- **THEN** the audit reports only its path, size, date, and classification.

### Requirement: Managed storage handling
The audit SHALL identify Docker VM files, Docker-native reclaimable resources, synced data, personal libraries, and application state separately.

#### Scenario: Docker VM is present
- **WHEN** Docker reports a VM disk and app-native reclaimable images or volumes
- **THEN** the audit excludes the VM disk itself from deletion candidates and reports only Docker-native reclaimable resources.

### Requirement: Privacy-preserving output
The audit SHALL avoid printing file contents, credentials, tokens, or raw database records.

#### Scenario: Credential-bearing path is encountered
- **WHEN** an inventory path appears to contain credentials or secrets
- **THEN** the audit reports only a redacted classification and does not disclose its contents.

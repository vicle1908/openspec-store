# local-user-asset-quarantine-and-hygiene Specification

## Purpose
Defines safety policies, credential quarantine requirements, document classification rules, and installer hygiene for managing and securing assets across macOS user directories (`~/Downloads`, `~/Documents`, `~/Desktop`).

## Requirements

### Requirement: Immediate quarantine isolation of sensitive credentials and keys

The system SHALL identify unencrypted private keys, public keys, and account recovery codes in local user directories, relocate them into the local sensitive quarantine area, enforce strict filesystem permissions (`0700` directories, `0600` files), and purge the source files from user directories.

#### Scenario: Private SSH keys and credentials in Downloads are quarantined
- **WHEN** private keys (`id_rsa*`) or recovery codes (`Backup-codes-*.txt`) are discovered in `~/Downloads`
- **THEN** they SHALL be copied to `~/Developer/sensitive-quarantine/downloads/`
- **AND** containing directories SHALL be set to mode `0700` and files to mode `0600`
- **AND** the source items SHALL be unlinked only after confirming the destination files are intact.

### Requirement: Consolidation of personal identity and financial documentation

The system SHALL consolidate loose personal identification scans, diplomas, payslips, and financial records from local user directories into the canonical 4-pillar iCloud taxonomy.

#### Scenario: Identity scans and degrees are relocated to the identity domain
- **WHEN** passport scans (`PassPortVinh.jpg`), national ID scans (`VinhCCCD_front.png`, `VinhIC*.jpg`), or graduation degree certificates (`NTUcertificate.jpg`, `NangyangTechnological.jpg`) are detected in `~/Downloads` or `~/Documents`
- **THEN** they SHALL be moved to `iCloud/2_Personal/Identity_and_Docs/identity/` preserving file metadata and sizes.

#### Scenario: Payslips and bank statements are relocated to the finance domain
- **WHEN** payslips (`Payslip*.pdf`) or bank account statements (`bankStatement.pdf`, `BIÊN LAI CHUYỂN TIỀN.pdf`) are detected in `~/Documents`
- **THEN** they SHALL be moved to `iCloud/2_Personal/Finance/salary/` without data loss.

### Requirement: Purge of disposable installers and packages

The system SHALL identify obsolete application disk images (`.dmg`) and historical archive snapshots in local user directories, verify that they are disposable or superseded, and remove them to reclaim disk storage.

#### Scenario: Obsolete application DMGs in Downloads are purged
- **WHEN** downloaded installer disk images matching `*.dmg` are identified in `~/Downloads`
- **THEN** the system SHALL record their sizes and paths in a purge manifest and safely unlink the files.

#### Scenario: Obsolete trial installation archives in Documents are purged
- **WHEN** trial installation zips (such as `MCP.Router-darwin-arm64-0.6.3.zip`) are encountered in historical trial paths
- **THEN** the system SHALL unlink the archive and prune empty parent directories bottom-up.

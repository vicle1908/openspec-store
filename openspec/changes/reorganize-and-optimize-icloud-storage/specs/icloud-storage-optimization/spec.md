## Purpose

Defines safety policies, classification rules, deduplication gates, and taxonomy consolidation criteria for optimizing non-code assets and storage structures in iCloud Drive.

## ADDED Requirements

### Requirement: Purge of disposable compiled mobile binaries and installer packages

The optimization pipeline SHALL locate and safely unlink obsolete compiled mobile application packages (`.apk`) and enterprise installer packages (`.pkg`) while verifying that source projects and configuration files have already been migrated or preserved.

#### Scenario: Legacy Android APK builds are safely removed
- **WHEN** the optimization scanner identifies compiled `.apk` files under `ascend/MM/MMApp/apk/`, `ascend/automation/testlab/app-crawler/`, and `Downloads/`
- **THEN** it records their file paths and sizes in a disposal manifest
- **AND** unlinks the `.apk` files without touching non-binary documentation or source scripts.

#### Scenario: Enterprise installer packages are removed
- **WHEN** the optimization scanner encounters installer packages matching `*.pkg` (such as `ghtk/ztrust/ZTrust-1.2.3-arm64.pkg`)
- **THEN** it verifies the file is an installer binary and unlinks it to reclaim storage.

### Requirement: Deduplication of redundant archive copies

The optimization pipeline SHALL identify redundant download archives and duplicate directory structures, verify that canonical uncompressed reading files or identical canonical copies exist, and purge only the redundant instances.

#### Scenario: Redundant book archive is removed when standalone assets exist
- **WHEN** evaluating `books/microservices/spring/Learning Spring Boot 4.rar`
- **THEN** the pipeline verifies that `Learning Spring Boot 4.epub` and `Learning Spring Boot 4.pdf` both exist with size > 50 MB
- **AND** only then unlinks the `.rar` archive file.

#### Scenario: Duplicate documentation directory trees are deduplicated
- **WHEN** evaluating duplicate folder pairs (such as `viettel/NTTC/Baohiem/vietin/Tai lieu BHDT_09182020-1/` versus `Tai lieu BHDT_09182020/`)
- **THEN** the pipeline compares SHA-256 checksums or size-and-stem parity for all child files
- **AND** upon asserting 100% identity, unlinks the duplicate directory tree.

### Requirement: Personal identity and financial document consolidation

The optimization pipeline SHALL consolidate scattered personal identification scans (CCCD, university degrees) and income spreadsheets into dedicated, organized personal domains.

#### Scenario: Dispersed CCCD and university degree scans are unified
- **WHEN** scanning personal identity documents dispersed across `doc/info/` and `SHB/info/`
- **THEN** it unifies canonical copies into `doc/identity/` (later `2_Personal/Identity/`)
- **AND** removes redundant duplicate copies after asserting identical content hashes.

#### Scenario: Salary income spreadsheets are moved to financial records
- **WHEN** discovering loose monthly income spreadsheets matching `Bang_thu_nhap*.xlsx` in `Downloads/`
- **THEN** it moves them to the consolidated personal finance domain without data loss.

### Requirement: Four-pillar root taxonomy reorganization

The optimization pipeline SHALL reorganize the loose root directories into a structured 4-pillar taxonomy (`1_Career/`, `2_Personal/`, `3_Library/`, `4_Archive/`) via atomic local moves and SHALL prune empty legacy directories bottom-up.

#### Scenario: Career workspace directories are grouped
- **WHEN** reorganizing employer folders (`Viettel`, `GHTK`, `Ascend`, `SHB`, `TimeCompany`)
- **THEN** they are moved under `1_Career/` preserving all internal folder hierarchies and timestamps.

#### Scenario: Personal records and media are unified
- **WHEN** reorganizing personal folders (`doc`, `family`, `loan`, `thue`, `binance`, `pic`, `fcfc`, `memory`, `s101`, `che`)
- **THEN** they are grouped under `2_Personal/` categorized into `Identity/`, `Family/`, `Finance/`, and `Media/`.

#### Scenario: Empty legacy directories are pruned bottom-up
- **WHEN** all files have been migrated or purged from a source root directory
- **THEN** the pipeline prunes all empty parent and child directories bottom-up without leaving orphaned paths.

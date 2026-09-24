# Proposal: Reorganize and Optimize iCloud Drive Storage & Taxonomy

## Why

Following the completion of the code, git repositories, and developer credentials migration to `~/Developer` (archived under `2026-09-22-migrate-and-purge-all-icloud-code` and `2026-09-24-migrate-residual-icloud-developer-assets`), iCloud Drive (`com~apple~CloudDocs`) now holds 1,356 non-code files totaling 5.32 GB.

A comprehensive audit of the remaining volume identified substantial optimization opportunities:
1. **Disposable Mobile Binaries & Installer Packages (~1.23 GB):** 51 obsolete compiled Android `.apk` builds from 2020–2021 (`ascend/MM/MMApp/apk/` and `ascend/automation/testlab/app-crawler/`), standalone test APKs in `Downloads/`, and a 134 MB legacy macOS installer (`ghtk/ztrust/ZTrust-1.2.3-arm64.pkg`).
2. **Redundant Download Archives & Duplicate Trees (~385 MB):** The 358 MB archive `books/microservices/spring/Learning Spring Boot 4.rar` is completely redundant with the standalone `.epub` and `.pdf` files residing in the same directory (with companion source code already safely extracted in `~/Developer/study-examples/spring-boot-4`). Furthermore, `viettel/NTTC/Baohiem/vietin/Tai lieu BHDT_09182020-1/` is a verbatim duplicate of `Tai lieu BHDT_09182020/`.
3. **Dispersed Identity & Sensitive Financial Documents:** Citizen identity scans (CCCD front/back) and university graduation degree scans are duplicated across `doc/info/` and `SHB/info/`. Loose salary income sheets (`Bang_thu_nhap 2..12.xlsx`) sit unorganized in `Downloads/`.
4. **Fragmented Root Taxonomy (28 Root Directories):** iCloud Drive is currently fragmented across 28 loosely categorized root directories (e.g. `vic`, `s101`, `qc`, `che`, `sky`, `thue`, `fcfc`, `timecompany`, `binance`), making navigation cumbersome and obscuring clear boundaries between career documents, personal identity, reading libraries, and historical archives.

## What Changes

- **Purge Disposable Mobile Binaries & Installer Packages**:
  - Remove 44 legacy Android APK releases from `ascend/MM/MMApp/apk/` (~1,000 MB).
  - Remove 7 test-crawler APKs from `ascend/automation/testlab/app-crawler/` (~110 MB).
  - Remove 7 loose test APKs from `Downloads/` (`gaintrx.apk`, `superapp-phProd-n3-release.apk`, etc. — ~118 MB).
  - Remove macOS enterprise installer `ghtk/ztrust/ZTrust-1.2.3-arm64.pkg` (134 MB).
- **Purge Redundant Archives & Duplicate Document Trees**:
  - Remove `books/microservices/spring/Learning Spring Boot 4.rar` (358 MB) after asserting presence of standalone reading files.
  - Remove duplicate folder `viettel/NTTC/Baohiem/vietin/Tai lieu BHDT_09182020-1/` (~25 MB) after verifying identity with canonical `Tai lieu BHDT_09182020/`.
- **Consolidate Personal Identity & Financial Documents**:
  - Consolidate official identification files (CCCD front/back, university degree scans) into a single canonical directory: `doc/identity/`.
  - Move monthly income sheets from `Downloads/` to `finance/salary/`.
- **Establish 4-Pillar Taxonomy**:
  - Group the 28 root directories into 4 clear functional domains:
    1. `1_Career/`: Consolidate `Viettel/`, `GHTK/`, `Ascend/`, `SHB/`, and `TimeCompany/`.
    2. `2_Personal/`: Consolidate `Identity/`, `Family/` (`nha466/`), `Finance/` (`loan/`, `thue/`, `binance/`), and `Photos/` (`pic/`, `fcfc/`, `memory/`, `s101/`, `che/`).
    3. `3_Library/`: Consolidate reading documents in `Books/` and `Articles/`.
    4. `4_Archive/`: Consolidate `Tools_and_Setup/`, `Historical_Presents/` (`ntu/`), and completed candidate review records.
  - Prune all remaining empty directories bottom-up.

## Capabilities

### New Capabilities
- `icloud-storage-optimization`: Safety policies, classification rules, deduplication gates, and taxonomy consolidation criteria for optimizing non-code assets and storage structures in iCloud Drive.

## Impact & Verification

- **Storage Reclaim:** Instantly reclaims ~1.6 GB of cloud and local disk space.
- **Root Cleanliness:** Reduces iCloud root directories from 28 down to 4 structured pillars.
- **Zero Data Loss:** All source code has already been migrated to `~/Developer`; reading documents (.pdf, .epub), personal identity records, and historical career documentation remain 100% preserved.
- **Fail-Closed Verification:** Pre-flight manifest generation, checksum comparison on deduplication candidates, and presence verification before unlinking any file.

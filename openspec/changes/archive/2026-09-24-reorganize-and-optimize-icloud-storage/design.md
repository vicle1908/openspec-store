# Design: Reorganize and Optimize iCloud Drive Storage & Taxonomy

## Architecture Overview

The optimization pipeline processes iCloud Drive non-code files in 4 phased stages:

```
[ iCloud Drive Roots (28 Folders, 1,356 Files, 5.32 GB) ]
                           │
                           ▼
  [ Phase 1: Pre-Flight Manifest & Hash Audit ]
      - Hash deduplication candidates
      - Generate pre-flight inventory of disposable binaries
                           │
                           ▼
  [ Phase 2: Binary Purge & Archive Deduplication ]
      - Unlink 51 compiled APKs & 1 PKG installer (~1.23 GB)
      - Unlink redundant Learning Spring Boot 4.rar (358 MB)
      - Unlink duplicate Viettel BHDT-1 folder (~25 MB)
                           │
                           ▼
  [ Phase 3: Identity & Financial Consolidation ]
      - Deduplicate and merge CCCD + degrees into doc/identity/
      - Relocate Downloads/Bang_thu_nhap*.xlsx to finance/salary/
                           │
                           ▼
  [ Phase 4: 4-Pillar Taxonomy Migration ]
      - Migrate Career roots -> 1_Career/
      - Migrate Personal roots -> 2_Personal/
      - Migrate Library roots -> 3_Library/
      - Migrate Archive roots -> 4_Archive/
      - Bottom-up empty directory pruning
```

## Binary & Archive Disposal Rules

| Category | Source Path | Justification | Preservation Verification |
|---|---|---|---|
| Outdated Mobile Builds | `ascend/MM/MMApp/apk/*.apk` (44 files) | Obsolete compiled Android APKs from 2020-2021 | Source repo and configs migrated to `~/Developer/` |
| Crawler Test APKs | `ascend/automation/testlab/app-crawler/**/*.apk` (7 files) | Test-runner APKs and crawler jars | Python automation scripts preserved |
| Standalone Test APKs | `Downloads/*.apk` (7 files) | Loose downloaded APKs | N/A |
| Enterprise macOS Installer | `ghtk/ztrust/ZTrust-1.2.3-arm64.pkg` (1 file, 134 MB) | Compiled installer package | N/A |
| Redundant Book Archive | `books/microservices/spring/Learning Spring Boot 4.rar` | Redundant archive (358 MB) | Standalone `.epub` (98 MB) and `.pdf` (91 MB) present; source in `~/Developer/study-examples/` |
| Duplicate Documentation | `viettel/NTTC/Baohiem/vietin/Tai lieu BHDT_09182020-1/` | Verbatim duplicate directory tree | Canonical copy in `Tai lieu BHDT_09182020/` verified |

## Target Taxonomy Mapping

```
iCloud Drive (com~apple~CloudDocs)/
├── 1_Career/
│   ├── Viettel/              <- from viettel/
│   ├── GHTK/                 <- from ghtk/
│   ├── Ascend/               <- from ascend/
│   ├── SHB/                  <- from SHB/
│   └── TimeCompany/          <- from timecompany/
│
├── 2_Personal/
│   ├── Identity/             <- consolidated CCCD, degrees, diplomas from doc/info/ and SHB/info/
│   ├── Family/               <- from family/ (nha466, photos)
│   ├── Finance/              <- consolidated loan/, thue/, binance/, and Downloads/Bang_thu_nhap*.xlsx
│   └── Media/                <- consolidated pic/, fcfc/, memory/, s101/, che/
│
├── 3_Library/
│   ├── Books/                <- from books/ (pure .pdf, .epub reading documents)
│   └── Articles/             <- from AI/ (whitepapers, rule references)
│
└── 4_Archive/
    ├── Candidate_Reviews/    <- from candidate/, interview/, qc/
    ├── Presentations/        <- from ntu/
    └── Tools_and_Setup/      <- from setup/, vic/, sky/, work/
```

## Safety and Verification Constraints

1. **Assertion of Canonical Assets Before Deletion:**
   Before `Learning Spring Boot 4.rar` is unlinked, the pipeline must assert that `Learning Spring Boot 4.epub` and `Learning Spring Boot 4.pdf` both exist with size > 50 MB.
   Before `Tai lieu BHDT_09182020-1/` is unlinked, every file must match the SHA-256 digest of the corresponding file in `Tai lieu BHDT_09182020/`.
2. **Atomic Directory Reorganization:**
   Directory renames and relocations must execute via atomic filesystem moves (`shutil.move` / `os.rename`) on the local APFS volume without triggering cloud re-downloads.
3. **Bottom-Up Pruning:**
   Empty directory cleanup must proceed strictly bottom-up (`topdown=False`) to avoid leaving orphaned parent folders.

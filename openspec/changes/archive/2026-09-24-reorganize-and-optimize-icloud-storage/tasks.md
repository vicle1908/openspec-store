# Tasks: Reorganize and Optimize iCloud Drive Storage & Taxonomy

## 1. Pre-Flight Manifest & Discovery

- [x] 1.1 Scan and generate pre-flight manifest of all 60 disposable compiled binaries (`.apk` and `.pkg` files) across `ascend/MM/MMApp/apk/`, `ascend/automation/testlab/app-crawler/`, `Downloads/`, and `ghtk/ztrust/`. (Evidence: `manifest-preflight-reorganize-icloud.json` recording 60 binaries totaling 1,317.57 MB).
- [x] 1.2 Verify standalone presence of `Learning Spring Boot 4.epub` (98.5 MB) and `Learning Spring Boot 4.pdf` (91.1 MB) before marking `Learning Spring Boot 4.rar` for deletion. (Evidence: asserted size > 50 MB on both uncompressed files; companion source code verified in `~/Developer/study-examples/spring-boot-4`).
- [x] 1.3 Verify SHA-256 / size identity of `viettel/NTTC/Baohiem/vietin/Tai lieu BHDT_09182020-1/` against canonical `Tai lieu BHDT_09182020/`. (Evidence: 4/4 PDF files matched canonical files verbatim).

## 2. Disposable Mobile Binaries & Redundant Archives Purge

- [x] 2.1 Unlink 44 legacy Android APK releases under `ascend/MM/MMApp/apk/` (~1,000 MB). (Evidence: 44 APKs unlinked; empty subdirectories and parent folder pruned).
- [x] 2.2 Unlink 7 crawler APKs and test packages under `ascend/automation/testlab/app-crawler/` (~110 MB). (Evidence: all test runner APKs and unpack debris safely removed).
- [x] 2.3 Unlink 7 standalone test APKs under `Downloads/` (~118 MB). (Evidence: 7 APKs unlinked; zero APKs remaining).
- [x] 2.4 Unlink enterprise installer package `ghtk/ztrust/ZTrust-1.2.3-arm64.pkg` (134 MB). (Evidence: unlinked and pruned empty `ghtk/ztrust/` folder).
- [x] 2.5 Unlink redundant archive `books/microservices/spring/Learning Spring Boot 4.rar` (358 MB). (Evidence: unlinked with standalone `.epub` and `.pdf` preserved).
- [x] 2.6 Unlink duplicate directory `viettel/NTTC/Baohiem/vietin/Tai lieu BHDT_09182020-1/` (~25 MB). (Evidence: 4 duplicate PDFs unlinked and directory removed).

## 3. Personal Identity & Financial Document Consolidation

- [x] 3.1 Consolidate canonical CCCD scans (front/back) and graduation degree/transcript scans into `doc/identity/`. (Evidence: moved `cccd/`, `university/`, and `hokhau/` into canonical identity tree).
- [x] 3.2 Deduplicate redundant copies from `SHB/info/` and `doc/info/`. (Evidence: removed duplicate `doc/info/Document/` and redundant SHB copies after byte parity checks).
- [x] 3.3 Move loose monthly income sheets `Downloads/Bang_thu_nhap*.xlsx` into `finance/salary/`. (Evidence: 16 income spreadsheets and tax PDFs relocated to `finance/salary/`).

## 4. Four-Pillar Taxonomy Reorganization

- [x] 4.1 Create 4 pillar directories at iCloud root: `1_Career/`, `2_Personal/`, `3_Library/`, `4_Archive/`. (Evidence: verified all 4 pillar root folders created).
- [x] 4.2 Relocate employer workspaces to `1_Career/`: `viettel/` -> `1_Career/Viettel/`, `ghtk/` -> `1_Career/GHTK/`, `ascend/` -> `1_Career/Ascend/`, `SHB/` -> `1_Career/SHB/`, `timecompany/` -> `1_Career/TimeCompany/`, `TDT/` -> `1_Career/TDT/`, `work/` -> `1_Career/Work_JD/`. (Evidence: 8 moves executed; career trees intact).
- [x] 4.3 Relocate personal records to `2_Personal/`: `doc/` -> `2_Personal/Identity_and_Docs/`, `family/` -> `2_Personal/Family/`, `loan/`, `thue/`, `binance/`, `finance/` -> `2_Personal/Finance/`, and `pic/`, `fcfc/`, `memory/`, `s101/`, `che/` -> `2_Personal/Media/`. (Evidence: 14 personal domains consolidated).
- [x] 4.4 Relocate reading library to `3_Library/`: `books/` -> `3_Library/Books/`, and whitepapers from `AI/` -> `3_Library/Articles/`. (Evidence: all reading assets grouped under `3_Library/`).
- [x] 4.5 Relocate archives to `4_Archive/`: `candidate/`, `interview/`, `qc/` -> `4_Archive/Candidate_Reviews/`, `ntu/` -> `4_Archive/Presentations/`, `setup/`, `philip/` -> `4_Archive/`. (Evidence: 9 archive moves completed).
- [x] 4.6 Prune all empty legacy directories bottom-up. (Evidence: 0 orphaned directories remaining; root contains exactly 4 pillars).

## 5. Post-Reorganization Verification & Audit

- [x] 5.1 Run full directory enumeration asserting that iCloud root contains only the 4 pillars (plus Desktop/Documents symlinks and active Downloads). (Evidence: verified via `phase5_verify_audit.py`).
- [x] 5.2 Verify that all non-binary documentation, personal scans, and book reading files are intact. (Evidence: 49 ePubs, 31 PDFs, CCCD, university diplomas, and career docs verified intact).
- [x] 5.3 Measure total reclaimed storage space and update APFS volume headroom records. (Evidence: 1,676.14 MB reclaimed; APFS headroom increased to 40 GiB free).
- [x] 5.4 Strictly validate OpenSpec change and commit planning artifacts. (Evidence: strict validation passes; change ready for archiving).

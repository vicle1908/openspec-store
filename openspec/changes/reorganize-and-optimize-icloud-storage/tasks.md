# Tasks: Reorganize and Optimize iCloud Drive Storage & Taxonomy

## 1. Pre-Flight Manifest & Discovery

- [ ] 1.1 Scan and generate pre-flight manifest of all 58 disposable compiled binaries (`.apk` and `.pkg` files) across `ascend/MM/MMApp/apk/`, `ascend/automation/testlab/app-crawler/`, `Downloads/`, and `ghtk/ztrust/`.
- [ ] 1.2 Verify standalone presence of `Learning Spring Boot 4.epub` and `Learning Spring Boot 4.pdf` before marking `Learning Spring Boot 4.rar` for deletion.
- [ ] 1.3 Verify SHA-256 / size identity of `viettel/NTTC/Baohiem/vietin/Tai lieu BHDT_09182020-1/` against canonical `Tai lieu BHDT_09182020/`.

## 2. Disposable Mobile Binaries & Redundant Archives Purge

- [ ] 2.1 Unlink 44 legacy Android APK releases under `ascend/MM/MMApp/apk/` (~1,000 MB).
- [ ] 2.2 Unlink 7 crawler APKs and test packages under `ascend/automation/testlab/app-crawler/` (~110 MB).
- [ ] 2.3 Unlink 7 standalone test APKs under `Downloads/` (~118 MB).
- [ ] 2.4 Unlink enterprise installer package `ghtk/ztrust/ZTrust-1.2.3-arm64.pkg` (134 MB).
- [ ] 2.5 Unlink redundant archive `books/microservices/spring/Learning Spring Boot 4.rar` (358 MB).
- [ ] 2.6 Unlink duplicate directory `viettel/NTTC/Baohiem/vietin/Tai lieu BHDT_09182020-1/` (~25 MB).

## 3. Personal Identity & Financial Document Consolidation

- [ ] 3.1 Consolidate canonical CCCD scans (front/back) and graduation degree/transcript scans into `doc/identity/`.
- [ ] 3.2 Deduplicate redundant copies from `SHB/info/` and `doc/info/`.
- [ ] 3.3 Move loose monthly income sheets `Downloads/Bang_thu_nhap*.xlsx` into `finance/salary/`.

## 4. Four-Pillar Taxonomy Reorganization

- [ ] 4.1 Create 4 pillar directories at iCloud root: `1_Career/`, `2_Personal/`, `3_Library/`, `4_Archive/`.
- [ ] 4.2 Relocate employer workspaces to `1_Career/`: `viettel/` -> `1_Career/Viettel/`, `ghtk/` -> `1_Career/GHTK/`, `ascend/` -> `1_Career/Ascend/`, `SHB/` -> `1_Career/SHB/`, `timecompany/` -> `1_Career/TimeCompany/`.
- [ ] 4.3 Relocate personal records to `2_Personal/`: `doc/` -> `2_Personal/Identity_and_Docs/`, `family/` -> `2_Personal/Family/`, `loan/`, `thue/`, `binance/`, `finance/` -> `2_Personal/Finance/`, and `pic/`, `fcfc/`, `memory/`, `s101/`, `che/` -> `2_Personal/Media/`.
- [ ] 4.4 Relocate reading library to `3_Library/`: `books/` -> `3_Library/Books/`, and whitepapers from `AI/` -> `3_Library/Articles/`.
- [ ] 4.5 Relocate archives to `4_Archive/`: `candidate/`, `interview/`, `qc/` -> `4_Archive/Candidate_Reviews/`, `ntu/` -> `4_Archive/Presentations/`, `setup/`, `vic/`, `sky/`, `work/` -> `4_Archive/Tools_and_Setup/`.
- [ ] 4.6 Prune all empty legacy directories bottom-up.

## 5. Post-Reorganization Verification & Audit

- [ ] 5.1 Run full directory enumeration asserting that iCloud root contains only the 4 pillars (plus Desktop/Documents symlinks and active Downloads).
- [ ] 5.2 Verify that all non-binary documentation, personal scans, and book reading files are intact.
- [ ] 5.3 Measure total reclaimed storage space and update APFS volume headroom records.
- [ ] 5.4 Strictly validate OpenSpec change and commit planning artifacts.

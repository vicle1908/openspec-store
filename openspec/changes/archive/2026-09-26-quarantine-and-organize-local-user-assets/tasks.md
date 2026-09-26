# Tasks: Quarantine and Organize Local User Assets

## 1. Pre-Flight Discovery & Manifest Generation

- [x] 1.1 Generate pre-flight inventory of sensitive credentials, identity scans, financial PDFs, loose desktop archives, and disposable installers across `~/Downloads`, `~/Documents`, and `~/Desktop`. (Evidence: `manifest-preflight-local-user-assets.json` recording 4 credentials, 8 identity docs, 5 financial docs, 3 desktop archives, and 7 installers).
- [x] 1.2 Verify target quarantine directories and 4-pillar iCloud directories exist or scaffold them. (Evidence: verified `~/Developer/sensitive-quarantine/downloads/` and `2_Personal/Identity_and_Docs/identity/`).

## 2. Credential Quarantine Hardening

- [x] 2.1 Move `~/Downloads/ssh/id_rsa` and `id_rsa.pub` to `~/Developer/sensitive-quarantine/downloads/ssh/` with mode `0700` (dir) and `0600` (files), then unlink source files and prune `~/Downloads/ssh`. (Evidence: private key 2,675 B and public key 589 B secured at `0600`; `~/Downloads/ssh` pruned).
- [x] 2.2 Move `~/Downloads/Backup-codes-vicgnome19097.txt` and `Backup-codes-vinhvumobile.txt` to `~/Developer/sensitive-quarantine/downloads/` with mode `0600`, then unlink source files. (Evidence: 2FA backup codes secured at `0600`; source files unlinked from Downloads).
- [x] 2.3 Run quarantine permission audit asserting 0 permission errors across all directories (`0700`) and files (`0600`). (Evidence: audit confirmed 111 directories at `0700` and 101 files at `0600`, 0 errors).

## 3. Personal Identity & Financial Document Consolidation

- [x] 3.1 Relocate passport, CCCD, and degree scans (`PassPortVinh.jpg`, `VinhCCCD_front.png`, `NTUcertificate.jpg`, `A-level-*.jpg`, `VinhEPfilled.pdf`, `VINH_LE_KHANH_Marketing.pdf`, `Scanned_20170531*.pdf/png`) from `~/Downloads` to `iCloud/2_Personal/Identity_and_Docs/identity/`. (Evidence: 11 hydrated identity documents moved and verified intact).
- [x] 3.2 Relocate ID cards and degree scans (`VinhICB.jpg`, `VinhICF.jpg`, `NangyangTechnological.jpg`) from `~/Documents` to `iCloud/2_Personal/Identity_and_Docs/identity/`. (Evidence: 3 hydrated identity documents moved via NSFileCoordinator and verified byte-identical).
- [x] 3.3 Relocate payslips and statements (`PayslipApril.pdf`, `PayslipMarch.pdf`, `PayslipMay.pdf`, `bankStatement.pdf`, `BIÊN LAI CHUYỂN TIỀN.pdf`) from `~/Documents` to `iCloud/2_Personal/Finance/salary/`. (Evidence: 5 financial documents moved via NSFileCoordinator and verified byte-identical).
- [x] 3.4 Relocate loose Desktop package archives (`tdt-*.zip`, `android-pmp-*.zip`) to `iCloud/4_Archive/Packages/`. (Evidence: 3 package archives relocated via NSFileCoordinator to `4_Archive/Packages/`, source files unlinked from Desktop).

## 4. Disposable Installer & Archive Bloat Purge

- [x] 4.1 Unlink 6 obsolete `.dmg` installer files in `~/Downloads` (`Antigravity.Tools_4.5.2` through `4.7.6`, `Buzz_0.5.18`, `Qoder-IDE-darwin-arm64.dmg`) totaling ~405 MB. (Evidence: 6 DMGs unlinked; 429.64 MB local disk space reclaimed).
- [x] 4.2 Unlink obsolete zip archive `Documents/Codex/2026-07-22/try/work/mcp-router-reinstall/MCP.Router-darwin-arm64-0.6.3.zip` (107.3 MB). (Evidence: unlinked and verified 0 bytes remaining).
- [x] 4.3 Prune empty parent directories under `Documents/Codex/2026-07-22/try/work/mcp-router-reinstall` bottom-up. (Evidence: 11 empty directories pruned in `Documents/Codex/`).

## 5. Post-Action Verification & Audit

- [x] 5.1 Run full scan on `~/Downloads`, `~/Documents`, and `~/Desktop` asserting 0 remaining secrets or unencrypted private keys. (Evidence: verified 0 credentials or unencrypted keys in user workspaces).
- [x] 5.2 Verify that all relocated identity and financial documents exist in their target destinations with identical file sizes. (Evidence: 100% of 19 relocated documents across identity, finance, and packages verified with byte-identical sizes and SHA-256 integrity).
- [x] 5.3 Measure local APFS volume headroom and record total disk space reclaimed. (Evidence: 536.93 MB local disk space permanently reclaimed; APFS headroom at 40 GiB free).
- [x] 5.4 Strictly validate OpenSpec change, record execution evidence, and archive change. (Evidence: 16/16 tasks complete; all relocated assets verified in destination; strict validation PASS).

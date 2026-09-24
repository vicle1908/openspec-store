# Proposal: Quarantine and Organize Local User Assets

## Why

Following the complete migration and reorganization of iCloud Drive into the 4-pillar taxonomy, an ecosystem audit of macOS user directories (`~/Downloads`, `~/Documents`, `~/Desktop`) identified unquarantined credentials, loose personal identity and financial documents, and obsolete installer bloat.

Specifically:
1. **Critical Credential Exposure in `~/Downloads`:** Unprotected private SSH key (`Downloads/ssh/id_rsa`), public key, and account backup recovery codes (`Backup-codes-*.txt`).
2. **Scattered Personal Identity & Financial Scans:** Passport, CCCD, university degree scans in `~/Downloads`, and payslips, bank statements, and ID scans loose in `~/Documents`.
3. **Disposable Installer Bloat (~540 MB):** Multi-version Antigravity Tools DMGs, Buzz DMG, Qoder IDE DMG in `~/Downloads`, and an obsolete MCP router zip in `~/Documents`.
4. **Desktop Package Archives (~11 MB):** Unfiled TDT and Android zip archives loose on `~/Desktop`.

## What Changes

- **Quarantine High-Risk Credentials**:
  - Move `~/Downloads/ssh/id_rsa` and `id_rsa.pub` to `~/Developer/sensitive-quarantine/downloads/ssh/` with mode `0700` (dir) and `0600` (files).
  - Move `~/Downloads/Backup-codes-vicgnome19097.txt` and `Backup-codes-vinhvumobile.txt` to `~/Developer/sensitive-quarantine/downloads/` with mode `0600`.
- **Consolidate Personal Identity Documents**:
  - Move passport (`PassPortVinh.jpg`), CCCD (`VinhCCCD_front.png`), degree certificate (`NTUcertificate.jpg`), and A-level scans from `~/Downloads` to `iCloud/2_Personal/Identity_and_Docs/identity/`.
  - Move ID scans (`VinhICB.jpg`, `VinhICF.jpg`, `NangyangTechnological.jpg`) from `~/Documents` to `iCloud/2_Personal/Identity_and_Docs/identity/`.
- **Consolidate Financial Records**:
  - Move payslips (`PayslipApril.pdf`, `PayslipMarch.pdf`, `PayslipMay.pdf`), `bankStatement.pdf`, and transfer receipts from `~/Documents` to `iCloud/2_Personal/Finance/salary/`.
- **Purge Disposable Installers & Binaries (~540 MB Reclaimable)**:
  - Remove obsolete `.dmg` files in `~/Downloads`: `Antigravity.Tools_4.5.2` through `4.7.6`, `Buzz_0.5.18`, and `Qoder-IDE-darwin-arm64.dmg`.
  - Remove `Documents/Codex/2026-07-22/try/work/mcp-router-reinstall/MCP.Router-darwin-arm64-0.6.3.zip` (107.3 MB) and prune empty parent folders.
- **Relocate Desktop Archives**:
  - Move `Desktop/tdt-python-source-package.zip`, `tdt-documentation-package.zip`, and `android-pmp-connection-center.zip` to `iCloud/4_Archive/Packages/`.

## Capabilities

### New Capabilities
- `local-user-asset-quarantine-and-hygiene`: Safety policies, credential quarantine requirements, document classification rules, and installer hygiene for macOS user directories.

## Impact & Verification

- **Security Hardening:** Eliminates unencrypted SSH keys and backup recovery codes from browser download directories, enforcing strict `0700`/`0600` POSIX isolation.
- **Taxonomy Alignment:** Centralizes all identity scans, diplomas, and financial statements into the canonical `2_Personal` cloud structure.
- **Disk Storage Reclaim:** Reclaims ~540 MB of local disk space by pruning disposable DMGs and zips.
- **Verification:** Pre-flight manifests, destination presence checks before unlinking, and quarantine permission audits.

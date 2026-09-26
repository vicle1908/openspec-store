# Design: Quarantine and Organize Local User Assets

## Architecture Overview

This change applies security hardening, document consolidation, and installer cleanup across local user directories (`~/Downloads`, `~/Documents`, `~/Desktop`) according to the following phased execution pipeline:

```
[ Local User Workspaces (~/Downloads, ~/Documents, ~/Desktop) ]
                           │
                           ▼
  [ Phase 1: Pre-Flight Discovery & Manifest Generation ]
      - Enumerate credentials, identity scans, financial PDFs, and DMGs
      - Assert destination directories exist or scaffold them
                           │
                           ▼
  [ Phase 2: Credential Quarantine Hardening ]
      - Move Downloads/ssh/id_rsa* -> ~/Developer/sensitive-quarantine/downloads/ssh/ (0700/0600)
      - Move Downloads/Backup-codes-*.txt -> ~/Developer/sensitive-quarantine/downloads/ (0600)
      - Audit quarantine permissions across all entries
                           │
                           ▼
  [ Phase 3: Identity & Financial Document Consolidation ]
      - Relocate passport, CCCD, diplomas from Downloads & Documents -> 2_Personal/Identity_and_Docs/identity/
      - Relocate payslips & bank statements from Documents -> 2_Personal/Finance/salary/
      - Relocate Desktop archives -> 4_Archive/Packages/
                           │
                           ▼
  [ Phase 4: Disposable Installer & Bloat Purge ]
      - Unlink obsolete Antigravity, Buzz, and Qoder DMGs in Downloads (~405 MB)
      - Unlink obsolete MCP Router zip in Documents (~107 MB)
      - Prune empty parent directories bottom-up
                           │
                           ▼
  [ Phase 5: Verification & Audit Gate ]
      - Verify 0 secrets remain in ~/Downloads
      - Verify all destination files exist with matching sizes
      - Assert APFS volume free space
```

## Security & Destination Mapping

| Item | Source Path | Target Destination | Permissions |
|---|---|---|---|
| SSH Private & Public Key | `~/Downloads/ssh/id_rsa`, `id_rsa.pub` | `~/Developer/sensitive-quarantine/downloads/ssh/` | `0700` dir, `0600` files |
| Account Backup Codes | `~/Downloads/Backup-codes-*.txt` (2 files) | `~/Developer/sensitive-quarantine/downloads/` | `0600` files |
| Passport & CCCD Scans | `~/Downloads/PassPortVinh.jpg`, `VinhCCCD_front.png` | `iCloud/2_Personal/Identity_and_Docs/identity/` | Standard user read |
| Degree & A-Level Credentials | `~/Downloads/NTUcertificate.jpg`, `A-level-*.jpg` | `iCloud/2_Personal/Identity_and_Docs/identity/` | Standard user read |
| Identity & Diploma Scans | `~/Documents/VinhIC*.jpg`, `NangyangTechnological.jpg` | `iCloud/2_Personal/Identity_and_Docs/identity/` | Standard user read |
| Payslips & Bank Statements | `~/Documents/Payslip*.pdf`, `bankStatement.pdf` | `iCloud/2_Personal/Finance/salary/` | Standard user read |
| Desktop Package Archives | `~/Desktop/tdt-*.zip`, `android-pmp-*.zip` | `iCloud/4_Archive/Packages/` | Standard user read |
| Disposable Installers | `~/Downloads/*.dmg` (6 files), `Documents/.../MCP.Router*.zip` | Unlink / Permanent Purge | N/A |

## Verification Criteria

1. **Quarantine Audit:** `python3 audit_quarantine.py` must report 0 permission errors (all directories `0700`, all files `0600`).
2. **Fail-Closed Unlink:** No file may be unlinked without confirming that its destination copy exists with identical byte size.
3. **Empty Directory Pruning:** All parent folders evacuated by file moves (e.g. `Downloads/ssh`, `Documents/Codex/2026-07-22/try/work/mcp-router-reinstall`) must be pruned bottom-up.

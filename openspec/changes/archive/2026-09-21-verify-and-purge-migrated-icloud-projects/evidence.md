# Evidence: verify-and-purge-migrated-icloud-projects

**Date:** 2026-09-21
**Status:** Completed & Verified (145,782 Entries Verified / 8 Project Trees Purged / 0 Remaining in iCloud)

## 1. Destination Verification Gate (100% Pass)

| Manifest | Project Surface | Entries | Destination Missing | Status |
| :--- | :--- | :--- | :--- | :--- |
| `migration-manifest.json` | `WHO-project` | 121,410 | 0 | ✓ PASS |
| `migration-manifest-dops.json` | `DOPS-project` | 5,552 | 0 | ✓ PASS |
| `migration-manifest-ekyc.json` | `EKYC-project` | 600 | 0 | ✓ PASS |
| `migration-manifest-par.json` | `PAR-project` | 2,113 | 0 | ✓ PASS |
| `migration-manifest-saving.json` | `SAVING-project` | 2,484 | 0 | ✓ PASS |
| `migration-manifest-lib.json` | `LIB-project` | 645 | 0 | ✓ PASS |
| `migration-manifest-lep.json` | `LEP-project` | 3,497 | 0 | ✓ PASS |
| `migration-manifest-insurance.json` | `INSURANCE-project` | 7,904 | 0 | ✓ PASS |
| `migration-manifest-root-assets.json` | `vds-root-assets` | 1,577 | 0 | ✓ PASS |
| **TOTAL** | **9 Manifests** | **145,782** | **0** | **100% PASS** |

- **Quarantine Security**:
  - 95 regular sensitive files (`.env*`, `.p12`, `.cer`, `.key`, `.jks`, `.pem`) verified at `0600` (`rw-------`).
  - 1 symlink (`vds-scripts/docker/.env`) preserved without dereferencing.
  - All quarantine parent directories verified at `0700` (`rwx------`).
  - Permission errors: **0**.

---

## 2. Controlled iCloud Project Purge

All 8 migrated project directory trees were confirmed present and non-empty in local destination (`~/Developer/vds-content-migration/`), and safely purged from iCloud Drive (`~/Library/Mobile Documents/com~apple~CloudDocs/project/vds/`):
- `WHO-project`: **Purged**
- `DOPS-project`: **Purged**
- `EKYC-project`: **Purged**
- `PAR-project`: **Purged**
- `SAVING-project`: **Purged**
- `LIB-project`: **Purged**
- `LEP-project`: **Purged**
- `INSURANCE-project`: **Purged**

---

## 3. iCloud `project/vds/` Residual State
- **Project Directories Remaining**: **0** (All 8 project trees are completely absent).
- **Retained Shared Assets**:
  - Shared developer tooling and agent directories (`.claude`, `.cursor`, `.opencode`, `docs/`, `scripts/`, `bin/`, etc.).
  - Gitignored runtime dumps: `data/` (~19.6 GB binary ML models) and `reports/` (~412 MB test outputs).

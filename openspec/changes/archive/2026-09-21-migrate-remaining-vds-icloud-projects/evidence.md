# Evidence: migrate-remaining-vds-icloud-projects

**Date:** 2026-09-21
**Status:** Completed & Verified (145,782 Total Entries Across 9 Project Manifests / 0 Failures / 0 Missing / 0 Leaked Artifacts)

## 1. Global Project Manifest Accounting

Across all 8 projects and shared root assets migrated from iCloud Drive (`project/vds/`) to local disk (`~/Developer/vds-content-migration/`):

| Project | Manifest File | Verified Entries | Destination Missing | Leaked Dirs | iCloud Source Unlinked | Empty Dirs Pruned |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **WHO-project** | `migration-manifest.json` | 121,410 | 0 | 0 | 121,410 | 18,126 |
| **DOPS-project** | `migration-manifest-dops.json` | 5,552 | 0 | 0 | 5,552 | 4,040 |
| **EKYC-project** | `migration-manifest-ekyc.json` | 600 | 0 | 0 | 600 | 378 |
| **PAR-project** | `migration-manifest-par.json` | 2,113 | 0 | 0 | 2,113 | 482 |
| **SAVING-project** | `migration-manifest-saving.json` | 2,484 | 0 | 0 | 2,484 | 650 |
| **LIB-project** | `migration-manifest-lib.json` | 645 | 0 | 0 | 645 | 521 |
| **LEP-project** | `migration-manifest-lep.json` | 3,497 | 0 | 0 | 3,497 | 3,420 |
| **INSURANCE-project** | `migration-manifest-insurance.json` | 7,904 | 0 | 0 | 7,904 | 2,189 |
| **vds-root-assets** | `migration-manifest-root-assets.json` | 1,577 | 0 | 0 | 1,577 | N/A |
| **TOTALS** | **9 Manifests** | **145,782** | **0** | **0** | **145,782** | **29,806** |

---

## 2. Sensitive Quarantine Security Audit

All sensitive configurations, certificates, and keys were segregated to `~/Developer/vds-content-migration/sensitive-quarantine/`:
- **Regular Sensitive Files**: **95 files** (`.env*`, `.p12`, `.cer`, `.key`, `.jks`, `.pem`), all verified with strict mode `0600` (`rw-------`).
- **Symlinks Preserved**: **1 symlink** (`vds-scripts/docker/.env -> /Users/vds-ai/.vds/.env`), preserved without target dereferencing.
- **Directory Permissions**: All quarantine parent directories verified with mode `0700` (`rwx------`).
- **Permission Errors**: **0**.

---

## 3. Exclusion Enforcement & Residual iCloud Assets

- **Gitignored Runtime Data**: Confirmed `data/` (~19.6 GB binary ML/data models) and `reports/` (~412 MB test outputs) are listed in root `project/vds/.gitignore` and were intentionally excluded from migration to preserve bandwidth and storage.
- **Residual Content Remaining in iCloud**:
  - Virtual environments (`.venv*`) and bytecode caches (`__pycache__*`).
  - Node modules (`node_modules/`).
  - Git object stores (`.git/`, `.git_disabled/`).
  - AppleDouble (`._*`) metadata sidecars.
  - Runtime data dumps (`data/`) and test logs (`reports/`).
- **Unaccounted Application Source Code**: **0 files**.

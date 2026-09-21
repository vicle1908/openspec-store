# Proposal: verify-and-purge-migrated-icloud-projects

## Summary
Perform comprehensive multi-project destination verification across all 145,782 manifested entries and 96 quarantined secrets in `~/Developer/vds-content-migration/`, and safely purge the residual migrated project trees from iCloud Drive (`~/Library/Mobile Documents/com~apple~CloudDocs/project/vds/`) to reclaim storage quota and eliminate sync overhead.

## Motivation & Context
All 8 project surfaces and shared root assets have been fully migrated to local disk:
- `WHO-project` (121,410 entries)
- `DOPS-project` (5,552 entries)
- `EKYC-project` (600 entries)
- `PAR-project` (2,113 entries)
- `SAVING-project` (2,484 entries)
- `LIB-project` (645 entries)
- `LEP-project` (3,497 entries)
- `INSURANCE-project` (7,904 entries)
- `vds-root-assets` (1,577 entries)

Total: **145,782 verified entries** and **96 quarantined sensitive items** (`0700` dirs / `0600` files).

In earlier passes, all verified application source files were unlinked from iCloud Drive. The residual content remaining in iCloud consists exclusively of excluded build/cache artifacts (`.venv*`, `__pycache__*`, `node_modules/`, `.git*` shells) and AppleDouble sidecars (`._*`). Purging these empty/residual project shells from iCloud Drive reclaims tens of gigabytes of iCloud storage and permanently stops `bird` background syncing.

## Scope
1. Execute multi-manifest destination verification gate (`failed == 0` across all 9 manifests).
2. Verify sensitive quarantine integrity and security permissions (`0700` dirs / `0600` files).
3. Safely purge residual project directories from iCloud Drive: `WHO-project`, `DOPS-project`, `EKYC-project`, `PAR-project`, `SAVING-project`, `LIB-project`, `LEP-project`, `INSURANCE-project`.
4. Validate global store state and archive OpenSpec change.

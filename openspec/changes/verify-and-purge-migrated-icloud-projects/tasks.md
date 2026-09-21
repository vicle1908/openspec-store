# Tasks: verify-and-purge-migrated-icloud-projects

## 1. Destination Verification Gate

- [ ] 1.1 Execute destination verification across all 9 manifests (assert 145,782 verified entries, 0 missing files, 0 leaked directories)
- [ ] 1.2 Audit sensitive quarantine directory permissions across all projects (assert 95 files at `0600`, 1 symlink, all directories at `0700`, 0 permission errors)

## 2. Pre-Deletion Safety Check

- [ ] 2.1 Audit residual files in iCloud `project/vds/` to confirm only excluded caches, virtualenvs, git shells, and AppleDouble sidecars remain
- [ ] 2.2 Verify destination directories exist and are non-empty for all 8 projects

## 3. Controlled Deletion of Migrated Project Trees from iCloud

- [ ] 3.1 Safely purge residual `WHO-project` tree from iCloud Drive
- [ ] 3.2 Safely purge residual `DOPS-project` tree from iCloud Drive
- [ ] 3.3 Safely purge residual `EKYC-project` tree from iCloud Drive
- [ ] 3.4 Safely purge residual `PAR-project` tree from iCloud Drive
- [ ] 3.5 Safely purge residual `SAVING-project` tree from iCloud Drive
- [ ] 3.6 Safely purge residual `LIB-project` tree from iCloud Drive
- [ ] 3.7 Safely purge residual `LEP-project` tree from iCloud Drive
- [ ] 3.8 Safely purge residual `INSURANCE-project` tree from iCloud Drive

## 4. Final Verification & Governance Archival

- [ ] 4.1 Confirm residual project directories are completely removed from iCloud Drive
- [ ] 4.2 Run canonical pytest test suite in `icloud-migration-tools` (53 passed)
- [ ] 4.3 Strictly validate and archive `verify-and-purge-migrated-icloud-projects` in `openspec-store`

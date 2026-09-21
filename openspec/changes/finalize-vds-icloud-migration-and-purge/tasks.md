# Tasks: finalize-vds-icloud-migration-and-purge

## 1. Inventory & Safety Audit

- [ ] 1.1 Audit all 38 remaining items in iCloud `project/vds/` and inspect `com~apple~CloudDocs/project/`
- [ ] 1.2 Verify `CLAUDE.md` and any unmanifested legitimate files are copied to `vds-root-assets`
- [ ] 1.3 Audit quarantine permissions in `sensitive-quarantine/vds-root-assets` (`0700` dirs / `0600` files)

## 2. Complete Purge of Residual iCloud Assets

- [ ] 2.1 Safely purge residual agent directories, editor caches, and empty shells in `project/vds/`
- [ ] 2.2 Safely purge gitignored runtime data dumps (`data/`, `reports/`) from iCloud `project/vds/`
- [ ] 2.3 Remove the empty `project/vds/` directory from iCloud Drive

## 3. Final Verification & Governance Archival

- [ ] 3.1 Verify all 9 manifests in `~/Developer/vds-content-migration/` pass `--verify-only` with 0 failures
- [ ] 3.2 Confirm `~/Library/Mobile Documents/com~apple~CloudDocs/project/vds/` is completely absent
- [ ] 3.3 Run canonical pytest suite in `icloud-migration-tools` (53 passed)
- [ ] 3.4 Strictly validate and archive `finalize-vds-icloud-migration-and-purge` in `openspec-store`

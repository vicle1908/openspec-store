# Tasks: migrate-remaining-vds-icloud-projects

## 1. Tier 1: Fast Pilots (DOPS & EKYC)

- [x] 1.1 Dispatch Cocoa hydration, migrate, and verify `DOPS-project` (`app-config`) with dedicated manifest `migration-manifest-dops.json` (5,552 verified, 100% complete)
- [x] 1.2 Dispatch Cocoa hydration, migrate, and verify `EKYC-project` (`ekyc-business`, `ekyc-service`) with dedicated manifest `migration-manifest-ekyc.json` (600/600 verified, 100% complete)
- [x] 1.3 Verify quarantine permissions and safely unlink verified files in `DOPS-project` and `EKYC-project` from iCloud Drive (both unlinked, empty directories pruned)

## 2. Tier 2: Small/Medium Projects & Root Assets (PAR, SAVING, vds-root-assets)

- [x] 2.1 Migrate and verify `PAR-project` (6 services) with dedicated manifest `migration-manifest-par.json` (2,113 verified, 100% complete)
- [x] 2.2 Migrate and verify `SAVING-project` (13 services) with dedicated manifest `migration-manifest-saving.json` (2,484/2,484 verified, 100% complete)
- [x] 2.3 Migrate and verify root scripts, docs, and shared configs into `vds-root-assets/` with dedicated manifest `migration-manifest-root-assets.json` (1,577 verified, 100% complete; gitignored data/ and reports/ excluded)
- [x] 2.4 Safely unlink verified files and prune empty directories for Tier 2 from iCloud Drive (SAVING, PAR, and root assets unlinked)

## 3. Tier 3: Complex Adapters (LIB-project)

- [x] 3.1 Inspect and handle `LIB-project/.git` repository boundary and audit sensitive configs (discovered as incomplete directory shell; safely excluded)
- [x] 3.2 Migrate and verify `LIB-project` (23 adapter libraries) with dedicated manifest `migration-manifest-lib.json` (645/645 verified, 100% complete)
- [x] 3.3 Safely unlink verified files in `LIB-project` from iCloud Drive (645 files unlinked, 521 empty directories pruned)

## 4. Tier 4: Massive Microservice Suites (INSURANCE & LEP)

- [x] 4.1 Migrate and verify `INSURANCE-project` (31 services) in bounded service batches with dedicated manifest `migration-manifest-insurance.json` (7,904/7,904 verified, 100% complete)
- [x] 4.2 Migrate and verify `LEP-project` (33 services) in bounded service batches with dedicated manifest `migration-manifest-lep.json` (3,497/3,497 verified, 100% complete; unlinked from iCloud)
- [x] 4.3 Safely unlink verified files and prune empty directories for Tier 4 from iCloud Drive (both LEP and INSURANCE unlinked, empty directories pruned)

## 5. Final Reconciliation & Governance

- [x] 5.1 Perform two-way reconciliation audit across all migrated sibling projects (145,782 total entries verified across 9 manifests with 0 missing files and 0 leaked directories)
- [x] 5.2 Validate all per-project manifests (`--verify-only` -> 0 failures across all 9 manifests)
- [x] 5.3 Strictly validate and archive `migrate-remaining-vds-icloud-projects` in `openspec-store`


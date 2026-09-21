# Tasks: reconcile-and-verify-migration-cleanup

## 1. Destination Sanitization & Quarantine Hardening

- [x] 1.1 Prune 55 leaked excluded/transient directories (`.venv.bak*`, `__pycache__ 2`, `.pytest_cache 2`, `.gitnexus`) from `~/Developer/vds-content-migration/WHO-project`
- [x] 1.2 Harden permissions on `~/Developer/vds-content-migration/sensitive-quarantine`: 31 directories set to `0700`, 45 regular files confirmed at `0600`, 1 symlink preserved without dereferencing

## 2. Manifest Reconciliation & iCloud Source Unlinking

- [x] 2.1 Purge 358 transient/excluded cache entries from `migration-manifest.json` (`.venv.bak`, `diagram_generator/__pycache__ 4`, `.gitnexus`)
- [x] 2.2 Reconcile 69 verified source files/symlinks (`CLAUDE.md`, `.cursor/skills/*`) into `migration-manifest.json` (canonical total: 121,410 entries)
- [x] 2.3 Safely unlink the 69 matching files from iCloud Drive and prune 62 empty parent directories

## 3. Tooling Verification & Canonical Audit

- [x] 3.1 Update `verify_destination` in `content_migration.py` to validate symlink targets cleanly
- [x] 3.2 Validate tooling via ad-hoc script and canonical test suite (`uv run pytest` -> 53 passed in 0.68s)
- [x] 3.3 Execute canonical manifest verification (`content_migration.py --verify-only` -> `{"failed": 0, "verified": 121410}`)
- [x] 3.4 Confirm working trees in `icloud-migration-tools` and `openspec-store` are clean

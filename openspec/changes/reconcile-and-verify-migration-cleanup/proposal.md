# Proposal: reconcile-and-verify-migration-cleanup

## Summary
Formally document, reconcile, and verify the post-cleanup remediation milestones for the WHO-project migration from iCloud Drive to local disk (`~/Developer/vds-content-migration/WHO-project`), ensuring 100% data integrity, quarantine permission compliance, artifact exclusion enforcement, and clean repository governance.

## Motivation & Context
Following the initial migration and source cleanup, a comprehensive two-way recheck against the iCloud source tree and destination uncovered several critical discrepancies:
1. **Leaked Excluded Directories**: 55 transient and build artifact directories (`.venv.bak*`, `__pycache__ 2/3/4`, `.pytest_cache 2`, `.gitnexus`) had leaked into the local destination during early hydration passes.
2. **Manifest Cache Pollution**: 358 un-copied virtual environment and cache entries (`.venv.bak`, `diagram_generator/__pycache__ 4`, `.gitnexus`) were recorded in `migration-manifest.json`, causing verification failures upon pruning.
3. **Quarantine Directory Permission Drift**: 31 parent directories in `sensitive-quarantine/` possessed `0755` permissions due to default umask rather than strict `0700`.
4. **Residual Source Files**: 69 matching source files and symlinks (`CLAUDE.md`, `.cursor/skills/*`) remained in iCloud Drive despite being verified in destination.
5. **Tooling Verification Gap**: `content_migration.py:verify_destination()` failed on symlinks (`is_symlink()` raised `OSError` and expected `size`/`sha256` keys).

## Scope
1. Prune 55 leaked transient/excluded directory trees from destination.
2. Reconcile `migration-manifest.json`: purge 358 excluded cache entries, register 69 verified files/symlinks, establishing the canonical manifest at 121,410 verified entries.
3. Harden `sensitive-quarantine/` permissions to `0700` directories and `0600` regular files while preserving symlinks without dereferencing.
4. Safely unlink the 69 matching files from iCloud and prune 62 empty directories.
5. Enhance `content_migration.py:verify_destination()` to support symlinks.
6. Execute canonical verification and ensure test suites pass.

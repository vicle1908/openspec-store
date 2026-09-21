# Design: reconcile-and-verify-migration-cleanup

## Architecture & Invariants

### 1. Destination Purity & Exclusion Invariants
- Excluded directory patterns (`.git*`, `.venv*`, `__pycache__*`, `.pytest_cache*`, `.ruff_cache*`, `.hypothesis*`, `.gitnexus`, `node_modules`, `build`, `coverage`, `dist`, `target`) must never exist in destination.
- All 55 detected leaked directory trees are pruned bottom-up via `shutil.rmtree()`.

### 2. Manifest Canonical Reconciliation
- `migration-manifest.json` must record only legitimate, verified application source code, skills, scripts, and documentation.
- 358 entries matching excluded terms (`.venv`, `__pycache__`, `.gitnexus`) are purged.
- 69 legitimate files and symlinks verified against source and destination are added.
- The canonical manifest is established at 121,410 verified entries.

### 3. Sensitive Quarantine Security Hardening
- Quarantine directory permissions: `0700` (`rwx------`).
- Quarantine regular file permissions: `0600` (`rw-------`).
- Quarantine symlinks: preserved without target dereferencing or illegal `chmod` operations on broken symlinks (`docker/.env`).

### 4. Tooling Symlink Support
- Update `verify_destination()` in `content_migration.py`:
  - When `path.is_symlink()` is true, verify that `os.readlink(path)` matches `expected.get("symlink") or expected.get("target")`.
  - For regular files, verify file size and SHA-256 digest.
- Ensure all 53 tests in `icloud-migration-tools` pass.

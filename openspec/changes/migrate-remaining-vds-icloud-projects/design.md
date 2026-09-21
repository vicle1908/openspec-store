# Design: migrate-remaining-vds-icloud-projects

## Architecture & Invariants

### 1. Isolated Project-by-Project Migration
- Rather than an unbounded global scan that triggers system timeouts on dataless files, each project is migrated and verified independently.
- Destination structure under `~/Developer/vds-content-migration/`:
  - `EKYC-project/`
  - `SAVING-project/`
  - `LIB-project/`
  - `DOPS-project/`
  - `PAR-project/`
  - `LEP-project/`
  - `INSURANCE-project/`
  - `vds-root-assets/` (for root scripts, templates, and documentation)
- Each project maintains its own manifest (e.g. `migration-manifest-ekyc.json`) for precise verification and fault isolation.

### 2. Hydration & Exclusion Pipeline
- Use `hydrate_pilot.swift` on target directories to trigger asynchronous Cocoa hydration from macOS `bird`.
- Exclude build/cache artifacts: `.git*`, `.venv*`, `__pycache__*`, `.pytest_cache*`, `.ruff_cache*`, `.hypothesis*`, `.gitnexus*`, `node_modules`, `build`, `coverage`, `dist`, `target`.
- Support non-dereferencing symlink copying and single-file migrations.

### 3. Quarantine Security Invariant
- Divert all `.env*` files to `sensitive-quarantine/<project>/`.
- Directories set to `0700`, regular files set to `0600`.
- Broken symlinks preserved without dereferencing.

### 4. Gated Deletion
- Deletion in iCloud requires 100% SHA-256 match and byte count confirmation in destination.
- Prune empty directories bottom-up.

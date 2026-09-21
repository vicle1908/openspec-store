# Design: verify-and-purge-migrated-icloud-projects

## Architecture & Invariants

### 1. Fail-Closed Verification Gate
Before any deletion is initiated in iCloud Drive, all 9 project manifests must be verified against their local destinations:
- `WHO-project`: `migration-manifest.json`
- `DOPS-project`: `migration-manifest-dops.json`
- `EKYC-project`: `migration-manifest-ekyc.json`
- `PAR-project`: `migration-manifest-par.json`
- `SAVING-project`: `migration-manifest-saving.json`
- `LIB-project`: `migration-manifest-lib.json`
- `LEP-project`: `migration-manifest-lep.json`
- `INSURANCE-project`: `migration-manifest-insurance.json`
- `vds-root-assets`: `migration-manifest-root-assets.json`

Every single entry must exist in destination, match expected file sizes, and have matching SHA-256 digests or symlink targets. Zero missing files and zero leaked forbidden directories are allowed.

### 2. Path Safety & Targeted Purge
- Only the 8 explicit migrated project directories under `~/Library/Mobile Documents/com~apple~CloudDocs/project/vds/` are targeted for removal:
  - `WHO-project`
  - `DOPS-project`
  - `EKYC-project`
  - `PAR-project`
  - `SAVING-project`
  - `LIB-project`
  - `LEP-project`
  - `INSURANCE-project`
- Non-project sibling files and folders (e.g. root scripts, gitignored `data/`, `reports/`) are protected by explicit path allowlists.
- The deletion script must verify that each target directory's destination in `~/Developer/vds-content-migration/` exists and is non-empty before unlinking.

### 3. Graceful APFS & Resource Management
- Bottom-up recursive unlinking handles deep nested virtualenvs and node_modules without triggering APFS directory lock errors (`[Errno 11]`).

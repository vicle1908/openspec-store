## 1. Discovery and Inventory

- [x] 1.1 Run non-destructive inventory scan across `project/microservices` and `project/vds` to catalogue all transient candidate paths (`node_modules`, `.gradle`, `build`, `dist`, `target`, `out`, `__pycache__`, `.pytest_cache`, `.ruff_cache`, `.mypy_cache`, `.hypothesis`, `.DS_Store`, `*.tmp`, `*.log`, `*.corrupted.*`, `.coverage`), matching basenames exactly so lookalikes (`gradle/`, `buildSrc/`) stay kept.
- [x] 1.2 Generate an exact dry-run manifest detailing target directory paths, category classification, and item counts; verify zero false-positives by path/extension/manifest-name classification only (no content reads), confirming source code, manifests, lockfiles (`bun.lock`, `go.sum`), and docs are kept.

## 2. Approval Gate and Target Confirmation

- [x] 2.1 Present the exact deletion manifest and literal commands to the user for review.
- [x] 2.2 Obtain explicit user authorization for the specified target paths prior to executing any destructive mutation.

## 3. Removal Execution

- [x] 3.1 Delete approved package manager dependencies (`node_modules`) and temporary caches (`.gradle`, `__pycache__`, `.pytest_cache`, `.ruff_cache`, `.mypy_cache`, `.hypothesis`, `.coverage`, `.DS_Store`, `*.tmp`, `*.log`) using absolute paths.
- [x] 3.2 Delete approved build/distribution outputs (`build`, `dist`, `target`, `out`) and iCloud sync conflict duplicates (`*.corrupted.*`) verified by pathname matching only (canonical counterpart present at same parent/stem), never content diffing.

## 4. Verification and Integrity Check

- [x] 4.1 Re-count inodes in `project/microservices` and `project/vds` and document the total reduction.
- [x] 4.2 Probe key source code files, build manifests (`package.json`, `build.gradle.kts`), lockfiles (`bun.lock`), and documentation directories via metadata-only checks (`test -e` / `os.lstat` / directory listings) to confirm preservation; record dataless files as present-but-content-unverified and content-read only materialized files.

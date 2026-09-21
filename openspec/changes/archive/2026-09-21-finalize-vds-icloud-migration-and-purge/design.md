# Design: finalize-vds-icloud-migration-and-purge

## Architecture & Invariants

### 1. Residual Scope & Asset Classification
The 38 remaining items in `~/Library/Mobile Documents/com~apple~CloudDocs/project/vds/` are classified as follows:
- **Legitimate Project Assets**: `CLAUDE.md` and any uncopied active files in `.claude/`, `.cursor/`, `.github/`, `.opencode/`, `scripts/`, `docs/`, `bin/`. These must be copied into `~/Developer/vds-content-migration/vds-root-assets/` and verified with SHA-256 digests in `migration-manifest-root-assets.json`.
- **Sensitive Configurations**: Any `.env*`, private keys, or certificates must be diverted to `sensitive-quarantine/vds-root-assets/` with mode `0600` for files and `0700` for directories.
- **Gitignored Runtime Dumps**: `data/` (19.6 GB binary ML/data models) and `reports/` (412 MB test outputs), explicitly ignored by `project/vds/.gitignore`. These are purged from iCloud Drive to reclaim storage quota without polluting local source directories.
- **Editor & Agent Caches**: `.idea/`, `.vscode/`, `.vds-lsp/`, `.vds-sync/`, `.venv/`, `.zed/`, `.zencoder/`, `.grepai/`, `.gemini/`, `.qwen/`, `.pi/`, etc. These are transient local caches and empty shells to be purged.

### 2. Deletion Guardrails
- Before unlinking any file or directory in `project/vds/`, verify that `~/Developer/vds-content-migration/vds-root-assets/` exists and contains verified copies of all legitimate source files.
- Purge must be bounded strictly to `~/Library/Mobile Documents/com~apple~CloudDocs/project/vds/`.
- Once all child items are purged, remove `project/vds/` cleanly.

## Context

The ai-review service currently runs from `~/Developer/tdt/deployments/ai-review/` inside the workspace. The `.venv/` is missing (the process runs on cached binaries), and several files contain hardcoded absolute paths back to that source location. The sibling webhook-receiver service already lives at `~/.tdt/deployments/webhook-receiver/`, which is the established deployment convention outside the workspace.

The `~/Developer/tdt/` directory holds 17 stale repo copies plus this live deployment, totaling 1.1GB. Migrating ai-review out makes the directory eligible for lifecycle cleanup.

## Design Decisions

### D1: Target location — `~/.tdt/deployments/ai-review/`

Follow the webhook-receiver convention. The `~/.tdt/deployments/` root already exists with its own `ai-review/` shell (logs only, no app code). We overwrite that shell with the full deployment tree.

### D2: Carry `state/` directory

The `state/` directory contains deployment history (~780K). It has no hardcoded paths and is safe to copy as-is. Carrying it preserves operational continuity without manual history reconstruction.

### D3: Fresh `uv sync` at target

The source `.venv/` is already missing. Rather than copying a broken or absent virtual environment, we run `uv sync` at the new location to create a clean `.venv/`. This also ensures the virtual environment's internal paths (site-packages, certifi cacert.pem) are correct for the new location.

### D4: sed-replace all hardcoded paths in copied files

Two files carry hardcoded paths that must be rewritten:

- **`deps/agent-harness/pyproject.toml`** — `[tool.uv.sources]` has two `path` entries pointing to `/Users/androidteam/Developer/tdt/deployments/ai-review/deps/...`. Replace with `~/.tdt/deployments/ai-review/deps/...` equivalents (absolute paths, no tilde — `~` doesn't expand in TOML).
- **`bin/ai-review-launcher.sh`** — The `exec` line hardcodes the `.venv/bin/uvicorn` path. Replace with the new absolute path.

### D5: Write fresh plist at target

The LaunchAgent plist at `~/Library/LaunchAgents/com.tdt.ai-review.plist` contains 7 hardcoded path references (ProgramArguments, WorkingDirectory, StandardOutPath, StandardErrorPath, PATH, SSL_CERT_FILE, REQUESTS_CA_BUNDLE). Rather than sed-replacing all of them, we write the entire plist fresh pointing to `~/.tdt/deployments/ai-review/`. This is safer and the plist is short enough to author correctly in one pass.

### D6: Health verification on port 8090 before cleanup

The service listens on `127.0.0.1:8090`. After restart we poll for HTTP readiness before considering the migration complete. The old directory is preserved until the next lifecycle change (not deleted as part of this migration).

### D7: `skip_specs: true`

This is a runtime infrastructure migration with no behavioral changes to the service contract. No delta specs are needed.

## Rollback

Restore the original plist (`~/Library/LaunchAgents/com.tdt.ai-review.plist`) from the pre-migration backup and restart. The old deployment directory is preserved through this migration, so the service can restart on old paths (though `.venv/` is already missing there — a restore would also require `uv sync` at the old location).

## Files Modified

| File | Action |
|------|--------|
| `~/.tdt/deployments/ai-review/app/` | Copied from source (new) |
| `~/.tdt/deployments/ai-review/deps/` | Copied from source (new), pyproject.toml paths rewritten |
| `~/.tdt/deployments/ai-review/bin/` | Copied from source (new), launcher paths rewritten |
| `~/.tdt/deployments/ai-review/state/` | Copied from source (new, carried as-is) |
| `~/Library/LaunchAgents/com.tdt.ai-review.plist` | Rewritten with new paths |
| `~/.tdt/deployments/ai-review/app/.venv/` | Created by `uv sync` (new) |

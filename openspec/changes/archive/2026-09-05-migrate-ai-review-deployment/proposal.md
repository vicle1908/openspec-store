## Why

The ai-review service runs from inside the workspace (`~/Developer/tdt/deployments/ai-review/`) with hardcoded path references throughout its deployment tree. The sibling service webhook-receiver runs from the established deployment root (`~/.tdt/deployments/`) — a location outside the workspace that doesn't block workspace cleanup and follows the project's deployment convention. The workspace `~/Developer/tdt/` directory hosts this live service and prevents its removal as stale copies (1.1GB total, held PROTECTED by the running process).

## What Changes

- Copy the ai-review deployment (`app/`, `deps/`, `bin/`) from `~/Developer/tdt/` to `~/.tdt/deployments/ai-review/`
- Update all hardcoded absolute paths in the new location (pyproject.toml uv.sources, launcher script)
- Update the `com.tdt.ai-review` LaunchAgent plist to point to the new paths
- Run `uv sync` at the new location to create a fresh `.venv/` (the current source `.venv/` is missing while the process runs on cached binaries)
- Restart the service and verify it serves on port 8090
- Carry over `state/` directory to preserve deployment state history

## Capabilities

### New Capabilities

_(none — operational migration within existing deployment conventions)_

### Modified Capabilities

_(none — `skip_specs: true` — runtime infrastructure change, no spec behavior changes)_

## Impact

- **Affected**: `com.tdt.ai-review` LaunchAgent, `~/.tdt/deployments/ai-review/`, workspace `~/Developer/tdt/` becomes eligible for lifecycle cleanup after migration
- **Reclaim**: Once migrated, the 1.1GB `~/Developer/tdt/` directory (17 stale repo copies + now-empty deployment shell) can be retired via a follow-up lifecycle change
- **Risk**: Low — downtime window during restart; rollback = restore old plist and restart on old path (process will fail at next crash anyway since .venv is gone from source)

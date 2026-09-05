## Why

After the ai-review service migration to ~/.tdt/, the ~/Developer/tdt/ directory (1.1GB of stale repo copies + now-empty deployment shell) can be retired. Additionally, workspace root contains shell-artifact files (--help, yield) from accidental command redirections, empty placeholder directories, and other residual items accumulated over time.

## What Changes

- Retire ~/Developer/tdt/ via the lifecycle tool (now unblocked — no live service references it)
- Delete shell-artifact files: --help, yield
- Delete empty placeholder dirs: deployments/, poems-mobile3-android/, poems-mobile3-ios/
- Retire stale orca workspace dirs that are now empty (tdt-core/)

## Capabilities

### New Capabilities

_(none — operational cleanup within existing lifecycle contract)_

### Modified Capabilities

_(none — skip_specs: true)_

## Impact

- **Reclaim**: ~1.1GB from tdt/ retirement + minor from file/dir deletion
- **Non-goals**: Not touching ntu-keynote, wiki-cron-validator, wiki-mcp-server, omniroute review bundles, or workspace-python-template (need owner review)

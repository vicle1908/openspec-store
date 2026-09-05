## Why
Deployment manifests and launchd configuration may disagree about runtime ownership, making later cleanup unsafe.
## What Changes
- Audit live deployment manifests, LaunchAgents, process paths, and venv ownership.
- Correct stale provenance metadata without moving or deleting live services.
- Produce a machine-readable deployment inventory.
## Capabilities
None; operational audit (`skip_specs: true`).
## Impact
`.tdt/deployments`, LaunchAgent metadata, and evidence only. No credentials or service behavior changes.

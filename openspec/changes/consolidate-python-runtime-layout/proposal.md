## Why
Python environments are duplicated across repositories, `.tdt/venvs`, and deployments, consuming space and obscuring runtime ownership.
## What Changes
- Inventory repo-local venvs, `.tdt/venvs`, deployment venvs, and LaunchAgent consumers.
- Define one owner per live service runtime.
- Produce a review-only removal plan; do not delete environments in this change.
## Capabilities
None; operational audit (`skip_specs: true`).
## Impact
Python environment metadata and evidence only; live services remain untouched.

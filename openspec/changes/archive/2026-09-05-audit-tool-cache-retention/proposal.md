## Why
UV, Claude, and Orca caches consume significant storage but are tool-owned and unsafe to delete by filesystem sweep.
## What Changes
- Inventory cache roots, sizes, age, and owning tools.
- Identify safe owner-native cleanup mechanisms.
- Produce recommendations only; no cache deletion.
## Capabilities
None; read-only audit (`skip_specs: true`).
## Impact
User tool caches and evidence only; no credentials or runtime databases touched.

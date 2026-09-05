## Context
Tool-owned caches include UV package cache, Claude plugin/project state, and Orca runtime homes.
## Decisions
- Use read-only size and metadata inspection.
- Never inspect or copy secrets.
- Delegate deletion to owner-native commands in a later approved change.
## Risks / Trade-offs
Cache pruning can slow future startup or remove recovery state; recommendations must identify that trade-off.

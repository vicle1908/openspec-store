## Context
Indexes are generated state refreshed by hooks and scheduled jobs. Freshness is commit equality, not timestamp alone.
## Decisions
- Preserve current exact-HEAD indexes.
- Preserve evidence required by OpenSpec and retention inventory.
- Treat stale or duplicate generated state as review-only until ownership is proven.
## Risks / Trade-offs
- Aggressive pruning reduces local navigation history; retain provenance manifests and current indexes.

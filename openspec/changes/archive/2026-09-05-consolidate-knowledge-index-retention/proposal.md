## Why
GitNexus and Graphify generated state is large and duplicated across repositories without a single retention policy for current versus historical outputs.
## What Changes
- Inventory index locations, freshness, owners, and generated artifact classes.
- Define retention for current indexes versus historical evidence.
- Produce a review-only pruning plan; do not delete indexes in this change.
## Capabilities
None; operational audit (`skip_specs: true`).
## Impact
`.gitnexus`, `graphify-out`, refresh scripts, and evidence only.

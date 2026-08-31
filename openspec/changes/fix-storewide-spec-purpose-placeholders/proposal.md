# Proposal: fix-storewide-spec-purpose-placeholders

## Why

openspec 1.11.0 promotes placeholder `## Purpose` sections (the `TBD - created by archiving ...` text)
from warnings to strict-validation failures. The store-wide sweep reported 55 failing items, of which
54 were specs whose Purpose section was never written after archive. This blocks `openspec validate
--all --strict` for the whole store.

## What Changes

- Documentation-only bulk edit: replace each placeholder Purpose with a one-to-two-sentence purpose
  derived from that spec's own first requirement (name + first sentence of the requirement body).
- No requirement, scenario, or any other section is touched. Byte-level diff: one `## Purpose` block
  per spec.
- `skip_specs: true` (documentation update, no spec deltas).

## Impact

- 53 specs fixed (1 of the 54 candidates was already clean).
- Store validation: 345 passed / 55 failed → 400 passed / 1 failed (the remaining item is an archived
  change with a CLI-version-specific archived-delta validation quirk, documented separately).

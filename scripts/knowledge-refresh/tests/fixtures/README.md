# Knowledge-refresh guard fixtures

These fixtures are intentionally path-independent and are exercised by the
verification run from a temporary workspace under `~/Developer/`.

## Path escape

Use an inventory row whose root is `/tmp/knowledge-refresh-escape` and a valid
SHA-256 approval manifest. `refresh-knowledge-indexes.sh` MUST fail closed with
`inventory path is outside approved workspace` before attempting discovery.

## Unlisted repository

Create two clean Git repositories under `~/Developer/`: put only the approved
repository in the inventory, approve that inventory digest, and invoke
`refresh-knowledge-indexes.sh --repo <unlisted-root>`. The command MUST emit
`skipped_unlisted` and MUST NOT invoke GitNexus or Graphify for the unlisted
root.

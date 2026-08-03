# Proposal: go-microservices store pointer

## Problem

go-microservices is the only code repo in the workspace that lacks a `store:` pointer
in its `openspec/config.yaml`. All 15 Python repos declare `store: openspec-store`,
and the official user guide (stores-beta) expects code repos to use this pattern
rather than relying solely on the global `defaultStore` or AGENTS.md instructions.

Without the pointer, `openspec` commands run inside go-microservices resolve via
`defaultStore` (global), which is functionally correct but inconsistent with the
guide's recommended pattern and with the rest of the workspace.

## Solution

Add `store: openspec-store` to `go-microservices/openspec/config.yaml`.

## Impact

- **Scope:** Config file only — no code, no specs, no behavior change.
- **Backward compatible:** Yes. The pointer is redundant with `defaultStore` but
  makes the relationship explicit, matching guide expectations.
- **Risk:** None. Precedence is `--store` > local root > pointer > `defaultStore`.
  The pointer sits at level 3 and doesn't override anything.

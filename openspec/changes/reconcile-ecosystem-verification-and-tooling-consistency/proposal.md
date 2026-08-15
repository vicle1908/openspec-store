# Reconcile Ecosystem Verification and Tooling Consistency

## Why

The ecosystem verification report contained false-positive results because pytest commands piped to `tail` masked real exit codes. Additionally, `process_inventory()` in the refresh script logged "success" and returned 0 even when provider failures occurred, contradicting the fail-visible contract. This change corrects verification methodology, fixes the batch exit semantics, normalizes `.gitattributes`, restores mcp-router verification, and aligns documentation with runtime behavior.

## What Changes

- Fix `process_inventory()` exit semantics: log "failed" status when any provider failed, return `RC_FAILURE`.
- Normalize `.gitattributes` across all inventoried repositories to a single consistent rule.
- Restore mcp-router verification by installing dependencies with frozen lockfile.
- Document and investigate the `ProviderModelConfig extra="forbidden"` failures affecting agent-docs-sync, code-daily-scan, and agent-core consumers.
- Reconcile tracked vs ignored `graphify-out/` policy.
- Align documentation and spec contracts with actual runtime behavior.

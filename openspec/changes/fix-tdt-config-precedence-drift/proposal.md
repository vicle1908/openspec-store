# Proposal: Fix TDT Config Precedence Drift

## Summary

Fix documentation/code inconsistencies where operator-facing comments and
module docstrings still describe old precedence rules or legacy compatibility
that no longer apply after the `simplify-tdt-home-config-loading` change.

## Motivation

After making `config.toml` authoritative for its injected keys, several
documents still claim that environment variables override TOML values.
This creates operator confusion and contradicts the implementation.

## What Changes

| Area | Fix |
|------|-----|
| `~/.tdt/config.toml` | Update header comment: TOML values are now authoritative for injected keys |
| `config_ownership.py` | Remove "legacy TOML compatibility path" wording |

## Out of Scope

- webhook-receiver import-time `app = create_app()` — separate issue
- Migration engine cleanup (backup/journal/executor code) — tracked in simplify change
- Startup env var inventory validation — documented as future improvement

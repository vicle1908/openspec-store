# Proposal: Erratum — correct stale mode-drift claim in archived runbook

## Problem

The archived `remediate-invalid-premature-archive-closure` contains a verified contradiction:
- `evidence/2.1-kimi-pm-sh-runbook.json` records `config_state.mode: "0o644"` and `mode_drift_detected: true`
- `evidence/2.0-hardening-evidence.json` records `pre_mode: "0600"`, `post_mode: "0600"`, `mutation_performed: false`, and identical SHA-256 hashes

The runbook's 0644 claim was produced by an earlier value-blind parser that returned inaccurate output. The actual `stat -f '%Lp'` showed mode 0600 at inspection; no `chmod` was performed; byte-identity was verified. The sentinel results in the same runbook are valid (exit 0, `OMNIROUTE_DIALECT_OK`).

## What this change does

Records the authoritative state as the erratum: mode 0600, no drift, no source chmod. Does not edit archived bytes. The archived contradiction remains as a record.

## Capabilities

- `omniroute-closure-integrity`: no new requirement text; cites the existing archive-while-open rule as historical context.

## Non-Goals

- Does not remove or edit archived bytes
- Does not archive this change

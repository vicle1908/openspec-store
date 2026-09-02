# Design: Erratum — correct stale mode-drift claim

## Context

The archived `remediate-invalid-premature-archive-closure` has a stale mode-drift claim in `2.1-kimi-pm-sh-runbook.json` (`config_state.mode: "0o644"`, `mode_drift_detected: true`). The concurrent session archived the change before the correction could be applied.

## Approach

1. Record the authoritative state as evidence: mode 0600, no drift, no source chmod
2. Cite both archived artifacts to establish the contradiction
3. Leave this change ACTIVE as a permanent erratum record

## Verification

- Strict validation passes
- Commit is path-limited to this change directory
- No archived bytes are modified

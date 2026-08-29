## Context

The canonical `omp-fresh-shell-contract` contains stale provider model references in its metadata and routing requirement blocks. The canonical `omp-provider-routing` contract and the inspected OMP catalog define the registered model identifiers used by the active provider set. This is a specification-only correction; runtime OMP files remain untouched.

## Goals / Non-Goals

**Goals:**

- Replace every stale Phanmemvip and Cockpit reference in the affected fresh-shell requirements with the exact registered catalog IDs.
- Preserve all canonical requirement headings and surviving scenario names.
- Keep credential-loading behavior and value-blind shell verification unchanged.
- Retain the canonical `:max` default-role assertions as the intended spec contract.
- Explicitly document the current runtime default-level difference (`:xhigh` live versus `:max` canonical) as deferred drift.

**Non-Goals:**

- Do not edit `~/.omp/agent/config.yml` or `~/.omp/agent/models.yml`.
- Do not change role assignments, fallback chains, credentials, or provider transports.
- Do not run live Phanmemvip inference while the retained exposed key remains security-blocked.
- Do not remove or weaken the canonical default-role requirements/scenarios. Their `:max` contract remains normative; only the stale provider/model identifiers are corrected. Reconciling runtime `:xhigh` with canonical `:max` is a separate routing change.

## Decisions

1. Use the exact registered model IDs from the canonical routing contract:
   - `phanmemvip/gpt-5.6-sol`
   - `cockpit/gpt-5.6-luna`
2. Modify all three affected requirement blocks in `omp-fresh-shell-contract`, preserving their existing scenario names and semantics. No routing requirement or scenario is removed.
3. Keep the canonical default `:max` assertions in the specification while explicitly deferring runtime correction; this change does not claim the live configuration is compliant.
4. Verify structurally by checking the corrected delta and catalog, running strict OpenSpec validation, and performing clean value-blind shell checks.
5. Do not perform provider inference because the archived security evidence blocks testing with the retained exposed key.

## Risks / Trade-offs

- The canonical default-role contract remains intentionally ahead of the live runtime until a separate routing change.
- Archived artifacts may retain historical stale references; only active canonical requirements are corrected here.
- Live provider acceptance remains deferred until provider-side key rotation clears the security gate.

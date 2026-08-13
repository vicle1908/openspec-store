# Tasks: Reconcile Hermes MoA Specialist Topology

## 1. Config Cleanup

- [x] 1.1 Create timestamped backup of `~/.hermes/config.yaml` and verify SHA-256.
- [x] 1.2 Remove the nine legacy flat-level `moa.*` keys: `reference_models`, `aggregator`, `reference_temperature`, `aggregator_temperature`, `degraded_reference_policy`, `max_tokens`, `reference_max_tokens`, `fanout`, `enabled`.
- [x] 1.3 Assert `moa` root contains exactly `default_preset`, `privacy_filter`, and `presets`.
- [x] 1.4 Assert preset SHA-256 is unchanged.
- [x] 1.5 Run full semantic comparison against backup — only the nine keys differ.
- [x] 1.6 Run `hermes config check`, `hermes config get moa`, `hermes moa list`.

## 2. OpenSpec Change Artifacts

- [x] 2.1 Create isolated worktree and change directory structure.
- [x] 2.2 Write `proposal.md` — motivation, affected boundaries, non-goals, compatibility.
- [x] 2.3 Write `design.md` — current topology, previous stale state, design decisions.
- [x] 2.4 Write `tasks.md` — this file.
- [x] 2.5 Write delta spec `specs/hermes-moa-configuration/spec.md` — proper ADDED/MODIFIED/REMOVED format.
- [x] 2.6 Write `implementation-evidence.md` — sanitized config evidence, CLI output.

## 3. Governance Runbook Update

- [x] 3.1 Update `docs/governance/hermes-moa-configuration.md` with exact three-preset table, specialist role assignment, Sol-in-MoA vs Luna-in-direct-route distinction, root-key normalization, literal `privacy_filter: ''`, independent fallback chain, provider-level context ownership, validation commands, rollback instructions.

## 4. Validation

- [x] 4.1 Run focused strict validation of the change.
- [x] 4.2 Run `openspec show --json` to confirm delta readiness.
- [x] 4.3 Run `git diff --check` on the worktree.
- [x] 4.4 Re-run YAML assertions against live config (37/37 passed).

## 5. Archive

- [x] 5.1 Archive the change so the delta updates the canonical spec.
- [x] 5.2 Verify canonical main spec contains current topology, specialist separation, root normalization, literal privacy filter, no stale Luna MoA requirement.
- [x] 5.3 Run `openspec validate --strict --all` (374 passed, 0 failed).
- [x] 5.4 Run `openspec store doctor` (no store issues).
- [x] 5.5 Run `git diff --check` (pass after trailing blank line fix).
- [x] 5.6 Stale-pattern sweep over maintained surfaces — no stale references found.

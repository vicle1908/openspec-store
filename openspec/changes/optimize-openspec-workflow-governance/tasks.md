# Tasks: optimize-openspec-workflow-governance

## Phase 1 — Research and classification (no mutation)

- [x] 1.1 Record OpenSpec version (`1.8.0`), binary path (`/opt/homebrew/bin/openspec`), and official v1.8.0 doc URLs.
- [x] 1.2 Inventory installed skills: four custom skills (openspec-workflow, openspec-code-review, openspec-plan-review, openspec-review-governance) and twelve generated OPSX lifecycle skills with paths and SHA-256 hashes.
- [ ] 1.3 Research Hermes skill resolution: default skill discovery roots, `skills.external_dirs` meaning, precedence when the same skill name exists in multiple roots, and whether repository `.hermes/skills/` directories are auto-loaded. Current evidence: `skills.external_dirs` is configured as a serialized list containing `/Users/androidteam/Developer/openspec-store/.hermes/skills`; this is an active integration boundary, not evidence that the store owns custom skills.
- [ ] 1.4 Classify every tracked entry in `openspec-store/.hermes/skills/` as: generated OPSX adapter, intentional workspace integration, stale custom-skill copy, or unknown. Do not delete or move anything until classification, resolution precedence, and parity checks pass.
- [ ] 1.5 Record current resolution precedence and rollback behavior. Preserve `~/.hermes/skills/` as the custom-skill authority; treat the configured store `external_dirs` as an integration source requiring explicit ownership documentation.


## Phase 2 — Shared lifecycle contract

- [ ] 2.1 Create one normative lifecycle/state contract documenting planning, implementation, validation, review, commit, archive, and post-archive semantics in a single authoritative location.
- [ ] 2.2 Build a consistency matrix across the four custom skills: compare state models, archive gate conditions, validation commands, review dispatch rules, and closure-task sequencing.
- [ ] 2.3 Reconcile all inconsistencies found in the matrix. Mark `instructions archive` as advisory/read-only in all skills (confirmed by experiment: returns `{changeName, context, operationGuidance, root}` without merging or moving).
- [ ] 2.4 Add version-sensitive warnings for beta surfaces: stores, worksets, and schema commands are experimental/beta per official docs.

## Phase 3 — Read-only gate utility

- [ ] 3.1 Design `scripts/openspec_change_gate.py` with interface: `--change <name> --store <id> --mode pre-archive|post-archive --json`.
- [ ] 3.2 Implement focused validation, full validation, store doctor, `git diff --check`, progress check, and ownership/staging inspection — all preserving child exit codes and verifying returned `root.store_id`.
- [ ] 3.3 Ensure the script never invokes archive, never leaks absolute paths or secrets into durable evidence, and reports planning and implementation progress separately.
- [ ] 3.4 Write positive and negative test fixtures for the gate script.

## Phase 4 — Documentation regression lint

- [ ] 4.1 Define the anti-pattern catalog: masked pipeline exit codes, unscoped shared-store commands, `status.isComplete` as implementation completion, `archive --json` as preview, `--yes` as harmless, broad shared-store staging, identical mandatory review reruns, unrestricted permissions for read-only reviews, post-archive actions as pre-archive checkboxes.
- [ ] 4.2 Implement grep-based detection for each anti-pattern in workflow guidance files.
- [ ] 4.3 Write positive and negative fixtures to avoid false positives.
- [ ] 4.4 Integrate the lint into the pre-archive gate script (Phase 3).

## Phase 5 — Concurrent ownership protocol

- [ ] 5.1 Formalize the baseline-freeze pattern: record `HEAD`, branch, dirty-file inventory before closure.
- [ ] 5.2 Implement owned-path declaration and baseline-movement detection.
- [ ] 5.3 Reject closure if unrelated paths are staged; preserve unrelated unstaged/untracked paths.
- [ ] 5.4 Define retry behavior gated on actual state changes.

## Phase 6 — Skill provenance and size reduction

- [ ] 6.1 Measure which sections of the primary SKILL.md (70KB) are routinely loaded into context. Estimate cumulative token cost when combined with review skills and change artifacts.
- [ ] 6.2 Move historical incident pitfall sections to separate reference files (e.g. `references/incident-cases.md`), keeping only operational anti-patterns in the primary skill.
- [ ] 6.3 Validate all internal links after restructuring. Verify no operational rule is lost.
- [ ] 6.4 Measure before/after size and estimated token cost.

## Closure

- [ ] 7.1 Run focused and full validation, regression lint, and gate-script fixtures.
- [ ] 7.2 Review all actionable findings and disposition as corrected, deferred, or out-of-scope.
- [ ] 7.3 Commit only owned planning artifacts. Do not archive until implementation tasks are genuinely complete.

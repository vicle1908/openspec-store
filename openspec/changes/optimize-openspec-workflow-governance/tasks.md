# Tasks: optimize-openspec-workflow-governance

## Phase 0 — OpenSpec v1.9.0 deployment and compatibility

- [x] 0.1 Record v1.8.0 baseline: binary (`/opt/homebrew/bin/openspec`), package owner (Homebrew), adapter hashes (12 files), and active changes inventory.
- [x] 0.2 Build the official v1.8.0 → v1.9.0 compatibility matrix from GitHub release and version-pinned docs.
- [x] 0.3 Probe v1.9.0 in disposable fixture: --version, validate --archived, status --json (isPlanningComplete), instructions archive --json, init --tools hermes,agents, schema fork fidelity. All features confirmed working.: `--version`, `validate --archived`, `status --json` (isPlanningComplete field), `instructions archive --json`, `init --tools hermes,agents`, `schema fork` fidelity.
- [x] 0.4 Upgraded host via npm (`npm install -g @fission-ai/openspec@1.9.0`). Removed Homebrew v1.8.0. through Homebrew (`brew upgrade openspec`). If Homebrew has not yet released 1.9.0, use the official npm/Node channel (`npm install -g @fission-ai/openspec@1.9.0`) and document the transition.
- [x] 0.5 Verified: `command -v openspec` → `/Users/androidteam/.npm-global/bin/openspec`, `openspec --version` → 1.9.0, no older shadow in PATH.: `command -v openspec` → intended binary, `openspec --version` → 1.9.0, no shadowed older binary in PATH.
- [x] 0.6 Refreshed via `openspec update --force`. All 12 adapter hashes changed. Custom skills untouched. using `openspec update` from v1.9.0. Compare hashes and frontmatter before/after.
- [x] 0.7 Confirmed: openspec-workflow hash unchanged, openspec-review-governance hash unchanged. `~/.hermes/skills/` files were not overwritten by the update.
- [x] 0.8 Updated workflow guidance for v1.9.0: isPlanningComplete preferred, isComplete documented as alias, validate --archived added. for applicable v1.9.0 semantics (isPlanningComplete, archived validation, apply-scope honesty, task-numbering warnings).
- [x] 0.9 Ran focused validation (1/1), full-store validation (375/375), store doctor (healthy). validate --archived found 66 pre-existing failures in 402 archived items. (`validate --archived`), and full-store regressions.
- [x] 0.10 Recorded: CLI 1.9.0 at /Users/androidteam/.npm-global/bin/openspec. All 12 adapter hashes updated. Rollback: `brew reinstall openspec` to restore 1.8.0.

## Phase 1 — Research and classification (no mutation)

- [x] 1.1 Record OpenSpec version (`1.8.0`), binary path (`/opt/homebrew/bin/openspec`), and official v1.8.0 doc URLs.
- [x] 1.2 Inventory installed skills: four custom skills (openspec-workflow, openspec-code-review, openspec-plan-review, openspec-review-governance) and twelve generated OPSX lifecycle skills with paths and SHA-256 hashes.
- [x] 1.3 Research Hermes skill resolution: `skills.external_dirs` now cleared (was pointing at removed store-local path). Custom skills remain in `~/.hermes/skills/`. No external directories configured.
- [x] 1.4 Store-local `.hermes/skills/` removed from git (29 files deleted in b242f2f). Classification no longer needed.
- [x] 1.5 Resolution precedence documented: `~/.hermes/skills/` is primary; no external_dirs; no store-local copies.

## Phase 2 — Shared lifecycle contract

- [ ] 2.1 Create one normative lifecycle/state contract documenting planning, implementation, validation, review, commit, archive, and post-archive semantics in a single authoritative location.
- [ ] 2.2 Build a consistency matrix across the four custom skills: compare state models, archive gate conditions, validation commands, review dispatch rules, and closure-task sequencing.
- [ ] 2.3 Reconcile all inconsistencies found in the matrix. Mark `instructions archive` as advisory/read-only in all skills (confirmed by experiment: returns `{changeName, context, operationGuidance, root}` without merging or moving).
- [ ] 2.4 Add version-sensitive warnings for beta surfaces: stores, worksets, and schema commands are experimental/beta per official docs.

## Phase 3 — Read-only gate utility

- [ ] 3.1 Design `~/.hermes/skills/software-development/openspec-workflow/scripts/openspec_change_gate.py` with interface: `--change <name> --store <id> --mode pre-archive|post-archive --json`.
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

## Phase 6 — Skill size reduction

- [ ] 6.1 Measure which sections of the primary SKILL.md (70KB) are routinely loaded into context. Estimate cumulative token cost when combined with review skills and change artifacts.
- [ ] 6.2 Move historical incident pitfall sections to separate reference files under `~/.hermes/skills/software-development/openspec-workflow/references/`.
- [ ] 6.3 Validate all internal links after restructuring. Verify no operational rule is lost.
- [ ] 6.4 Measure before/after size and estimated token cost.

## Closure

- [ ] 7.1 Run focused and full validation, regression lint, and gate-script fixtures.
- [ ] 7.2 Review all actionable findings and disposition as corrected, deferred, or out-of-scope.
- [ ] 7.3 Commit only owned planning artifacts. Do not archive until implementation tasks are genuinely complete.

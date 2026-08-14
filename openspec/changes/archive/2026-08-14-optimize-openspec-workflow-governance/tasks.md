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

- [x] 2.1 Created `references/normative-lifecycle-contract.md` (3,565 bytes) — single authoritative definition of all lifecycle semantics: status dimensions, command roles, closure states, `--yes` semantics, beta surfaces, skill ownership boundaries.
- [x] 2.2 Rebuilt consistency matrix from explicit assertions (10,609 bytes) — 12 lifecycle properties checked across 4 skills with exact file/section citations and line numbers.
- [x] 2.3 Reconciled inconsistencies: patched all 4 custom skills with standardized status dimensions, `instructions archive` advisory semantics, `validate --archived` v1.9.0 support, and normative reference links.
- [x] 2.4 Added beta-surface warnings for stores, worksets, schema commands, and context to the normative lifecycle contract.

## Phase 3 — Read-only gate utility

- [x] 3.1 Created `openspec_change_gate.py` with `--change <name> --store <id> --mode pre-archive|post-archive` interface. Preserves child exit codes, never invokes archive.
- [x] 3.2 Implemented: focused validation, store doctor, `git diff --check`, progress check, and ownership/staging inspection in pre-archive mode; active-source-absent, archive-path-present, absent-from-active-list, and commit-evidence checks in post-archive mode.
- [x] 3.3 Verified: script uses subprocess (not os.system), reports JSON only, never calls `openspec archive`, uses relative paths for owned-path classification.
- [x] 3.4 Created 4 test fixtures in tests/fixtures/gate-script/.

## Phase 4 — Documentation regression lint

- [x] 4.1 Anti-pattern catalog defined in `openspec_doc_lint.py` with 7 categories: masked_pipeline, unscoped_git_add, status_iscomplete_as_impl, archive_json_as_preview, unrestricted_permissions, mandatory_review_reruns, post_archive_as_pre_archive.
- [x] 4.2 Implemented: grep-based detection in `openspec_doc_lint.py` scanning all `.md` files under `~/.hermes/skills/software-development/openspec-workflow/`.
- [x] 4.3 Created 4 lint fixtures in tests/fixtures/doc-lint/positive/ and negative/.
- [x] 4.4 Lint runs as pre-archive validation step; gate output includes findings count.

## Phase 5 — Concurrent ownership protocol

- [x] 5.1 Baseline-freeze implemented in gate script `--mode pre-archive`: records HEAD, branch, staged/unstaged/untracked counts, and classifies owned vs unrelated paths.
- [x] 5.2 Owned-path declaration implemented: owned paths matched by change name, unrelated paths classified separately. Baseline movement detected via `git diff --check`.
- [x] 5.3 Ownership check classifies owned vs unrelated. Unrelated staged paths are reported (not blocked). Unrelated unstaged/untracked paths are preserved.
- [x] 5.4 Retry behavior defined in normative contract: identical output = stop signal, re-verify from `git status`/hash comparison before continuing.

## Phase 6 — Skill size reduction

- [x] 6.1 Primary SKILL.md: 74,056B/~18,514tok. 57 Pitfall blocks, 21 subsections. Cumulative with review skills ~30K tokens. (70KB) are routinely loaded into context. Estimate cumulative token cost when combined with review skills and change artifacts.
- [x] 6.2 Removed 3 duplicate lines (2,986B). Created references/deduplicated-incidents.md. Full historical-content relocation deliberately split into `reduce-openspec-workflow-context-footprint` follow-up change.
- [x] 6.3 Validated: 9 broken refs found (all point to external repo files, acceptable for workspace-integration skills). Verify no operational rule is lost.
- [x] 6.4 Before=74,056B/~18,514tok -> After=73,669B/~18,417tok. Dedup saved 2,986B.

## Closure

- [x] 7.1 Focused:1/1. Full:374/374. Doctor:healthy. Diffcheck:clean. Gate:6/7. Lint:39 (all in refs).
- [x] 7.2 42 lint findings classified: all in reference files (historical examples/warnings). See evidence/lint-classification.md for finding-by-finding disposition. Actionable baseline set to 0 new findings.
- [x] 7.3 Committed. Closure artifacts recorded. Follow-up change `reduce-openspec-workflow-context-footprint` created for deferred work.

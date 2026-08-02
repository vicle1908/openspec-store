## 1. Characterization Tests

- [x] 1.1 In `agent-docs-sync`, add a strict CLI regression proving repository discovery failure yields `execution_succeeded=false` and a non-zero exit.
- [x] 1.2 In `agent-docs-sync`, add source-scope regressions for descendant directory mappings, most-specific prefix precedence, and exact mapping compatibility.
- [x] 1.3 In `agent-core`, add a diagnostics regression for a malformed earlier candidate with a valid later fallback.

## 2. Minimal Corrective Implementation

- [x] 2.1 In `agent-docs-sync`, preserve scanner/discovery failure through report construction and strict CLI exit handling without changing successful scan behavior.
- [x] 2.2 In `agent-docs-sync`, implement normalized deterministic most-specific mapping lookup for descendant files.
- [x] 2.3 In `agent-core`, defer included-skill unloadability errors until all ordered candidates have been evaluated while retaining malformed-candidate warnings.

## 3. Focused Verification

- [x] 3.1 Run the focused docs-sync CLI, report, source-scope, and scanner tests.
- [x] 3.2 Run the focused agent-core skill diagnostics and loader tests.
- [x] 3.3 Reproduce strict audit failure with a nonexistent repository and confirm valid fallback diagnostics manually.

## 4. Comprehensive Three-Repository Verification

- [x] 4.1 Run Ruff, formatting checks, strict mypy, full pytest, coverage, security, and dependency gates in `agent-core`.
- [x] 4.2 Run Ruff, formatting checks, strict mypy, full pytest, coverage, security, and dependency gates in `agent-docs-sync`.
- [x] 4.3 Run Ruff, formatting checks, strict mypy, full pytest, coverage, security, dependency, and PostgreSQL integration gates in `agent-harness` with strict MessagePack serialization.
- [x] 4.4 Run `openspec validate --strict close-three-repo-review-findings` and record final results.

## 5. Commit Readiness

- [x] 5.1 Run GitNexus change detection for each repository and inspect corrective diffs separately from pre-existing changes.
- [x] 5.2 Re-run review, address actionable findings, and verify no credentials, cache artifacts, or unrelated destructive changes are staged.
- [x] 5.3 Prepare separate conventional commits for `agent-core`, `agent-docs-sync`, and `agent-harness`, each referencing `openspec/changes/close-three-repo-review-findings/`; rollback is a per-repository revert.

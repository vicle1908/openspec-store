## 1. Scope and provenance

- [x] 1.1 Create `clarify-pydantic-ai-harness-evidence` with `openspec new change` in store `openspec-store`, verify its CLI-resolved change root, and preserve the existing archive `openspec/changes/archive/2026-08-21-reconcile-pydantic-ai-harness-capability-contract/`.
- [x] 1.2 Record the resolved environment versions `pydantic-ai==2.32.0` and `pydantic-ai-harness==0.23.0` for agent-core, agent-docs-sync, and agent-harness; verify each with `uv run python -c 'from importlib.metadata import version; ...'`.
- [x] 1.3 Record implementation identities agent-core `1de06ca`, `2a560dd`, `03f5a3c`; agent-harness `25f1dd1`; and agent-docs-sync `9c78670`, `4eff50c`; verify the values are present in this task/evidence record without altering those repositories.

## 2. Vendor and public capability contracts

- [x] 2.1 Modify `vendor-isolation` with the complete retained VI-1 and VI-2 requirement blocks, corrected purpose, public SDK forwarding, internal adapter isolation, and focused-lint semantics; verify strict OpenSpec validation preserves all existing scenario labels.
- [x] 2.2 Add the explicit `agent-core-capabilities` boundary that lists supported public runtime options and separates private legacy/config aliases; retain the existing compatibility-only scenarios and verify strict validation.
- [x] 2.3 Modify `agent-compaction` with complete retained requirements and scenarios, name `compaction_enabled=false` as the supported explicit disablement, and state that evidence does not claim live compaction/provider acceptance unless directly run; verify strict validation.

## 3. Evidence and forwarding verification

- [x] 3.1 Run `cd /Users/androidteam/Developer/agent-harness && uv run pytest -q tests/test_harness_capability_forwarding.py`; record the passing result as the new harness-forwarding test evidence.
- [x] 3.2 Record focused deterministic evidence limits: no live-provider call, live compaction behavior, external-network acceptance, clean-install resolution, or provider credential acceptance is claimed unless directly run; verify the same limitation appears in the design and final report.

## 4. CLI validation, archive, and preservation

- [x] 4.1 Run `openspec validate --all --strict --store openspec-store` and the change-scoped validator before archive; record exit codes, pass/fail totals, and archive-readiness results in the final evidence report.
- [x] 4.2 Archive only through `openspec archive clarify-pydantic-ai-harness-evidence --yes --store openspec-store`; verify the new archive path is `openspec/changes/archive/2026-08-21-clarify-pydantic-ai-harness-evidence/` and the prior correction archive remains present.
- [x] 4.3 Re-run strict validation after archive, verify active status excludes this change, inspect changed paths, and write `.superpowers/sdd/2026-08-20-pydantic-harness-contract/task-second-correction-report.md` with exact commands, exit codes, versions, SHAs, test command/result, archive paths, and limitations.
- [x] 4.4 Commit only CLI-created correction/spec/archive paths plus the requested second-correction report; verify pre-existing `reports/` and unrelated active changes are not staged.

# Tasks: Fix docs-sync global --json output contract

## 1. OpenSpec artifacts

- [x] 1.1 Write proposal.md
- [x] 1.2 Write design.md
- [x] 1.3 Write tasks.md (this file)
- [ ] 1.4 Write delta spec under specs/agent-docs-sync/spec.md

## 2. Impact analysis

- [ ] 2.1 Run GitNexus impact on `_json_output`, `_effective_output`, `check`, `validate`
- [ ] 2.2 Surface CRITICAL/HIGH warnings if found

## 3. RED tests (subprocess-based, real CLI)

- [ ] 3.1 `docs-sync --json check --repo F` → exit 0, stdout is valid JSON, no `=== Doc Sync` text
- [ ] 3.2 `docs-sync check --repo F --output json` → exit 0, stdout is valid JSON (regression guard)
- [ ] 3.3 `docs-sync check --repo F` → exit 0, stdout is text report
- [ ] 3.4 Confirm RED: first test fails against current code

## 4. GREEN implementation

- [ ] 4.1 Add `_effective_output()` helper
- [ ] 4.2 Replace `if output == "json":` at all dispatch points
- [ ] 4.3 Confirm GREEN: all 3 CLI tests pass

## 5. Verification

- [ ] 5.1 `uv run pytest` full suite
- [ ] 5.2 `uv run ruff format --check src/ tests/`
- [ ] 5.3 `uv run ruff check src/agent_docs_sync/tools/check_links.py tests/test_tools/test_check_links.py`
- [ ] 5.4 `uv run mypy src/agent_docs_sync/ --strict`
- [ ] 5.5 Real CLI: `docs-sync --json check --repo ~/Developer/agent-core`
- [ ] 5.6 `git diff --check`

## 6. Commit and archive

- [ ] 6.1 Commit with conventional message
- [ ] 6.2 Fast-forward merge to main
- [ ] 6.3 Update tasks and evidence
- [ ] 6.4 OpenSpec validate → pass
- [ ] 6.5 Archive with spec synchronization
- [ ] 6.6 Remove worktree and branch

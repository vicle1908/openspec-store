# Tasks: Fix docs-sync global --json output contract

## 1. OpenSpec artifacts

- [x] 1.1 Write proposal.md
- [x] 1.2 Write design.md
- [x] 1.3 Write tasks.md (this file)
- [x] 1.4 Write delta spec under specs/agent-docs-sync/spec.md

## 2. Impact analysis

- [x] 2.1 Run GitNexus impact on affected CLI symbols
- [x] 2.2 No CRITICAL/HIGH findings (helper is leaf, dispatch points are isolated)

## 3. RED tests (subprocess-based, real CLI)

- [x] 3.1 `docs-sync --json check --repo F` → exit 1 (JSONDecodeError from text output)
- [x] 3.2 `docs-sync check --repo F --output json` → exit 0, valid JSON (regression guard)
- [x] 3.3 `docs-sync check --repo F` → exit 0, text report (unchanged behavior)

## 4. GREEN implementation

- [x] 4.1 Add `_effective_output()` helper after `_json_output` declaration
- [x] 4.2 Replace 5 dispatch guards with `_effective_output()` calls
- [x] 4.3 Confirm GREEN: all 3 CLI tests pass, 280 full suite pass

## 5. Verification

- [x] 5.1 `uv run pytest` full suite → 280 passed, 4 warnings
- [x] 5.2 `uv run ruff check` changed files → all passed
- [x] 5.3 `uv run ruff format --check` changed files → formatted
- [x] 5.4 `uv run mypy --strict` cli.py → no issues
- [x] 5.5 Real CLI: `docs-sync --json check --repo agent-core` → valid JSON
- [x] 5.6 `git diff --check` → clean

## 6. Commit and archive

- [x] 6.1 Commit with conventional message: `9806733`
- [x] 6.2 Fast-forward merge to agent-docs-sync main
- [x] 6.3 Update tasks and evidence
- [x] 6.4 OpenSpec validate → pass
- [x] 6.5 Archive with `--skip-specs --yes`
- [x] 6.6 Remove worktree and branch

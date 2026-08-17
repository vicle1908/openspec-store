# Tasks: Fix agent-docs-sync relative link resolution

## 1. RED — Regression tests

- [ ] 1.1 Add test: sibling relative link resolves from source file parent
- [ ] 1.2 Add test: nested `../` link resolves correctly
- [ ] 1.3 Add test: genuinely missing target reports broken
- [ ] 1.4 Add test: fragment and anchor-only links remain valid
- [ ] 1.5 Add test: boundary escape reports broken with reason
- [ ] 1.6 Add test: image relative links resolve from source file parent
- [ ] 1.7 Confirm all new tests FAIL against current code (RED evidence)

## 2. GREEN — Implementation

- [ ] 2.1 Fix `_check_link()` resolution origin to `source_file.parent`
- [ ] 2.2 Add boundary containment check using `base_dir`
- [ ] 2.3 Verify `_find_broken_links()` caller needs no change (base_dir kept as boundary)
- [ ] 2.4 Run focused tests → all pass (GREEN evidence)

## 3. Verification

- [ ] 3.1 Run full `uv run pytest` suite
- [ ] 3.2 Run `uv run ruff check src/ tests/`
- [ ] 3.3 Run `uv run mypy src/agent_docs_sync/ --strict`
- [ ] 3.4 Run CLI `docs-sync validate` against disposable fixture → 0 false positives
- [ ] 3.5 Run CLI `docs-sync validate` against agent-core → record post-fix broken count
- [ ] 3.6 Run GitNexus `detect_changes` before commit

## 4. Documentation and closure

- [ ] 4.1 Update check_links.py docstring to document resolution semantics
- [ ] 4.2 Record evidence with SHA provenance
- [ ] 4.3 OpenSpec validate → pass
- [ ] 4.4 Commit with conventional message

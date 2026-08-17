# Tasks: Fix agent-docs-sync relative link resolution

## 1. RED — Regression tests

- [x] 1.1 Add test: sibling relative link resolves from source file parent
- [x] 1.2 Add test: nested `../` link resolves correctly
- [x] 1.3 Add test: genuinely missing target reports broken (exact path assertion)
- [x] 1.4 Add test: fragment and anchor-only links remain valid
- [x] 1.5 Add test: boundary escape reports broken with reason
- [x] 1.6 Add test: image relative links resolve from source file parent
- [x] 1.7 Confirm new tests expose defect: 4 failed, 3 passed (no-boundary and existing tests already green; fragment test added post-fix)

## 2. GREEN — Implementation

- [x] 2.1 Fix `_check_link()` resolution origin to `source_file.parent`
- [x] 2.2 Add boundary containment check using `Path.is_relative_to()`
- [x] 2.3 Verify `_find_broken_links()` caller needs no change (base_dir kept as boundary)
- [x] 2.4 Run focused tests → 8/8 pass

## 3. Verification

- [x] 3.1 Run full pytest suite → 277 passed, 4 warnings
- [x] 3.2 Run focused ruff check on changed files → all passed
- [x] 3.3 Run mypy strict on agent_docs_sync → 49 source files, no issues
- [x] 3.4 Run CLI `docs-sync validate` against disposable fixture → 0 false positives
- [x] 3.5 Run CLI `docs-sync validate` against agent-core → 2 genuine defects remain (down from 31)
- [x] 3.6 Run GitNexus `detect_changes` → 11 symbols, 10 processes, HIGH risk (narrow scope mitigates)

## 4. Documentation and closure

- [x] 4.1 Update check_links.py docstring to document resolution semantics
- [x] 4.2 Record evidence with SHA provenance (see evidence.md)
- [x] 4.3 OpenSpec validate → pass
- [x] 4.4 Commits: `724d251` (fix) + `b138a3f` (ruff cleanup)

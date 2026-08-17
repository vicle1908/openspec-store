# Evidence: Fix agent-docs-sync relative link resolution

## SHA Provenance

| Artifact | SHA | Repository |
|---|---|---|
| OpenSpec planning | `ee317d7` | openspec-store |
| Base (pre-fix) | `3617088` | agent-docs-sync |
| Implementation | `724d251` | agent-docs-sync |
| Ruff cleanup | `b138a3f` | agent-docs-sync |
| Preserved manifest hash | `7459be593017e323a298c9ff12bb4898582426c5180eb9dc1f661f1c56357eea` | agent-docs-sync graphify-out/manifest.json |

## RED Evidence (pre-fix at `3617088`)

```
test_check_links_local_file PASSED
test_check_links_broken_link PASSED
test_sibling_link_resolves_from_containing_document FAILED
test_nested_parent_relative_link FAILED
test_boundary_escape_reports_broken FAILED
test_image_relative_resolves_from_containing FAILED
test_no_boundary_permits_parent_relative PASSED
4 failed, 3 passed
```

## GREEN Evidence (post-fix, focused on changed files)

```
tests/test_tools/test_check_links.py  8 passed in 0.12s
src/agent_docs_sync/tools/check_links.py  ruff check passed
```

## Full Verification

| Gate | Result |
|---|---|
| pytest (full suite) | 277 passed, 4 warnings |
| mypy --strict (49 source files) | No issues |
| ruff check (changed files only) | All passed |
| ruff check (full repo src/ tests/) | 13 pre-existing I001 import-order findings in unrelated test files |
| ruff format (full repo) | 95 files already formatted |
| GitNexus impact (upstream) | CRITICAL — 8 affected processes |
| GitNexus detect-changes (staged) | HIGH — 11 symbols, 10 affected processes |

## CLI Acceptance

| Fixture | Result |
|---|---|
| Positive (all links present in fixture) | 3 links checked in 4 files, exit 0 |
| Negative (target deleted from fixture) | 1 broken link reported, exit 1 |
| Agent-core validation (before fix) | 31 broken links |
| Agent-core validation (after fix) | 2 genuine documentation defects, exit 1 |

## Remaining Genuine Defects (agent-core — filed separately)

1. `docs/README.md → model-resolution.md` — file does not exist under `docs/`
2. `docs/extending.md → docs/scheduling.md` — resolves to `docs/docs/scheduling.md` (path duplication)

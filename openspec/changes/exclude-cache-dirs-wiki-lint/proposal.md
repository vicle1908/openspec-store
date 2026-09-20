# Proposal

## Why

Running tests in `~/Developer/wiki` generates test cache artifacts such as `.pytest_cache/README.md`. Because `wiki-lint.py` directory traversal only excludes `(".git", "_archive")` without filtering hidden dot-directories or cache directories, these untracked runner files produce false positive lint failures (`no frontmatter found` and `orphan (zero inbound links)`), while `wiki/.gitignore` lacks `.pytest_cache/` coverage.

## What Changes

- **Exclude hidden and cache directories in `wiki-lint.py`**: Update `_scan_pages()` in `wiki/scripts/wiki-lint.py` to skip all directory path segments starting with `.` (such as `.pytest_cache`, `.venv`, `.git`) or listed in an expanded `EXCLUDED_DIRS` set (`.git`, `_archive`, `.pytest_cache`, `.ruff_cache`, `.venv`).
- **Update `wiki/.gitignore`**: Add `.pytest_cache/` and Python test cache artifacts to `~/Developer/wiki/.gitignore`.
- **Add unit test coverage**: Add a test in `wiki/tests/test_wiki_lint.py` verifying that hidden dot-directories and test caches are ignored during page discovery and orphan calculation.
- **Explicit Non-Goals**:
  - We do NOT modify, delete, or commit files within `.pytest_cache/`.
  - We do NOT alter existing frontmatter, link resolution, or staleness rules for tracked wiki pages in `entities/`, `concepts/`, `comparisons/`, `architecture/`, or `references/`.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `workspace-wiki-integrity`: Update wiki lint discovery requirements so that hidden dot-directories and runner cache directories are excluded from frontmatter, link, and orphan validation.

## Impact

- **Affected Repository**: `/Users/androidteam/Developer/wiki` (`scripts/wiki-lint.py`, `.gitignore`, `tests/test_wiki_lint.py`).
- **Affected Specs**: `openspec/specs/workspace-wiki-integrity/spec.md`.
- **Ownership Boundaries**: Scoped strictly to wiki lint automation and ignores; does not mutate any wiki knowledge content or external repository code.

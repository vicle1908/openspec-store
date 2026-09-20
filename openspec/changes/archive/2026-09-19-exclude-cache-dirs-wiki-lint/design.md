# Design

## Context

Running tests or tools in `~/Developer/wiki` (e.g. pytest or IDE tooling) creates local cache directories such as `.pytest_cache/` containing `.pytest_cache/README.md`. 

Currently, `_scan_pages()` in `wiki/scripts/wiki-lint.py` collects all `.md` files under the wiki root using `root.rglob("*.md")` and filters only against `EXCLUDED_DIRS = (".git", "_archive")`. Because `.pytest_cache` is not in `EXCLUDED_DIRS`, the scanner attempts to parse `.pytest_cache/README.md`, flagging it with:
1. `no frontmatter found`
2. `orphan (zero inbound links)`

Additionally, `wiki/.gitignore` does not ignore `.pytest_cache/`.

## Goals / Non-Goals

**Goals:**
- Update `wiki/scripts/wiki-lint.py` to filter out any directory segment that starts with `.` or is in `EXCLUDED_DIRS`.
- Add `.pytest_cache/` and common Python test artifacts to `wiki/.gitignore`.
- Add a unit test in `wiki/tests/test_wiki_lint.py` proving that files inside `.pytest_cache/` are ignored.

**Non-Goals:**
- Do not mutate or track `.pytest_cache/README.md`.
- Do not change frontmatter or orphan rules for valid content pages.

## Decisions

### 1. Robust Directory Filtering in `_scan_pages`
Update `_scan_pages()` in `scripts/wiki-lint.py`:
```python
def _scan_pages(root):
    pages = []
    for p in sorted(root.rglob("*.md")):
        parts = p.relative_to(root).parts
        # Skip hidden directories (starting with '.') and explicitly excluded directories
        if any(d in EXCLUDED_DIRS or d.startswith(".") for d in parts[:-1]):
            continue
        pages.append(_parse_page(p, root))
    return pages
```
*Rationale*: Checking `d.startswith(".")` on parent directory parts (`parts[:-1]`) cleanly ignores all hidden directories (`.pytest_cache`, `.venv`, `.git`, `.ruff_cache`, `.idea`, etc.) without needing an exhaustive list.

### 2. Update `EXCLUDED_DIRS`
Update the constant in `wiki-lint.py`:
```python
EXCLUDED_DIRS = (".git", "_archive", ".pytest_cache", ".ruff_cache", ".venv")
```

### 3. Update `wiki/.gitignore`
Append `.pytest_cache/` and test cache globs to `wiki/.gitignore`.

## Risks / Trade-offs

- **Risk**: A valid documentation directory might start with `.` (unlikely).
- **Mitigation**: Standard wiki structure places documentation in `entities/`, `concepts/`, `comparisons/`, `architecture/`, `references/`, and `raw/`. No valid content pages reside in dot-folders.

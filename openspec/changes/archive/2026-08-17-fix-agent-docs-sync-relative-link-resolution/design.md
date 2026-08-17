# Design: Relative Link Resolution Fix

## Resolution Semantics (Target)

| Link form | Resolution origin | Example |
|---|---|---|
| Ordinary relative (`guide.md`) | `source_file.parent` | `docs/README.md → guide.md` → `docs/guide.md` |
| Parent-relative (`../api.md`) | `source_file.parent` | `docs/guide/start.md → ../api.md` → `docs/api.md` |
| Fragment (`#section`) | N/A (valid) | Always valid |
| Anchor-only (`#`) | N/A (valid) | Always valid |
| External (`http://`, `https://`) | Skipped unless `check_external` | Existing behavior preserved |
<!-- Root-absolute link behavior is not part of the confirmed defect and is excluded from this change scope. -->

## `base_dir` Redefinition

**Before:** `base_dir` is the origin for all relative link resolution.
**After:** `base_dir` is the containment boundary. A resolved path must
remain within `base_dir` (if provided) to be considered valid. Resolution
origin is always `source_file.parent`.

## Security Boundary

If `base_dir` is provided and the resolved path escapes it (e.g., via
`../../etc/passwd`), the link SHALL be reported as broken with reason
`"Escapes repository boundary"`. This prevents path-traversal false
positives from being reported as valid.

## Implementation

### `_check_link()` change

```python
# Before (defect): base_dir overrides resolution origin
# resolved = (base_dir / file_path).resolve()

# After: resolve from source_file.parent, contain with base_dir
boundary = Path(args.base_dir).expanduser().resolve() if args.base_dir else None
resolved = (source_file.parent / file_path).resolve()

if boundary is not None and not resolved.is_relative_to(boundary):
    return {"status": "broken", "reason": f"Escapes repository boundary: {resolved}"}
```

### `_find_broken_links()` change

No caller changes needed. Both `_find_broken_links()` and `cli.py`
continue passing `base_dir=str(repo_path)`. The semantic change is
entirely within `_check_link()` and `_check_file()`, where `base_dir`
now acts as a containment boundary rather than a resolution origin.

### Directory-mode `execute()` change

When `target.is_dir()`, the current code passes a single `base` to all
files. After the fix, each file resolves from its own parent, and `base`
acts only as the containment boundary. No caller change needed.

## Test Matrix

| Scenario | Input | Expected |
|---|---|---|
| Sibling link | `docs/README.md → guide.md`, `docs/guide.md` exists | valid |
| Nested parent link | `docs/guide/start.md → ../api.md`, `docs/api.md` exists | valid |
| Missing target | `docs/README.md → nonexistent.md` | broken |
| Fragment link | `docs/README.md → #section` | valid |
| External link | `docs/README.md → https://example.com` | valid (skipped) |
| Boundary escape | `docs/README.md → ../../etc/passwd` | broken (escapes) |
| Image relative | `docs/README.md → ![img](img.png)`, `docs/img.png` exists | valid |

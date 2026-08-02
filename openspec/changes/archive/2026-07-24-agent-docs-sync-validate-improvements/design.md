## Context

The `docs-sync validate` command checks markdown files for broken links. Currently it:
- Scans files sequentially (slow)
- Shows no progress (confusing)
- Defaults to scanning everything (hangs)
- Can't skip external URLs (unnecessary delays)

## Goals / Non-Goals

**Goals:**
- Parallel file validation (5-10x speedup)
- Progress reporting during validation
- Selective checking (local-only, skip images)
- Better default behavior

**Non-Goals:**
- Caching/incremental validation (future enhancement)
- Output format changes (already has --output json)
- New validation types (link checking only)

## Decisions

### Decision 1: Parallel Validation with asyncio.gather()

Use `asyncio.gather()` to check multiple files concurrently:

```
Current (sequential):          Improved (parallel):
├─ file1.md (2s)               ├─ file1.md ─┐
├─ file2.md (2s)               ├─ file2.md ─┼─ gather() → 2s total
├─ file3.md (2s)               └─ file3.md ─┘
└─ Total: 6s
```

### Decision 2: Progress with Rich Library

Use `rich.progress` for progress bars:
```
Checking docs... ━━━━━━━━━━━━━━━━━━━━━━━━━ 3/10 files
```

### Decision 3: Selective Checking Flags

```bash
# Local files only (fast)
docs-sync validate --check-local

# Include external URLs (slower)
docs-sync validate --check-external

# Skip image validation
docs-sync validate --skip-images
```

### Decision 4: Smart Default Path

When no --path provided:
```python
if path:
    target = path
elif Path(repo / "docs").exists():
    target = str(Path(repo) / "docs")
else:
    target = repo
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Validation Pipeline (Improved)                         │
└─────────────────────────────────────────────────────────┘

  CLI (--check-local, --check-external, --skip-images)
    │
    ▼
  CheckLinksTool.execute(path, options)
    │
    ├─ Discover .md files (fast)
    │
    ▼
  asyncio.gather(*[_check_file(f) for f in files])
    │
    ├─ Parallel HTTP requests (external)
    ├─ Parallel file existence checks (local)
    │
    ▼
  Rich progress bar updates
    │
    ▼
  Results aggregated
```

## Configuration

```bash
# CLI Options
--path TEXT           Specific file or directory
--check-local         Only check local file links (default)
--check-external      Also check HTTP links
--skip-images         Skip image validation
--output TEXT         Output format: text, json
```

## Error Handling

| Error | Handling |
|-------|----------|
| File not found | Report as broken link |
| HTTP timeout | Report as warning, continue |
| HTTP error | Report status code, continue |
| Permission error | Skip file, report warning |

## Testing Strategy

| Test Type | Scope |
|-----------|-------|
| Unit | CheckLinksTool with new options |
| Integration | Parallel execution correctness |
| E2E | CLI with --check-local, --check-external |
| Performance | Parallel vs sequential timing |

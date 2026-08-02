## Why

The `docs-sync validate` command currently has usability issues:
1. **Hangs without --path** — Scans all markdown files recursively, appearing unresponsive
2. **No progress indication** — User doesn't know what's being checked
3. **Sequential processing** — Slow for many files
4. **No selective checking** — Can't skip external URLs or images

These issues make the validate command frustrating to use and discourage regular doc validation.

## What Changes

- **Parallel validation** — Check multiple files concurrently using asyncio.gather()
- **Progress reporting** — Show "Checking file 3/10..." during validation
- **Selective checking** — Flags for --check-local, --check-external, --skip-images
- **Better defaults** — Default to docs/ directory when no --path provided

## Capabilities

### Modified Capabilities

- `agent-docs-sync`: Enhance validate command with parallel execution, progress reporting, and selective checking

## Impact

- **Code changes:** `agent-docs-sync/src/agent_docs_sync/cli.py`, `tools/check_links.py`
- **Dependencies:** None new (asyncio already available)
- **Breaking changes:** None — all new flags are optional

# Evidence: Fix docs-sync global --json output contract

## SHA Provenance

| Artifact | SHA | Repository |
|---|---|---|
| OpenSpec planning | `16834ca` | openspec-store |
| Implementation | `9806733` | agent-docs-sync |
| Base (pre-fix) | `b138a3f` | agent-docs-sync |

## RED Evidence (pre-fix)

```
test_json_output_global_flag FAILED
  json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
  stdout: '=== Doc Sync Check Report ===\nRepository: ...\nChanges detected: False\n...'
```

## GREEN Evidence (post-fix)

```
3 passed in 9.24s
  test_json_output_subcommand_flag PASSED
  test_json_output_global_flag PASSED
  test_text_output_default PASSED
```

## Full Verification

| Gate | Result |
|---|---|
| pytest (full suite) | 280 passed, 4 warnings |
| mypy --strict (cli.py) | No issues |
| ruff check (changed files) | All passed |
| ruff format (changed files) | Formatted |
| Real CLI `docs-sync --json check --repo agent-core` | Valid JSON, exit 0 |
| git diff --check | Clean |

## What Changed

1. Added `_effective_output()` helper after `_json_output` declaration
2. Replaced 5 dispatch guards (`if output == "json":`) with `_effective_output()` calls
3. Added 3 subprocess CLI regression tests

## Unchanged

- Sync command's unconditional JSON emit (no `--output` option; separate concern)
- Approval lifecycle commands (pending/list/approve/deny/resume) — separate scope
- graphify-out/ pre-existing dirty state

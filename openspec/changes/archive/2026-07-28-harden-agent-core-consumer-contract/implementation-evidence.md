# Implementation evidence

## Core contract

- `ConsumerRuntimeProfile.tools_allowed` preserves omission as `None`; `()` is
  explicit deny-all; non-empty tuples remain bounded.
- `build_agent`, flavor merging, static preparation, and run-scoped preparation
  preserve the distinction and intersect visibility policies. Unknown names do
  not broaden access.
- `AgentRuntime.step_store_is_process_local` and `step_store_backend` expose the
  selected upstream store without exposing persisted content or credentials.
- A supplied `StepPersistence` is retained. SQLite reconstruction is exercised
  in a separate spawned process through `continue_run`; a failed declared store
  propagates `OSError` and is not replaced with memory.
- `AgentConfig.step_persistence` is retained only as compatibility metadata; it
  is not a runtime construction path.

## Verification

- agent-core: `uv sync --frozen`; Ruff check/format; strict mypy over `src` and
  `tests`; 575 tests passed; coverage 82.82% (threshold 80%).
- agent-docs-sync: frozen sync and 195 tests passed against the editable core.
- agent-harness: frozen sync and full pytest suite passed against the editable
  core; the legacy sentinel remains until the dependent harness change.
- `npx gitnexus detect-changes --scope all -r agent-core` reports a coarse
  CRITICAL projection (17 files, 62 symbols, 43 flows). Manual review shows the
  runtime edits are limited to tool-policy composition/preparation, store
  diagnostics, and profile/build composition; documentation and tests account
  for the remaining files. No `_compute_allowed_tools` or run-loop logic was
  edited.

## Rollback

The persistent snapshot schema and upstream store implementation are unchanged
from the prior core baseline. A SQLite snapshot written before rollback remains
readable by the unchanged `SqliteStepStore`; omitted legacy profiles continue to
validate as unrestricted. Rollback therefore restores the prior core package and
temporarily retains the harness sentinel, without deleting or migrating the
consumer's state database.

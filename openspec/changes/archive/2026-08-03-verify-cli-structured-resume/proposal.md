## Why

All three coding CLIs now pass a basic editing task, but reliable automation also depends on machine-readable structured results and the ability to continue a prior noninteractive session without restating its context.

## What Changes

- Run schema-constrained structured-output probes for Antigravity, Claude Code, and Codex.
- Capture each CLI's session/conversation identifier without recording credentials.
- Resume each noninteractive session and verify a context-dependent value supplied only in the first turn.
- Update the orchestration skills if live behavior differs from existing documentation.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

None. This is a procedural verification change with `skip_specs: true`.

## Impact

- Disposable fixture and schema files under `/tmp/cli-structured-resume-20260803`.
- Hermes orchestration skill documentation if caveats are discovered.
- Shared OpenSpec verification archive.
- No application repositories or credentials are modified.

## Non-Goals

- Long-context quality evaluation.
- Concurrent session editing.
- Testing interactive session pickers.
- Comparing model intelligence or cost across providers.

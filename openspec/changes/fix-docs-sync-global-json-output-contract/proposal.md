# Proposal: Fix docs-sync global --json output contract

## Why

`docs-sync --json check --repo ...` emits the human-readable text report instead
of JSON. The global `--json` flag stores a boolean in `_json_output` and configures
logging, but command output dispatch is controlled by each command's local `output`
option. Since the global flag's help text says "JSON output," users who write
`docs-sync --json check ...` expect machine-readable JSON and get prose.

This is a real contract inconsistency: the per-command `--output json` works,
the global `--json` does not.

## What Changes

- Add a `_effective_output()` helper that resolves the effective output mode
  from both the global `_json_output` flag and the command's local `output` option.
- Use the effective mode at each command's output dispatch point.
- Add subprocess-based CLI regression tests that invoke the actual installed CLI.

## Non-Goals

- No changes to logging behavior (JSON logging stays separate from JSON output).
- No changes to agent-core or other repositories.
- No skill-profile mutations.

## Impact

- Blast radius: LOW — `_effective_output` is a leaf helper; only CLI dispatch code
  is touched. No workflow, generation, or agent code changes.
- Consumers: CLI users who write `docs-sync --json <command>`.
- Risk: Existing `--output json` paths must remain unchanged. Regression tests
  cover both invocations.

# Proposal: openspec-progress-exit-status-correction

## Why

Four live OpenSpec workflow examples pipe `openspec instructions apply --json` directly into a Python parser without preserving the upstream command's exit status. A failed command can therefore produce a misleading parsed diagnostic or no useful result while the shell pipeline exits successfully. This undermines the workflow's explicit evidence and loop-prevention contract.

## What Changes

- Replace the four affected task-progress examples with a status-preserving pattern.
- Require the parser to emit progress only after the OpenSpec command succeeds.
- Preserve the explicit `--store openspec-store` and JSON contract.
- Do not modify the archived `verification-loop-workflow-correction` artifacts.

This is a documentation/workflow correction only; it has no product behavior or normative OpenSpec requirement delta (`skip_specs: true`).

## Evidence

Verified against installed OpenSpec 1.8.0:

- `openspec instructions apply --change definitely-not-a-real-change --json --store openspec-store | python3 ...` returned shell exit 0 despite a command-specific JSON error.
- The same pipeline under `set -o pipefail` returned exit 1.
- Exact live matches were found in the primary workflow skill, `active-change-triage.md`, `implementation-pitfalls.md`, and `pre-archive-validation.md`.
- The prior `verification-loop-workflow-correction` is archived and remains immutable.

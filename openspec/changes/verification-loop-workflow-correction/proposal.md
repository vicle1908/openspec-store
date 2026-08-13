# Proposal: verification-loop-workflow-correction

## Why

The shared OpenSpec workflow can send an agent into repeated verification instead of advancing to the next gate. The primary cause is that the CLI exposes different state dimensions through different commands, while several workflow references treat them as interchangeable:

- `openspec status --change <name> --json` reports planning-artifact completion, not implementation-task completion.
- `openspec instructions apply --change <name> --json` reports implementation-task progress.
- `openspec validate` reports structural validity only.
- `openspec archive --yes` can intentionally bypass the incomplete-task warning.

The workflow also contains unscoped validation examples that return `Nothing to validate` from consumer repositories, shell pipelines that hide verifier exit codes, and checkbox-count snippets that can generate duplicate zero values for missing task files.

## What Changes

- Document the four distinct lifecycle state dimensions and their authoritative commands.
- Make review commands explicitly target the registered `openspec-store`.
- Replace masked validation examples with commands that preserve the verifier exit code.
- Replace fragile `grep -c ... || echo 0` arithmetic with a parser matching the OpenSpec task grammar.
- Bound multi-round verification and require a state change before repeating a gate.
- Preserve incomplete tasks as incomplete; structural validation or planning completion must never be used to mark implementation complete.

This is a workflow and documentation correction only; it does not change product behavior or normative OpenSpec requirements (`skip_specs: true`).

## Evidence

Observed on 2026-08-13 with OpenSpec CLI 1.8.0:

- `openspec status --change complete-agent-llm-config-integration --json --store openspec-store` returned `isComplete: true` and all four planning artifacts `done`, while the change had `0/140` implementation tasks.
- `openspec instructions apply --change complete-agent-llm-config-integration --json --store openspec-store` returned `state: ready`, `progress.total: 140`, `complete: 0`, `remaining: 140`.
- `openspec validate --strict` from `~/Developer/agent-core` returned `Nothing to validate` with exit 1.
- `openspec validate complete-agent-llm-config-integration --strict --store openspec-store` passed.
- `openspec validate --all --strict --no-interactive --store openspec-store` passed with 373/373 items.
- The legacy missing-file shell pattern produced `done_count=$'0\n0'` and an arithmetic syntax error.
- `openspec store doctor --json openspec-store` reported no issues.

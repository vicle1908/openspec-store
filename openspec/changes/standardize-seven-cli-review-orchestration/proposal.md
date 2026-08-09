# Proposal: Standardize Seven-CLI Review Orchestration

## Why

The review workflow references use stale versions, incorrect flags, and contradictory guidance:
- `fable-5 --auto` referenced but `fable-5` is not an installed binary name
- `pi --no-session` flag does not exist
- `agy --print` should be `agy -p`
- "Never pass file paths in the prompt" contradicts file-based context strategy
- Goose and Kimi added but not in the orchestration lens table
- No standardized CLI verification protocol

## What Changes

1. Update `references/cli-based-review-workflow.md` — ground-truth versions, 7 CLIs, corrected flags
2. Update `references/five-provider-review-orchestration.md` — 7 CLI lenses, verified invocation patterns
3. Add real CLI verification protocol with compact context fixture
4. Standardize output contract (VERDICT + findings + recommendations)
5. Document default-model-only policy (no `-m`, `--model`, or provider overrides)

## Scope

- OpenSpec skills references only (not source code changes)
- Hermes skill files at `~/.hermes/skills/`
- No changes to agent-core, openspec-store main specs, or production config

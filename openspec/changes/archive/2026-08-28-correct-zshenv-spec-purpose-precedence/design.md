## Context

Canonical credential specs now use the managed `.zshenv` block, but Purpose text and three migration-era requirements still contradict the active implementation.

## Goals / Non-Goals

**Goals:** Correct both Purpose texts and replace the stale `Shared allowlisted loader`, `Nonfatal missing sources`, and `Pre-existing variable precedence` requirements with accurate `.zshenv` contracts and scenarios.

**Non-Goals:** No credential, shell, OMP, provider, or routing changes.

## Decisions

Use REMOVED/ADDED deltas for all three affected requirements. Preserve accurate scenario coverage by adding scenarios for managed-block absence and retired-loader absence, while replacing the inherited-sentinel behavior with unconditional `.zshenv` overwrite semantics. Apply Purpose text edits explicitly during implementation because existing-capability Purpose fields are not synchronized automatically by archive.

## Risks / Trade-offs

The precedence scenario uses a sentinel input only; verification remains value-blind.

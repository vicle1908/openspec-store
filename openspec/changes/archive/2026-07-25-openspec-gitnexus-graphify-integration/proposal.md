## Why

OpenSpec workflows currently operate without code intelligence tools. When implementing changes, the agent works blind without understanding blast radius, architecture consistency, or scope verification.

**Current guardrails in openspec-apply-change:**
- Keep going through tasks until done or blocked
- Always read context files before starting
- If task is ambiguous, pause and ask before implementing
- Keep code changes minimal and scoped to each task
- Update task checkbox immediately after completing each task

**Missing:**
- No impact analysis before code changes
- No change detection after code changes
- No architecture exploration tools
- No blast radius assessment

## What Changes

- **openspec-apply-change**: Add GitNexus impact analysis BEFORE and detect_changes AFTER each code change
- **openspec-explore**: Add GitNexus query/context and Graphify query/path/explain
- **openspec-propose**: Add blast radius assessment to proposals
- **openspec-verify-change**: Add scope verification with detect_changes

## Capabilities

### Modified Capabilities
- `openspec-apply-change`: Add code intelligence guardrails
- `openspec-explore`: Add GitNexus/Graphify exploration workflow
- `openspec-propose`: Add pre-proposal impact analysis
- `openspec-verify-change`: Add scope verification

## Impact

- **Files modified**: 4 OpenSpec skill files in `.agents/skills/openspec-*`
- **No code changes**: Documentation/instructions only
- **Dependencies**: Requires GitNexus index to be fresh

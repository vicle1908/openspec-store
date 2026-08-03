## Context

Antigravity, Claude Code, and Codex expose different project, permission, sandbox, and authentication interfaces. A fair functional check needs identical source state, prompt, and external acceptance criteria while preserving each CLI's correct invocation contract.

## Goals / Non-Goals

**Goals:**

- Verify that each CLI can diagnose a failing test, edit the correct file, and make all tests pass.
- Prevent cross-agent contamination with separate Git repositories.
- Capture machine-verifiable outcomes independently of agent self-reports.

**Non-Goals:**

- Statistical model evaluation.
- Testing network, MCP, browser, subagent, or PR capabilities.
- Measuring production-grade performance.

## Decisions

### Decision: Use a deterministic standard-library Python fixture

The fixture contains a small `slugify` function whose handling of repeated separators and surrounding whitespace is incorrect. `unittest` requires no dependency installation and produces deterministic pass/fail results.

### Decision: Seed three repositories from identical files

Each repository receives the same committed baseline. Agent processes cannot see or edit another agent's checkout.

### Decision: Use equivalent autonomous write authority

- Antigravity: fresh logical project, exact workdir, absolute target scope, bounded print mode.
- Claude Code: login-shell token context, print mode, explicit file/Bash tools, bounded turns.
- Codex: exec mode, `approval_policy="never"`, workspace-write sandbox.

### Decision: Verify outside each agent

After completion, run `python3 -m unittest -v`, inspect `git diff --check`, changed filenames, and final file content. A successful narrative without passing tests is a failure.

## Risks / Trade-offs

- **Different models and system prompts** → Treat this as capability verification, not a quality leaderboard.
- **Agent adds unnecessary files** → Record changed filenames and reject out-of-scope changes.
- **CLI startup/context overhead dominates timing** → Report observed duration only, without broad performance conclusions.
- **Concurrent OpenSpec work exists** → Commit only this change's archived path.

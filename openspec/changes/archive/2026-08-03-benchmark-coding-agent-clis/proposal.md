## Why

The three CLIs have been individually validated, but a uniform coding benchmark is still needed to demonstrate comparable autonomous editing and test execution under the same task and independent verification criteria.

## What Changes

- Create three identical disposable Git repositories with one deterministic Python bug and failing unit tests.
- Give Antigravity, Claude Code, and Codex the same implementation instruction in isolated repositories.
- Use each CLI's verified safe automation path and configured authentication context.
- Independently inspect each diff and run the test suite after the agent exits.
- Record outcome, duration, file placement, test status, and notable orchestration behavior.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

None. This is a disposable verification exercise with `skip_specs: true`.

## Impact

- **Temporary surface:** `/tmp/coding-agent-cli-benchmark-20260803/`.
- **Persistent evidence:** Shared OpenSpec archive only.
- **Production impact:** None.
- **Credentials:** Existing CLI authentication is used without printing or persisting credential values.

## Non-Goals

- Ranking model intelligence from one tiny task.
- Benchmarking cost or latency under controlled laboratory conditions.
- Modifying application repositories.
- Committing agent-generated fixture changes outside disposable repositories.

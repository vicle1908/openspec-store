# Proposal: align-realtime-vitest-docs

## Why
The realtime frontend documentation identifies Vitest as the test runner, but the tracked frontend still contains a Jest configuration and Jest-style test globals. After the initial migration, the full Vitest suite exposed behavioral failures that must be resolved before claiming alignment.

## What Changes
- Run and align the actual Vitest suite.
- Remove or migrate stale Jest configuration and globals consistently.
- Fix migration-caused or newly exposed test failures within the frontend test/component scope, including timeout and accessibility failures.
- Update frontend README/testing documentation to describe the supported runner and commands.
- Preserve test behavior and verify build plus the complete Vitest suite.

## Outcome
The tracked code, test configuration, tests, and documentation describe and execute one consistent, green Vitest-based workflow.

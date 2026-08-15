## 1. Binary contract

- [x] 1.1 Implement `platform/cmd/agent-core` `version` and `health` commands.
- [x] 1.2 Add Compose option environment handling for file, env file, and project.
- [x] 1.3 Parse object and array Compose JSON; fail closed for empty, malformed, missing, stopped, and unhealthy records.
- [x] 1.4 Add Go unit tests for all parser and exit-state cases.

## 2. Integration script

- [x] 2.1 Derive repository-relative defaults for Compose file, env file, project, and binary output.
- [x] 2.2 Validate `AGENT_CORE_BIN` overrides and preserve caller-owned binaries.
- [x] 2.3 Add bounded duration parsing and fail-closed Compose polling.
- [x] 2.4 Ensure cleanup removes only resources started by the script and only binaries built by it.

## 3. Regression and documentation

- [x] 3.1 Expand the no-Docker regression suite with stubbed command behavior for empty, malformed, and failing Compose status.
- [x] 3.2 Document invocation, defaults, overrides, and environment-independent regression coverage in `scripts/README.md`.
- [x] 3.3 Run focused validation, platform tests, vet, build, shell syntax checks, and `git diff --check`.
- [x] 3.4 Review and commit only owned Go/script/documentation paths; preserve unrelated worktree changes.

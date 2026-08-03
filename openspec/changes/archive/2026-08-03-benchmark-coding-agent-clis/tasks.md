## 1. Benchmark Definition

- [x] 1.1 Define one deterministic Python bug, failing tests, shared prompt, and acceptance criteria.
- [x] 1.2 Create three identical disposable Git repositories and confirm the baseline tests fail identically.

## 2. Agent Execution

- [x] 2.1 Run Antigravity in its isolated repository using bounded print mode.
- [x] 2.2 Run Claude Code in its isolated repository using the login-shell token context and bounded print mode; record repeated pre-token API connectivity failure.
- [x] 2.3 Run Codex in its isolated repository using noninteractive workspace-write mode.

## 3. Independent Verification

- [x] 3.1 Run unit tests and diff checks independently in all three repositories.
- [x] 3.2 Confirm Antigravity and Codex changed only `slugify.py`; confirm Claude remained unchanged after pre-token connectivity failures.
- [x] 3.3 Record exact outcomes and non-secret execution metadata in `verification.md`.

## 4. Closure

- [x] 4.1 Run focused and full strict OpenSpec validation.
- [x] 4.2 Archive and commit only this benchmark change's paths.
- [x] 4.3 Remove disposable repositories and confirm no benchmark-owned uncommitted store paths remain.

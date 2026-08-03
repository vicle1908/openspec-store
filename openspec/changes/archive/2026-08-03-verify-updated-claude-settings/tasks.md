## 1. Settings and Connectivity

- [x] 1.1 Inspect updated settings using secret-safe redaction.
- [x] 1.2 Confirm direct invocation uses settings-owned environment while login shell still overrides the endpoint.
- [x] 1.3 Verify direct Claude API connectivity and authenticated status.

## 2. Coding Verification

- [x] 2.1 Create the same deterministic failing fixture used in the three-CLI benchmark.
- [x] 2.2 Run Claude directly with bounded tools, permissions, and turns.
- [x] 2.3 Independently verify four passing tests, clean diff, and `slugify.py`-only tracked changes.

## 3. Documentation and Closure

- [x] 3.1 Update the Claude Code skill with settings-versus-login-shell precedence guidance.
- [x] 3.2 Record non-secret verification evidence and run focused/full strict validation.
- [x] 3.3 Archive and commit only this change's paths, remove the fixture, and preserve concurrent work.

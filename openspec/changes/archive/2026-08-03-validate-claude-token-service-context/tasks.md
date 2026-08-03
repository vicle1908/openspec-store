## 1. Authentication Discovery

- [x] 1.1 Verify the direct Hermes process has no Claude token variables without printing values.
- [x] 1.2 Verify `zsh -lic` loads `ANTHROPIC_AUTH_TOKEN` using a presence-only check.
- [x] 1.3 Verify login-shell `claude auth status` reports authenticated token usage.

## 2. Runtime Verification

- [x] 2.1 Run a one-turn, no-tools Claude JSON request through the login shell.
- [x] 2.2 Confirm the process exits zero and returns exactly `CLAUDE_TOKEN_OK`.
- [x] 2.3 Record non-secret session, model, usage, and cost metadata.

## 3. Skill Update

- [x] 3.1 Add the service/login-shell environment distinction to the Claude Code skill.
- [x] 3.2 Add safe presence-only and token-loaded invocation examples.
- [x] 3.3 Reload the skill and verify no token values or unsafe command-line token examples are present.

## 4. Closure

- [x] 4.1 Write verification evidence and run focused plus full strict OpenSpec validation.
- [x] 4.2 Archive and commit only this change's paths.
- [x] 4.3 Confirm no uncommitted paths from this change remain; preserve concurrent work.

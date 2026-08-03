## Context

Direct Hermes subprocesses reported Claude Code logged out and did not contain `ANTHROPIC_AUTH_TOKEN`. A noninteractive `zsh -lic` presence check found the token in the user's login-shell environment. The same context changed `claude auth status` to authenticated and allowed model execution.

## Goals / Non-Goals

**Goals:**

- Make token-backed Claude invocation reliable from Hermes without revealing credentials.
- Ensure presence checks, status checks, and model execution share the same environment.
- Keep delegated verification bounded and tool-free.

**Non-Goals:**

- Exporting the token into launchd.
- Changing shell initialization files.
- Creating new credentials.

## Decisions

### Decision: Invoke through `zsh -lic`

Use the user's noninteractive login shell because it is the existing source of token configuration. Run `claude auth status` and `claude -p` inside that same command environment.

Alternative considered: copy the token into the Hermes process or command line. Rejected due to credential exposure and duplicated secret management.

### Decision: Use presence-only diagnostics

Check whether named variables are present without printing values. Record only auth method and success metadata.

### Decision: Use a no-tools bounded probe

Run `claude -p` with `--tools ""`, `--max-turns 1`, and JSON output. This verifies the model/auth path without file, shell, MCP, or network-tool authority.

## Risks / Trade-offs

- **Login-shell startup files change** → Re-run presence and auth status through the same shell before each delegated task.
- **Token exists but expires** → Treat nonzero auth/model results as authentication failure and ask the user to refresh their token.
- **Shell startup has side effects** → Keep the invocation noninteractive, bounded, and inspect exit status/output.

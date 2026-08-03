## Context

The updated settings include a token and remote `ANTHROPIC_BASE_URL`. Direct Hermes subprocesses do not set that URL and therefore allow Claude Code to load the settings value. By contrast, `zsh -lic` still exports the obsolete loopback URL and overrides settings precedence.

## Goals / Non-Goals

**Goals:**

- Verify the effective direct-invocation path without exposing secrets.
- Repeat the exact prior coding fixture with tool authority.
- Preserve the distinction between connectivity/customization behavior and coding correctness.

**Non-Goals:**

- Editing shell startup files.
- Removing the stale login-shell export.
- Altering Claude customization plugins or security hooks.

## Decisions

### Decision: Use direct Claude invocation

Run `claude` directly so `~/.claude/settings.json` supplies its configured environment. Do not use `zsh -lic` while it overrides `ANTHROPIC_BASE_URL` with the stale loopback endpoint.

### Decision: Treat exact-output probe refusal as customization behavior

The direct minimal request reached the API but the customization stack classified forced exact output as prompt injection. Connectivity is proven by a successful API result; response text is not used as a health assertion.

### Decision: Reuse the prior deterministic fixture

Use the same buggy `slugify()` implementation, tests, prompt, and acceptance criteria to close the historical runtime-unavailable gap fairly.

## Risks / Trade-offs

- **Shell invocation regresses endpoint selection** → Prefer direct process invocation while settings own endpoint/token.
- **Customization stack changes response style** → Judge coding by external diff/tests, not exact narrative output.
- **Broad user permissions exist** → Continue supplying narrow per-invocation tools and permission rules.

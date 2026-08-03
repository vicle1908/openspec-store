## Context

The three CLIs are installed and authenticated, but provider topology differs:

- Antigravity uses Google Antigravity services and runtime-listed models.
- Claude Code uses a configured first-party-compatible custom endpoint/model rather than `api.anthropic.com`.
- Codex uses a custom Responses API provider/model rather than the default OpenAI endpoint.

Upstream CLI flags therefore describe potential capability, while live probes establish only what the configured provider/model actually supports.

## Goals / Non-Goals

**Goals:**

- Produce a conservative matrix grounded in current binaries, settings, and successful runtime evidence.
- Distinguish transport JSON from schema-constrained output.
- Distinguish feature discovery from successful provider-backed execution.
- Recheck critical noninteractive coding paths after current provider changes.

**Non-Goals:**

- Validate every model exposed by each provider.
- Change provider routing or credentials.
- Run interactive account or payment flows.

## Decisions

### Decision: Four evidence classes

Each capability is labeled:

1. **Verified runtime** — exercised successfully through the configured provider.
2. **Provider-limited** — CLI supports it, but current provider/model fails or ignores it.
3. **Surface verified** — current CLI/help/config exposes it, but no external side-effecting runtime test was performed.
4. **Not tested** — neither runtime nor sufficient local-surface evidence in this pass.

### Decision: Reuse bounded common probes

Use non-destructive probes for JSON transport and provider identity, one disposable coding fixture per CLI, session continuation with a nonce, and schema validation where supported. MCP checks are read-only and use existing configured servers only.

### Decision: Preserve provider routing

Do not unset `ANTHROPIC_BASE_URL`, override Codex provider configuration, or switch Antigravity accounts/models except by selecting a runtime-listed model slug for a bounded invocation.

### Decision: Verify externally

Read files, inspect diffs, execute tests, parse output envelopes, and validate schemas outside the agent. Agent narrative alone is not acceptance evidence.

## Risks / Trade-offs

- **Provider behavior changes after verification** → Record date, CLI version, configured model/provider, and require future rechecks.
- **Custom plugins alter prompts/results** → Record customization-sensitive behavior and use safe mode only as a diagnostic, not a silent production default.
- **Feature discovery is mistaken for execution** → Keep evidence classes explicit in every matrix row.
- **Concurrent store work** → Stage and commit only this archived change path.

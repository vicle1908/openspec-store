## Why

The agent ecosystem has no single executable contract for resolving LLM models, provider metadata, and environment-backed secrets. Existing main specs conflicted, direct consumers exposed different effective values, and two untracked planning drafts overlapped an already archived change. This corrective change establishes one source-aware resolution boundary.

**Native CLI convergence insight.** Codex, Grok, Kimi, and Pi all converge on the same three-layer configuration pattern — provider definitions (endpoint + protocol + credential reference), named model aliases (provider + wire model + behavior), and default alias selection. The TDT ecosystem duplicates this information across `config.yaml`, the packaged `environment-key-registry.json`, and per-agent YAML files, creating synchronization failures. This change aligns TDT Python consumers with the proven native CLI pattern.

## What Changes

- Add a canonical, typed resolved-agent-profile API in `tdt-core` that returns immutable effective model/runtime/provider data plus redacted source provenance.
- Make the precedence contract executable: explicit run override > consumer-specific process environment > shared model environment > per-agent YAML > global YAML > defaults.
- Make `tdt-core` the sole owner of `TDT_HOME`, dotenv/profile loading, secure YAML mapping, agent-overlay policy, path containment, cache invalidation, and environment-key metadata.
- Make `agent-core` consume a resolved profile and construct Pydantic-AI models without reading YAML or dotenv files.
- Correct `agent-docs-sync` and `agent-harness` so their public config projections, effective model, provider settings, and runtime services all derive from one resolved profile.
- Migrate agent-harness to source-preserving domain-overlay composition, keeping harness-owned gate, persistence, authority, validation, budget, and retention sections outside the global LLM merge.
- Converge provider/model configuration toward the native CLI pattern: YAML `providers.*.auth_env` as credential declaration, YAML `models.*` as named aliases, YAML `defaults.model` as selected alias.

## What Was Not Part of This Change

- Provider credential migration or copying between runtimes.
- Forcing `prime-agent` or `claude-code-provider-adapter` through the Python/Pydantic-AI model factory.
- Non-LLM fields in `TDTSettings` and `agent_core.foundation.Settings`.
- Scheduler, skills, memory, hooks, or domain workflow semantics except where needed to consume the resolved profile.
- Modifying Claude Code's `~/.claude/settings.json` — that is a separate native runtime configuration surface governed by the `claude-code-provider-profile-resolution` change.

## Boundary Statement

Claude Code's `~/.claude/settings.json` is a separate native runtime configuration surface. The v2 resolver governs Python agent consumers and CLI projections. The two systems may share conceptual provider/model metadata but must not share credentials or assume identical precedence.

## Execution, Acceptance, and Lifecycle Gates

The change is not archive-ready until:

1. The three custom provider credentials are registered in the environment-key registry (interim unblocker) and focused tests pass.
2. The YAML provider/model/default schema is defined and implemented in `tdt-core`.
3. `auth_env` support replaces direct `api_key_env` references in provider configuration.
4. The registry is retired or reduced to generic schema validation.
5. Full downstream consumer test suites pass in an isolated `TDT_HOME` environment.
6. CLI-provider integrations for `ai-harness-skills` and `ai-review` are implemented, tested, and evidence is captured — or explicitly de-scoped from this change.
7. The evidence manifest covers live streaming and non-streaming paths, direct-provider versus adapter scope, and stale task/doc-count reconciliation.

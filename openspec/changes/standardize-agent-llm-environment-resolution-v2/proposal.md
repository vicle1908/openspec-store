## Why

The agent ecosystem had no single executable contract for resolving LLM models, provider metadata, and environment-backed secrets. Existing main specs conflicted, direct consumers exposed different effective values, and two untracked planning drafts overlapped an already archived change. This corrective change established one source-aware resolution boundary.

## What Changes

- Added a canonical, typed resolved-agent-profile API in `tdt-core` that returns immutable effective model/runtime/provider data plus redacted source provenance.
- Made the precedence contract executable: explicit run override > consumer-specific process environment > shared model environment > per-agent YAML > global YAML > defaults.
- Made `tdt-core` the sole owner of `TDT_HOME`, dotenv/profile loading, secure YAML mapping, agent-overlay policy, path containment, cache invalidation, and environment-key metadata.
- Made `agent-core` consume a resolved profile and construct Pydantic-AI models without reading YAML or dotenv files.
- Corrected `agent-docs-sync` and `agent-harness` so their public config projections, effective model, provider settings, and runtime services all derive from one resolved profile.
- Migrated agent-harness to source-preserving domain-overlay composition, keeping harness-owned gate, persistence, authority, validation, budget, and retention sections outside the global LLM merge.

## What Remains (not yet implemented or verified)

- Custom provider credential keys (`HERMES_CUSTOM_GIAODUC_API_KEY`, `HERMES_CUSTOM_SHOPAPIKEY_API_KEY`, `HERMES_CUSTOM_COCKPIT_API_KEY`) are not registered in the `tdt-core` environment-key registry. This blocks all downstream consumer test suites.
- CLI adapter integrations for `ai-harness-skills` and `ai-review` are not implemented. The `project_cli_profile()` API exists in `tdt-core` but no consumer repos consume it.
- Cross-repository contract tests, isolated `TDT_HOME` fixture validation, live LLM acceptance, and full downstream suite validation are not complete.

## What Was Not Part of This Change

- Provider credential migration or copying between runtimes.
- Forcing `prime-agent` or `claude-code-provider-adapter` through the Python/Pydantic-AI model factory.
- Non-LLM fields in `TDTSettings` and `agent_core.foundation.Settings`.
- Scheduler, skills, memory, hooks, or domain workflow semantics except where needed to consume the resolved profile.

## Execution, Acceptance, and Lifecycle Gates

The change is not archive-ready until:

1. The three custom provider credentials are registered in the environment-key registry with `secret: true`, one provider binding each, and focused tests.
2. Full downstream consumer test suites pass in an isolated `TDT_HOME` environment.
3. CLI-provider integrations for `ai-harness-skills` and `ai-review` are implemented, tested, and evidence is captured — or explicitly de-scoped from this change.
4. The evidence manifest covers live streaming and non-streaming paths, direct-provider versus adapter scope, and stale task/doc-count reconciliation.

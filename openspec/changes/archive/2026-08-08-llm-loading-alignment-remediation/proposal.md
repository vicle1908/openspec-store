# Remediate LLM Loading and CLI-Agent Verification Findings

## Why

The post-migration review found several alignment gaps in the native pydantic-ai model-loading path:

- `api_mode` can be paired with an incompatible model-kind prefix without a clear failure.
- The `fable-5` provider-prefix mapping is ambiguous because `fable-5` is also a model name.
- The configured fallback list is parsed into settings but is not used by the agent-core CLI runtime.
- The configuration template and provider documentation contain stale gateway settings, incomplete routing examples, and invalid YAML placeholders.
- The previous external coding-agent review was not reproducible: some runs used Hermes delegation instead of the requested CLIs, stale processes exhausted file descriptors, Pi stalled during MCP-tool registration, and Codex inherited open stdin.

## What Changes

- Make provider resolution configuration-driven for provider-specific model names while keeping model-kind prefixes authoritative for API endpoint selection.
- Remove the ambiguous `fable-5` prefix shortcut and add explicit `model_names` provider routing for cockpit.
- Reject incompatible `api_mode`/model-prefix combinations with an actionable error before model construction.
- Wire `model.fallback` into the agent-core CLI runtime using the native `FallbackModel` factory.
- Align configuration templates, docs, canonical specs, and tests with the implemented loading behavior.
- Document and verify the external CLI-agent invocation requirements and failure modes without storing credentials.

## Scope

- `agent-core` model factory, CLI runtime, tests, configuration template, and docs.
- Shared OpenSpec canonical model-resolution spec and this change's delta spec.
- User-owned CLI-agent skills only where the verified invocation behavior is stale or incomplete.

## Out of Scope

- Changing pydantic-ai's model-kind or endpoint semantics.
- Live provider cutovers, credential rotation, or changes to provider secrets.
- Replacing the external CLIs or their upstream configuration.

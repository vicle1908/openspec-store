# Tasks: TDT Config Consumer Alignment

## Investigation and Review

- [x] Verify raw `~/.tdt/config.yaml` identifiers and provider entries without exposing secrets.
- [x] Verify `TDT_HOME`, environment, YAML, and default precedence in agent-core.
- [x] Review model/provider/API-mode/fallback resolution with Claude Code.
- [x] Review SDK, templates, and documentation consistency with Codex.
- [x] Record Goose as unavailable after executable lookup failed; do not count it as a review.

## RED and GREEN Implementation

- [x] Add focused tests for CLI runtime model-settings extraction.
- [x] Reuse the SDK model-settings builder so provider-specific extras are flattened.
- [x] Pass configured model settings to `BaseAgent.run(model_settings=...)`.
- [x] Inject configured thinking through the public Thinking capability.
- [x] Preserve positional native `FallbackModel` construction.
- [x] Remove the legacy `gateway:` YAML fallback from `load_settings()`.

## Documentation and Consistency

- [x] Correct default `api_mode` documentation to describe model-prefix inference.
- [x] Consolidate duplicate provider failover guidance.
- [x] Remove translated/corrupted model identifiers from owned tests and change artifacts.
- [x] Align proposal, design, tasks, and delta specs with the implemented pydantic-ai API.

## Quality Gates

- [x] Focused model/CLI tests pass.
- [x] Agent-core full tests pass.
- [x] Agent-docs-sync full tests pass.
- [x] Agent-harness full tests pass.
- [x] Ruff passes in all three repositories.
- [x] Strict mypy passes in all three repositories.
- [x] Focused OpenSpec change validation passes.
- [x] Archive the completed change.
- [x] Commit the archived change and merged specification in the shared store.

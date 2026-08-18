## ADDED Requirements

### Requirement: Profile resolution and launcher routing own distinct surfaces

This capability SHALL own the persistent credential-free defaults surface: `~/.claude/settings.json` global defaults, `apiKeyHelper` credential retrieval, and per-provider profile files under `~/.claude/profiles/`. The `claude-code-provider-routing` capability SHALL own the per-provider launcher functions that select a profile via `claude --settings <profile>` and pass a default model via `--model`. Model-selection precedence SHALL be: an explicit `--model` CLI flag, then the `--settings` profile file selected by the launcher, then the global `~/.claude/settings.json`. Neither capability SHALL claim authority over the other's surface.

#### Scenario: Global settings provide credential-free defaults

- **WHEN** `~/.claude/settings.json` is loaded for a bare invocation
- **THEN** it SHALL provide the default provider model, base URL, and effort without containing any credential values

#### Scenario: apiKeyHelper is the sole credential boundary

- **WHEN** Claude Code requires a bearer token
- **THEN** it SHALL obtain it by invoking the configured `apiKeyHelper`
- **AND** no credential value SHALL appear in settings files or profile files

#### Scenario: Launcher-selected profile overrides global settings

- **GIVEN** a provider launcher invokes `claude --settings <profile.json>`
- **WHEN** Claude Code starts from that launcher
- **THEN** the selected profile SHALL win for that session over the global settings file

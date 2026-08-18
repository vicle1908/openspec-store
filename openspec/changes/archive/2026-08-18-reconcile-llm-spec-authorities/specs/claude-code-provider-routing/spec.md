## ADDED Requirements

### Requirement: Launcher routing and profile resolution own distinct surfaces

This capability SHALL own the per-provider launcher functions: each launcher selects a provider profile via `claude --settings <profile>` and passes a default model via `--model`, sets the provider base URL, and unsets `ANTHROPIC_AUTH_TOKEN` so that `apiKeyHelper` is the sole credential boundary. The `claude-code-provider-profile-resolution` capability SHALL own the persistent credential-free defaults surface: `~/.claude/settings.json` global defaults, `apiKeyHelper` credential retrieval, and per-provider profile files under `~/.claude/profiles/`. Model-selection precedence SHALL be: an explicit `--model` CLI flag, then the `--settings` profile file selected by the launcher, then the global `~/.claude/settings.json`. Neither capability SHALL claim authority over the other's surface.

#### Scenario: Launcher selects a profile via --settings

- **GIVEN** a provider launcher invokes `claude --settings <profile.json> --model <alias>`
- **WHEN** Claude Code starts from that launcher
- **THEN** the selected profile file SHALL take precedence over the global settings file for that session
- **AND** the explicit `--model` flag SHALL take precedence over the profile's own model field
- **AND** the global settings file SHALL remain unchanged

#### Scenario: Profile file overrides global settings

- **WHEN** Claude Code is invoked with `--settings` pointing at a provider profile
- **THEN** the profile's model, base URL, effort, and apiKeyHelper SHALL take precedence over the global settings file

#### Scenario: Bare invocation uses global defaults

- **WHEN** Claude Code is invoked without a launcher or `--settings` profile
- **THEN** the global settings file defaults SHALL apply

# Proposal

## Why

The workspace previously installed Kimi via an outdated Homebrew formula (`kimi-code` 2.1.1) with legacy artifacts in `~/.kimi`. Upstream Moonshot AI officially publishes standalone native releases (v2.2.0) with an integrated migration engine into `~/.kimi-code`. Additionally, the workspace coding agent standard requires all terminal assistants to route their default model to the high-throughput, context-cached OmniRoute combo `gemini-3.8-flash-high`. Migrating Kimi to the official standalone distribution, executing the legacy data migration, and configuring its default model to `gemini-3.8-flash-high` brings Kimi into full compliance with workspace standards.

## What Changes

- Uninstall the outdated Homebrew `kimi-code` (v2.1.1) package and remove ad-hoc binary symlinks to enforce single-owner toolchain precedence.
- Install the official standalone Moonshot AI native binary (v2.2.0) into `~/.kimi-code/bin/kimi` using the official installer.
- Configure clean, consistent PATH precedence in `~/.zprofile` and `~/.zshrc` so `kimi` resolves strictly to `~/.kimi-code/bin/kimi`.
- Execute full legacy migration from `~/.kimi` to `~/.kimi-code` via `kimi migrate --run`, migrating sessions, MCP servers, and history with completion markers.
- Configure `~/.kimi-code/config.toml` (hardened to mode 0600) with `default_model = "gemini-3.8-flash-high"` backed by `omniroute-anthropic` (`http://localhost:20128`) with 1M context window and thinking/tool_use capabilities.
- Validate end-to-end execution with non-interactive CLI inference and verify OmniRoute gateway token logs.

## Capabilities

### New Capabilities
<!-- None -->

### Modified Capabilities
- `omniroute-agent-cli-routing`: Verifies that `kimi-code` routes its default model to `gemini-3.8-flash-high` via OmniRoute.
- `portable-workstation-toolchain`: Documents vendor-supported standalone installation for `kimi-code` under `~/.kimi-code/bin`.

## Impact

- Affected systems: `~/.kimi-code/`, `~/.zprofile`, `~/.zshrc`, Homebrew Cellar.
- Dependencies: OmniRoute gateway running on `localhost:20128`.
- Non-goals: Modifying upstream Moonshot cloud accounts or altering unrelated coding agent profiles.

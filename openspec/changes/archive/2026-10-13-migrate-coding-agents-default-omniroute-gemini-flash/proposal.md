# Proposal: Migrate Coding Agents and CLI Default Models to OmniRoute Gemini 3.8 Flash High

## Why

Coding agent CLI tools across the workstation currently use divergent default model combinations across multiple providers. Standardizing all supported coding agents and CLI profiles on the local OmniRoute gateway using the `gemini-3.8-flash-high` combo unifies agent reasoning performance, simplifies routing, and maximizes throughput while preserving Hermes's native Mixture of Agents (MoA) configuration.

## What Changes

- Update remaining coding agents and editor configurations to use OmniRoute's `gemini-3.8-flash-high` as their primary default model:
  - **Kimi Code (`~/.kimi-code/config.toml`)**: Add OmniRoute model mapping for `gemini-3.8-flash-high` and switch `default_model` from `sh-claude-fable` to `omniroute-gemini-flash`.
  - **Zed Editor (`~/.config/zed/settings.json`)**: Update `assistant.default_model` to `agy/gemini-3.8-flash-high` under the `omniroute` provider.
  - **Claude Code (`~/.claude/profiles/omniroute-pm.json`)**: Update default profile model and environment targets from `pm/Claude-Fable` to `gemini-3.8-flash-high`.
- Verify and document previously migrated agents that already default to OmniRoute `gemini-3.8-flash-high`:
  - **Codex CLI (`~/.codex/config.toml`)**
  - **Oh My Pi / OMP (`~/.omp/agent/config.yml`)**
  - **Pi (`~/.pi/agent/settings.json`)**
  - **Goose CLI (`~/.config/goose/config.yaml`)**
  - **Grok CLI (`~/.grok/config.toml`)**
  - **OpenCode (`~/.config/opencode/opencode.json`)**
  - **Prime Agent (`~/.prime/agent/settings.json`)**
  - **Droid (`~/.factory/settings.json`)**
- Explicitly preserve **Hermes Agent (`~/.hermes/config.yaml`)** on its existing native MoA (Mixture of Agents) default architecture with `omniroute:gemini-3.8-flash-high[reasoning=xhigh]` aggregator.

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `omniroute-agent-cli-routing`: Expand default routing to mandate `gemini-3.8-flash-high` as the default model across all supported coding agents and CLIs (including Kimi Code, Zed, Claude Code profile, Codex, OMP, Pi, Goose, Grok, OpenCode, Prime Agent, Droid) while explicitly preserving Hermes native MoA architecture.

## Impact

- CLI and editor configurations: `~/.kimi-code/config.toml`, `~/.config/zed/settings.json`, `~/.claude/profiles/omniroute-pm.json`.
- Mode 600 permission preservation and atomic backups for altered configuration files.
- OmniRoute gateway endpoints verified live on port 20128 (`/v1/responses`, `/v1/chat/completions`, `/v1/messages`).
- Zero regressions to Hermes configuration (`~/.hermes/config.yaml`), maintaining `model.provider: moa`.

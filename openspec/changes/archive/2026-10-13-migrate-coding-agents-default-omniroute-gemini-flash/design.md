# Design: Standardize Coding Agent Default Models to OmniRoute Gemini 3.8 Flash High

## Context

See `proposal.md` for motivation. Coding agent configurations are distributed across user-level configuration directories (`~/.codex`, `~/.omp`, `~/.pi`, `~/.config/goose`, `~/.grok`, `~/.config/opencode`, `~/.prime`, `~/.factory`, `~/.kimi-code`, `~/.config/zed`, and `~/.claude`). Several agents were previously configured to use `omniroute` and `gemini-3.8-flash-high`, while Kimi Code, Zed, and the Claude Code OmniRoute profile remained on divergent legacy providers (`shopapikey`, `cockpit`, `phanmemvip`).

OmniRoute serves:
- OpenAI Responses API at `http://localhost:20128/v1` (with `/v1/responses`)
- OpenAI Chat Completions API at `http://localhost:20128/v1` (and `http://localhost:20128/chat/completions`)
- Anthropic Messages API at `http://localhost:20128/v1/messages`

Live probes have confirmed that `gemini-3.8-flash-high` responds cleanly across all three endpoints.

## Goals / Non-Goals

**Goals:**
- Unify default model selection across all coding agents and CLI profiles to `gemini-3.8-flash-high` under the local OmniRoute gateway (`http://localhost:20128`).
- Update the remaining unmigrated targets (`~/.kimi-code/config.toml`, `~/.config/zed/settings.json`, and `~/.claude/profiles/omniroute-pm.json`).
- Ensure all updated files have atomic mode-600 backups before mutation and pass JSON/TOML syntax validation.
- Preserve all existing secondary/fallback providers and existing configuration settings.
- Maintain Hermes Agent's existing native MoA (Mixture of Agents) setup unchanged, with `omniroute:gemini-3.8-flash-high[reasoning=xhigh]` as aggregator.

**Non-Goals:**
- Modifying Hermes Agent's default provider from `moa` to direct `omniroute`.
- Removing existing secondary models or fallback chains from any coding agent.
- Modifying upstream agent binaries or npm/pip/cargo packages.

## Decisions

1. **Protocol Dialect Mapping per Agent**:
   - **Kimi Code (`~/.kimi-code/config.toml`)**: Uses OpenAI-compatible chat backend via `[providers.omniroute]` (`http://localhost:20128/v1`). Add `[models.omniroute-gemini-flash]` with `model = "gemini-3.8-flash-high"` and set `default_model = "omniroute-gemini-flash"`.
   - **Zed (`~/.config/zed/settings.json`)**: Uses `omniroute` provider with `agy/gemini-3.8-flash-high`. Set `assistant.default_model` to `{ "provider": "omniroute", "model": "agy/gemini-3.8-flash-high", "enable_thinking": true }`.
   - **Claude Code (`~/.claude/profiles/omniroute-pm.json`)**: Uses Anthropic Messages format routed to OmniRoute (`http://localhost:20128`). Set `ANTHROPIC_MODEL` and related model overrides to `gemini-3.8-flash-high`.
   - **Codex, OMP, Pi, Goose, Grok, OpenCode, Prime Agent, Droid**: Retain confirmed active default configuration pointing to `gemini-3.8-flash-high`.

2. **Credential and Permission Preservation**:
   - Configuration files containing keys (or mode 600 permissions) retain strict permissions `chmod 600`.
   - Backups created prior to mutation using `.bak-<timestamp>` format with mode 600.

3. **Hermes MoA Invariant**:
   - Keep `~/.hermes/config.yaml` untouched; `model.default` remains `default` with `model.provider: moa`.

## Risks / Trade-offs

- **[Risk]** Syntax error or schema rejection during agent launch.  
  → **Mitigation**: Create pre-mutation backups; run parse validation immediately after file modification.
- **[Risk]** Token limit or thinking parameter differences across dialects.  
  → **Mitigation**: Set explicit `contextWindow: 1000000` and `reasoning: true` / `default_effort: high` matching OmniRoute's verified capabilities.
- **[Risk]** Unintentional override of Hermes Agent MoA architecture.  
  → **Mitigation**: Strictly exclude `~/.hermes/config.yaml` from default provider modification; verify Hermes config state post-migration.

## Migration Plan

1. Create pre-mutation mode-600 backups for `~/.kimi-code/config.toml`, `~/.config/zed/settings.json`, and `~/.claude/profiles/omniroute-pm.json`.
2. Apply configuration updates to each target.
3. Validate syntax (TOML / JSON parsing) and permissions.
4. Execute live sentinel calls / test queries to verify model resolution.
5. Record verification evidence and update OpenSpec tasks.

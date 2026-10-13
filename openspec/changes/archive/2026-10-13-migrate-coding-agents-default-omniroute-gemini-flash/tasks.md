# Tasks: Migrate Coding Agent Defaults to OmniRoute Gemini 3.8 Flash High

## 1. Pre-flight Verification and Backups

- [x] 1.1 Verify live OmniRoute endpoints on port 20128 for `gemini-3.8-flash-high` across OpenAI Responses, Chat Completions, and Anthropic Messages by running live HTTP probes
- [x] 1.2 Create atomic mode-600 backups of target configuration files (`~/.kimi-code/config.toml`, `~/.config/zed/settings.json`, `~/.claude/profiles/omniroute-pm.json`) and verify backup existence and permissions

## 2. Configuration Migration to Default OmniRoute Gemini 3.8 Flash High

- [x] 2.1 Update Kimi Code configuration (`~/.kimi-code/config.toml`) to add the `omniroute-gemini-flash` model mapping and set `default_model = "omniroute-gemini-flash"`, verifying clean TOML parse
- [x] 2.2 Update Zed configuration (`~/.config/zed/settings.json`) to set `assistant.default_model` to `agy/gemini-3.8-flash-high` under the `omniroute` provider, verifying clean JSON parse
- [x] 2.3 Update Claude Code profile (`~/.claude/profiles/omniroute-pm.json`) to route `gemini-3.8-flash-high`, verifying clean JSON parse
- [x] 2.4 Configure Continue configuration (`~/.continue/config.json`) to set `gemini-3.8-flash-high` via OmniRoute as the default model and autocomplete model

## 3. Consistency Audit and Preservation Gates

- [x] 3.1 Verify existing coding agents (`codex`, `omp`, `pi`, `goose`, `grok`, `opencode`, `prime-agent`, `droid`) preserve their configured default `gemini-3.8-flash-high` OmniRoute routing
- [x] 3.2 Verify Hermes Agent configuration (`~/.hermes/config.yaml`) remains strictly preserved on `model.provider: moa` with native MoA aggregator routing
- [x] 3.3 Validate the complete OpenSpec change strictly using `openspec validate migrate-coding-agents-default-omniroute-gemini-flash --store openspec-store --strict`

# Spec Delta

## ADDED Requirements

### Requirement: Claude Code Omniroute Launcher Cutover to Gemini 4 Neon
The `omniroute()` launcher function in `~/.zshrc` and its backing profile `~/.claude/profiles/omniroute-pm.json` on `iosteam-mac-mini` SHALL default to `gemini-4-neon` at `high` reasoning effort, while preserving CLI management subcommands and registering `gemini-4-neon` in `modelPicker.options`.

#### Scenario: Omniroute launcher defaults to Gemini 4 Neon
- **WHEN** `omniroute` is invoked in an interactive Zsh shell without subcommands or flags
- **THEN** it SHALL launch Claude Code using `--settings ~/.claude/profiles/omniroute-pm.json` with `--model gemini-4-neon`
- **AND** `~/.claude/profiles/omniroute-pm.json` SHALL set `model: "gemini-4-neon"` and `env.ANTHROPIC_MODEL: "gemini-4-neon"`
- **AND** `modelPicker.options` SHALL list `gemini-4-neon` (`512K`) as the primary fleet default option

### Requirement: Local OMP Claude Code Launcher Subagent Remapping
Workstation shell functions targeting the local OMP Auth-Gateway (`http://127.0.0.1:4000`) SHALL pass `--settings` with `modelOverrides` remapping `claude-*-haiku*` identifiers to `gemini-3.8-flash` and SHALL override `~/.claude/settings.json` `env` defaults to prevent fallback to `Claude-Fable[1m]` or `shopapikey-key.sh`.

#### Scenario: Local Claude launchers prevent Haiku and Fable 404 errors on Auth-Gateway
- **WHEN** `claude-neon`, `claude-hydrogen`, or `claude-argon` is invoked against `http://127.0.0.1:4000`
- **THEN** the launcher helper SHALL pass `--settings` containing `modelOverrides` that map `claude-haiku-4-5-20251001`, `claude-haiku-4-5`, `claude-3-5-haiku`, and `claude-3-5-haiku-20241022` to `'gemini-3.8-flash'`
- **AND** the launcher SHALL override `ANTHROPIC_BASE_URL` to `'http://127.0.0.1:4000'`, set `ANTHROPIC_DEFAULT_HAIKU_MODEL` and `CLAUDE_CODE_SUBAGENT_MODEL` to `'gemini-3.8-flash'`, and override `ANTHROPIC_DEFAULT_OPUS_MODEL` / `ANTHROPIC_DEFAULT_SONNET_MODEL` to the target Gemini 4 model
- **AND** spawning a fast subagent or summary request in that session SHALL succeed without returning `HTTP 404 Unknown model` or hitting `phanmemvip.shop`

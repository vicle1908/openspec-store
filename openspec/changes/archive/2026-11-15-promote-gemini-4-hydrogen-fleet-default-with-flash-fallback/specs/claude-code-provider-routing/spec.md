# Spec Delta: claude-code-provider-routing

## MODIFIED Requirements

### Requirement: Claude Code cockpit and omniroute launcher profiles match active OmniRoute bridge and Gemini combo

The Claude Code launcher functions in `~/.zshrc` and their backing profile files in `~/.claude/profiles/` SHALL align with the active OmniRoute deployment for `cockpit` (`:20129`) and `omniroute` (`:20129` / profile `omniroute-pm.json`) using `omniroute-key.sh` credential indirection, defaulting `omniroute` to `gemini-4-hydrogen` with `gemini-3.8-flash-high` retained in `modelPicker.options`.

#### Scenario: Cockpit launcher resolves OmniRoute bridge port 20129
- **WHEN** `cockpit` is invoked from an interactive Zsh shell or `~/.claude/profiles/cockpit.json` is inspected
- **THEN** `ANTHROPIC_BASE_URL` SHALL be `http://localhost:20129`
- **AND** `model` and `ANTHROPIC_CUSTOM_MODEL_OPTION` SHALL be `cockpit/gpt-5.6-luna` with `CLAUDE_CODE_EFFORT_LEVEL=max`

#### Scenario: Omniroute launcher resolves gemini-3.8-flash-high while delegating CLI subcommands
- **WHEN** `omniroute` is invoked in an interactive Zsh shell
- **THEN** CLI management subcommands (`health`, `models`, `providers`, `combo`, `keys`, `eval`, `logs`, `stats`, `cache`, `resilience`, `settings`) SHALL delegate to `command omniroute "$@"`
- **AND** bare or flag invocations SHALL launch Claude Code with `--settings ~/.claude/profiles/omniroute-pm.json` selecting `model: "gemini-4-hydrogen"` (with `gemini-3.8-flash-high` preserved in `modelPicker.options` and `modelOverrides` as fallback)

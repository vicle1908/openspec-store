# Spec Delta: omniroute-agent-skills

## MODIFIED Requirements

### Requirement: Interactive Zsh Function Subcommand Multiplexing

The workstation interactive shell environment in `~/.zshrc` SHALL multiplex the `omniroute()` shell function: when invoked with known CLI subcommands or informational flags (`health`, `models`, `providers`, `combo`, `combos`, `keys`, `resilience`, `doctor`, `serve`, `chat`, `repl`, `status`, `--help`, `-h`, `--version`, `-v`), it SHALL dispatch to `command omniroute "$@"`. When invoked without subcommands, it SHALL preserve the Claude Code launcher under the `omniroute-pm.json` profile defaulting to `gemini-4-hydrogen` (with `gemini-3.8-flash-high` retained as fallback).

#### Scenario: CLI subcommand dispatches to host binary
- **WHEN** a user enters `omniroute health` in an interactive zsh terminal
- **THEN** the shell dispatches to `command omniroute health`
- **AND** server health output is displayed in the terminal

#### Scenario: Bare invocation preserves Claude Code launcher
- **WHEN** a user enters `omniroute` or `omniroute -p "prompt"` in an interactive zsh terminal
- **THEN** Claude Code launches with profile `omniroute-pm.json` and default model `gemini-4-hydrogen`

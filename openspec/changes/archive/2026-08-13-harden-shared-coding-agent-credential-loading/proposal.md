## Why

The current `.zprofile` sources the entire `~/.hermes/.env` (52 variables:
Discord tokens, Slack keys, Telegram tokens, debug flags, browser settings,
etc.) into every login shell. This was added to fix omp fresh-shell credential
loading, but it is broader than necessary and inappropriate as a reusable
coding-agent mechanism.

omp and other zsh-based coding agents (Claude Code, Codex, Grok, Kimi, Pi,
Prime Agent, OpenCode) only need the five `HERMES_CUSTOM_*_API_KEY` variables.
The remaining 47 variables are unrelated and should not leak into coding-agent
shells.

## What Changes

1. Replace the broad `.zprofile` source block with a call to the allowlisted
   loader at `~/.config/agent-llm/load-hermes-custom-credentials.zsh`.
2. Wire the same loader into `.zshenv` for non-login shell coverage.
3. The loader reads only assignments matching `HERMES_CUSTOM_[A-Z0-9_]+_API_KEY`
   from the existing mode-600 `~/.hermes/.env` using a constrained dotenv parser.

## Non-Goals

- No credential rotation or key-value changes.
- No modifications to `models.yml`, `config.yml`, Hermes provider config, or
  the Homebrew omp installation.
- No changes to OmniRoute credentials.
- No changes to how Hermes itself loads `.env` (Hermes reads it directly).

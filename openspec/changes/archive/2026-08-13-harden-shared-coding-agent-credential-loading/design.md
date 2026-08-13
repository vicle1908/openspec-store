# Design: harden-shared-coding-agent-credential-loading

## Problem

The `.zprofile` sources the entire `~/.hermes/.env` (52 variables including
Discord tokens, Slack keys, Telegram tokens, browser settings, debug flags)
into every login shell. This was added to fix omp fresh-shell credential
loading, but it leaks unrelated secrets and settings into coding-agent shells.

## Solution

Replace the broad source with a shared allowlisted parser that exports only
`HERMES_CUSTOM_*_API_KEY` variables. Wire through `.zshenv` for universal
zsh coverage (login and non-login shells).

### Shared loader

Path: `~/.config/agent-llm/load-hermes-custom-credentials.zsh`
Permissions: mode 700, owned by user

Architecture: **sourceable allowlisted dotenv parser**

The loader is sourced directly from `.zshenv`. It does NOT emit to stdout
and does NOT require `eval` of subprocess output.

Constrained dotenv grammar:
```
KEY=value
export KEY=value
KEY="value"
KEY='value'
```

Algorithm:
1. Check `~/.hermes/.env` exists and is readable; return 0 if not (nonfatal)
2. Read line by line with `IFS= read -r`
3. Strip carriage returns, skip empty lines and comments
4. Strip `export ` prefix if present
5. Split on first `=` — skip lines without `=`
6. Strip surrounding quotes (double or single) from value
7. Check key against allowlist: `[[ "$key" == HERMES_CUSTOM_*_API_KEY ]]`
8. Check parameter not already defined: `! (( ${+parameters[$key]} ))`
9. Export if both conditions pass
10. Unset all parser temporary variables

### .zshenv integration

```zsh
# Shared custom-provider credentials for coding-agent CLIs
_agent_llm_loader="$HOME/.config/agent-llm/load-hermes-custom-credentials.zsh"
if [[ -r "$_agent_llm_loader" ]]; then
  source "$_agent_llm_loader"
fi
unset _agent_llm_loader
```

Why `.zshenv` only:
- Covers both login (`-l`) and non-login shells
- omp and other zsh-launched coding agents inherit credentials
- Single integration point; no dual-source confusion

### .zprofile cleanup

Remove the entire broad source block (lines 14-18).

### Canonical credential source

- Path: `~/.hermes/.env`
- Permissions: mode 600
- Content: all Hermes configuration variables (messaging tokens, API keys,
  debug flags, etc.)
- The loader reads this file but exports only the allowlisted subset

### Supported consumers

Any zsh-based coding agent inherits credentials via `.zshenv`:
- omp (Homebrew, v17.2.15)
- Claude Code, Codex CLI, Grok Build CLI, Kimi Code CLI
- Pi CLI, Prime Agent CLI, OpenCode CLI

Does NOT provision:
- GUI-launched applications (Cockpit Tools.app, etc.)
- LaunchAgents running under a different user or shell
- Non-zsh processes (Python scripts, Docker containers, etc.)

### Allowlist contract

Variables matching `HERMES_CUSTOM_[A-Z0-9_]+_API_KEY` are exported.
The pattern avoids hardcoding a fixed count so future custom providers
work automatically.

## Security

- The loader never prints credential values to stdout or stderr
- Produces zero output when sourced (no `export KEY=value` emission)
- Pre-existing exported values in the parent shell take precedence
- Parser temporary variables are cleaned up after use

### Credential exposure

During earlier gate testing, credential values were printed into terminal
output and appear in session logs. If credential rotation is desired,
rotate these five keys:
- `HERMES_CUSTOM_ANTIGRAVITY_API_KEY`
- `HERMES_CUSTOM_COCKPIT_API_KEY`
- `HERMES_CUSTOM_GIAODUC_API_KEY`
- `HERMES_CUSTOM_LOCALHOST_51006_API_KEY`
- `HERMES_CUSTOM_SHOPAPIKEY_API_KEY`

## What does NOT change

- `~/.hermes/.env` (canonical source, untouched)
- `~/.omp/agent/models.yml` (providers, context windows, equivalence)
- `~/.omp/agent/config.yml` (roles, display settings)
- Hermes `config.yaml` (provider definitions)
- Claude Code profiles
- Homebrew omp installation
- Any credential values

## Rollback

Restore from `~/.omp/backups/zprofile-loader-20260813_133720/`:
```bash
cp ~/.omp/backups/zprofile-loader-20260813_133720/.zprofile ~/.zprofile
cp ~/.omp/backups/zprofile-loader-20260813_133720/.zshenv ~/.zshenv
```

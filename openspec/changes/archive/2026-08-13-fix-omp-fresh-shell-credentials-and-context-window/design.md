# Design: fix-omp-fresh-shell-credentials-and-context-window

## Credential loading

`~/.hermes/.env` is the existing canonical secret file and is mode 600. It
contains the three custom provider assignments:

- `HERMES_CUSTOM_SHOPAPIKEY_API_KEY`
- `HERMES_CUSTOM_GIAODUC_API_KEY`
- `HERMES_CUSTOM_COCKPIT_API_KEY`

No standard zsh startup file currently sources it. Add a guarded source to
`~/.zprofile`:

```zsh
# Hermes custom provider credentials (canonical secret file, mode 600)
if [[ -r "$HOME/.hermes/.env" ]]; then
  set -a
  source "$HOME/.hermes/.env"
  set +a
fi
```

This keeps values out of tracked configuration and makes them available to
fresh login shells. The guard avoids breaking shells when the file is absent.

## omp context metadata

Add `contextWindow: 1000000` only to these three model entries:

- `shopapikey/fable-5`
- `giaoduc/Advance`
- `cockpit/gpt-5.6-luna`

This matches Hermes's current `context_length: 1000000` declarations. Existing
OmniRoute per-model values remain unchanged because those are distinct models
with verified smaller windows.

## Role correction

Change only `config.yml`:

```yaml
modelRoles:
  default: cockpit/gpt-5.6-luna:high
```

Preserve `smol`, `slow`, `plan`, `commit`, and `task` exactly.

## Safety and rollback

Before mutation, capture hashes and mode for `.zprofile`, `models.yml`, and
`config.yml`. Write `.zprofile` atomically after syntax validation. Update the
two omp YAML files with parsed temporary files and atomic rename. If any
post-change check fails, restore all three files from timestamped backups.
Never print credential values.

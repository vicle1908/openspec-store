## Why

A genuinely clean login shell (`env -i ... zsh -lic`) resolves the Homebrew omp
binary but has none of the three custom provider key variables. The keys exist
in the canonical `~/.hermes/.env` (mode 600), but no standard zsh startup file
loads that file. The current Hermes process inherited the variables, masking
the fresh-shell defect.

Hermes config also declares a 1,000,000-token context window for Cockpit,
Giaoduc, and Shopapikey, while omp's corresponding model entries omit
`contextWindow`. The omp role default has drifted to `giaoduc/Advance`; the
intended native Cockpit default is `cockpit/gpt-5.6-luna:high`.

## What Changes

- Source `~/.hermes/.env` from `.zprofile` using a guarded, non-interactive
  source so fresh login shells receive the three custom key variables.
- Add `contextWindow: 1000000` to the three custom omp model entries.
- Restore `config.yml` default role to `cockpit/gpt-5.6-luna:high`.
- Preserve existing provider endpoints, transports, credentials, and all other
  role assignments.

## Non-Goals

- No credential rotation or key-value changes.
- No OmniRoute credential migration.
- No changes to Hermes config, Claude profiles, Cockpit Tools.app, Docker, or
  the Homebrew omp installation.

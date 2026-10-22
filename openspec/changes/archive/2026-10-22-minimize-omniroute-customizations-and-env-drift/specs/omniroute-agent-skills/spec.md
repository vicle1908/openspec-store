# Spec Delta

## ADDED Requirements

### Requirement: Host CLI bridge SHALL suppress Bun .env pre-loading and duplicate .env shadowing warnings

The host CLI bridge (`~/.local/bin/omniroute`) SHALL spawn `bun` with `--env-file=/dev/null`, export `OMNIROUTE_CLI_SKIP_DEFAULT_DATA_ENV=1` and `OMNIROUTE_CLI_SKIP_REPO_ENV=1`, provide an ephemeral `STORAGE_ENCRYPTION_KEY` default, and avoid running `bin/omniroute.mjs` with `/Users/androidteam/OmniRoute` as `process.cwd()` so pass-through CLI commands do not emit duplicate `.env` shadowing warnings on `stderr`.

#### Scenario: Pass-through CLI commands execute without duplicate .env warnings on stderr
- **WHEN** a pass-through CLI command (such as `omniroute health --json` or `omniroute models --output json`) is invoked via `~/.local/bin/omniroute`
- **THEN** `bun` SHALL be invoked with `--env-file=/dev/null`, `OMNIROUTE_CLI_SKIP_DEFAULT_DATA_ENV=1`, and `OMNIROUTE_CLI_SKIP_REPO_ENV=1`
- **AND** `stderr` SHALL contain zero `is ignored, ... set it first` `.env` shadowing warnings

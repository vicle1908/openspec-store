# Govern TDT_HOME Config and Environment

## Why

The agent ecosystem has a canonical `TDT_HOME` resolver, but configuration, secrets, state, logs, and credentials are still resolved and protected inconsistently across consumers.

The live `~/.tdt` audit found:

- `tdt-core` provides `tdt_root()`, `.env` loading, state helpers, and scheduler config loading.
- At least 18 source paths across `agent-core`, `agent-docs-sync`, `agent-harness`, `tdt-observability`, and `tdt-sheets` construct `~/.tdt` independently; several therefore ignore `TDT_HOME` or snapshot it at import time.
- Both `config.toml` and `config.yaml` contain scheduler configuration, creating ambiguous ownership and precedence.
- Scheduler database DSNs are present in general config files that are mode `0644`; the `~/.tdt` root is mode `0755`.
- `~/.tdt/google-service-account.json` is a broken symlink, while a second credential file exists with mode `0600`.
- Runtime material (logs, DuckDB/SQLite databases, PIDs, schedules, scripts, backups, and state) shares one root without a machine-checkable layout or permission audit.

## What Changes

- Expand the existing `tdt-env-loader-tdt-home` capability into the complete canonical `TDT_HOME` contract.
- Make `tdt-core` the provider of dynamically evaluated paths for config, credentials, schedules, logs, state, and per-application runtime files.
- Define explicit precedence profiles: unset or `development` keeps repo-local `.env` above process environment for backward compatibility; explicit `production` disables repo-local loading so process environment wins over `$TDT_HOME/.env`, typed non-secret config, and defaults.
- Separate secrets from non-secret config. General YAML/TOML files may contain secret references or environment variable names, never secret values.
- Add a redacting `tdt config doctor` audit for runtime layout, duplicate keys, broken links, and permissions.
- Add a separate workspace-bound `tdt config source-audit --workspace-root <path>` for repository conformance; runtime doctor remains usable from an installed wheel without sibling checkouts.
- Migrate consumers provider-first, with isolated worktrees and focused tests in each repository.
- Release `tdt-core` 0.3.x as the first version containing the provider contract, then set consumer dependency floors and regenerate lockfiles before import migration.
- Raise `tdt-observability` from Python 3.12+ to Python 3.14.x rather than adding a second path provider; treat this as an explicit compatibility break with release notes and rollback evidence.
- Repair the live `~/.tdt` layout only after backup, dry-run, and successful compatibility checks.

## Modified Capabilities

- `tdt-env-loader-tdt-home` — canonical resolution, precedence, layout, secret handling, diagnostics, and cross-repository adoption.

## New Capabilities

None. This change extends the existing capability that already owns `TDT_HOME` and environment loading.

## Ownership Boundaries

- `tdt-core`: path/config API, precedence, diagnostics, migration utility, contract tests.
- `agent-core`, `agent-docs-sync`, `agent-harness`, `tdt-observability`, `tdt-sheets`: replace private path construction with the provider API.
- `ai-harness-skills`: retain standalone runtime isolation while using the same root-resolution contract; it must not share agent-core or agent-harness state directories.
- `~/.tdt`: operator-owned runtime surface; never committed to a repository.
- `openspec-store`: normative capability and implementation plan only.

## Compatibility and Rollout

The default remains `~/.tdt`. Existing filenames remain readable during one compatibility window. `tdt-core` 0.3.x ships first; consumers migrate only after that version is available from the configured distribution channel and their metadata/locks require `>=0.3,<0.4`. `tdt-observability` moves to Python `>=3.14,<3.15` in the same reviewed rollout. The live migration is copy/verify/switch, not destructive move.

## Rollback

Restore consumer imports and dependency metadata/locks before rolling back `tdt-core`. Already published 0.3.x provider helpers remain compatibility exports; they are not removed during routine rollback. Reinstall pre-change consumer wheels in a clean environment to prove rollback. Restore the timestamped permission/config backup if the live doctor or smoke checks fail; do not delete legacy files during this change.

## Non-Goals

- Redesign Jira, report, mobile scan, or application-specific configuration schemas.
- Introduce Vault, a cloud secrets manager, or automated credential rotation.
- Rotate credentials solely because their storage location changes.
- Move logs or databases out of `TDT_HOME`.
- Merge the standalone `ai-harness-skills` runtime with the agent ecosystem.
- Change model/provider configuration unrelated to `TDT_HOME`.

## Evidence and References

- Existing implementation: `tdt_core.paths`, `tdt_core.env`, `tdt_core.config`, and scheduler settings.
- Existing capability: `openspec/specs/tdt-env-loader-tdt-home/spec.md`.
- [The Twelve-Factor App: Config](https://12factor.net/config) — deploy-varying configuration belongs outside code and should be orthogonal.
- [python-dotenv](https://bbc2.github.io/python-dotenv/) — documents `override` precedence and parsing behavior.
- [OWASP Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html) — standardization, least privilege, auditing, and lifecycle controls.
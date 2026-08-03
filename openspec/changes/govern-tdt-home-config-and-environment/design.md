# Design: Canonical TDT_HOME Control Plane

## Goals

1. Every participating process resolves the same root at call time.
2. Operators can explain the source and precedence of every effective setting without revealing values.
3. Secrets are not stored in general YAML/TOML config or emitted by the governed loader, parser, doctor, source-audit, or migration outputs.
4. Runtime subtrees have explicit ownership, permissions, and migration behavior.
5. Adoption is provider-first, reversible, and testable across repositories.

## Current State

Canonical provider: `tdt_core.paths.tdt_root()` re-evaluates `TDT_HOME`, expands `~`, and falls back to `~/.tdt`.

Environment behavior: `load_tdt_env()` loads `$TDT_HOME/.env` without overriding the process environment, then loads repo-local `./.env` with `override=True`. The latter can override production process values when a process starts in a repository checkout.

Config behavior: `config.toml` is read by `tdt_core.config`; `config.yaml` is read by scheduler and agent settings. Both currently carry scheduler settings, including a DSN.

Consumer drift: several modules construct `Path.home() / ".tdt"`, snapshot `TDT_HOME` at import, or implement their own expansion. `tdt-observability` and `tdt-sheets` are the clearest bypasses.

Live security state: root `0755`; `.env` and primary credential target `0600`; general config `0644`; canonical Google credential symlink broken. Logs and databases are mostly `0644` and should be treated as potentially sensitive operational data.

## Decision 1: One Dynamic Path Provider

Add typed helpers in `tdt-core`, all backed by `tdt_root()` and evaluated at call time:

- `tdt_config_path(format)`
- `tdt_credentials_path(name)`
- `tdt_schedules_dir()`
- `tdt_logs_dir()` / `tdt_log_path(app, name)`
- existing `tdt_state_path()` / `ensure_tdt_state_dir()`
- `tdt_runtime_path(app, kind, name)` for bounded app-owned files

No public constant may capture `TDT_HOME` at import time. Consumers may accept an explicit path for tests and dependency injection; their default must call the provider helper.

Why: this preserves the proven resolver and removes divergent implementations without creating another configuration framework.

## Decision 2: Explicit Precedence Profiles

Effective precedence for development compatibility:

1. repo-local `./.env` (explicit development override)
2. process environment
3. `$TDT_HOME/.env`
4. typed non-secret app config under `$TDT_HOME`
5. code defaults

Production-safe mode disables repo-local `.env`; process environment then wins. The mode is selected explicitly (`TDT_ENV_PROFILE=development|production`) rather than inferred from a directory name. Unknown profiles fail closed.

`load_tdt_env()` remains idempotent by default, but a test-only reset/context API supports isolated verification without mutating module internals. Diagnostics report source names and overridden key names, never values.

Why: this preserves the currently specified local override while preventing an accidental checkout-local override in production. It follows python-dotenv's documented distinction between `override=False` and `override=True`.

## Decision 3: Config Ownership and Secret References

- `config.toml`: legacy application/report configuration. It remains readable during migration but gains no new sections.
- `config.yaml`: canonical shared platform configuration for scheduler, skills, and agent framework settings.
- Application-specific files (`code-daily-scan.yaml`, observability files, schedule manifests): remain separate and typed by their owning packages.
- `.env` or injected process environment: secret values and deploy-specific credentials.

Secret-shaped keys in YAML/TOML (`*_secret`, `*_token`, `*_password`, `*_dsn`, `*_api_key`, credentials) must contain an environment reference such as `${SCHEDULER_POSTGRES_DSN}`, not a literal. The loader resolves references after environment loading and emits only typed missing-key errors.

Duplicate logical settings across `config.toml` and `config.yaml` are diagnostic errors until migrated. Scheduler settings become owned by `config.yaml`; legacy TOML reads warn for one release, then are removed in a later change.

Why: the live files prove that file mode alone is insufficient. Separating secret values makes config reviewable and aligns with Twelve-Factor and OWASP guidance.

## Decision 4: Layout and Permission Policy

Canonical layout:

- `$TDT_HOME/.env`: secret environment, `0600`
- `$TDT_HOME/credentials/`: credential files/links, directory `0700`, files/targets `0600`
- `$TDT_HOME/config.yaml` and non-secret app config: `0600` during the legacy mixed-content window; later policy may allow `0640`
- `$TDT_HOME/schedules/`: declarative manifests, directory `0700`, files `0600`
- `$TDT_HOME/state/<app>/`: durable app state, directories `0700`, files `0600`
- `$TDT_HOME/logs/<app>/`: logs, directories `0700`, files `0600`
- `$TDT_HOME/backups/`: operator backups, directory `0700`, files `0600`

The root is `0700`. Symlinks are allowed only when their resolved target exists, is a regular file, and meets the same permission policy. The migration supports the legacy root-level `google-service-account.json` name as a compatibility link to `credentials/google-service-account.json`.

Why: logs, state, and config can contain operational identifiers or payloads even if they are not credential stores. A uniform private default is safer and auditable on this single-user workstation.

## Decision 5: Redacting Doctor and Manifest

`tdt config doctor [--json] [--strict]` is a runtime/configuration check that requires no source checkout. It checks:

- root existence, ownership, and permissions;
- expected directories and file permissions;
- broken or escaping symlinks;
- parse validity for known YAML/TOML/.env files;
- duplicate logical config keys and secret literals in general config;
- effective source/key provenance with values redacted.

JSON output contains paths, key names, source classes, modes, and reason codes—never values or file contents. `--strict` exits non-zero on security, ambiguity, or broken-link findings.

`tdt config source-audit --workspace-root <path> [--json] [--strict]` is the separate source-governance command. The explicit workspace root contains the registered repositories. Missing repositories are failures in strict source-audit mode, while runtime doctor neither discovers nor requires repositories. The manifest names relative repository paths and allowed legacy exceptions with owner, reason, and expiry. Tests cover a complete workspace, a missing repository, an installed-wheel invocation outside a workspace, and an expired exception.

## Decision 6: Migration and Transaction Boundaries

Migration command: `tdt config migrate --dry-run` then `tdt config migrate --apply`.

Transaction boundary for live files:

1. acquire an exclusive migration lock under `$TDT_HOME/state/tdt-core/`;
2. create a timestamped backup manifest with path, mode, size, and SHA-256 (never content in logs);
3. create private directories;
4. copy credentials/config to temporary files in the destination;
5. fsync, parse, and validate targets;
6. atomically replace destinations and compatibility links;
7. tighten permissions after secret references resolve successfully;
8. run strict doctor and consumer smoke checks;
9. retain originals and backup for rollback; no deletion in this change.

A failure before step 6 leaves active paths unchanged. A failure afterward restores from the manifest before releasing the lock.

## Repository Rollout

1. `tdt-core`: add contract tests, helpers, doctor, migration, and docs; bump to the first containing version `0.3.0`; build and publish its wheel to the configured internal distribution channel; verify installation from that channel without sibling source paths.
2. Direct dependents currently using editable `tdt-core`: `agent-core`, `agent-docs-sync`, `agent-harness`. Add runtime floor `tdt-core>=0.3,<0.4`, retain the editable source only for local development, regenerate locks, and prove clean installs resolve the published wheel.
3. `tdt-observability`: explicitly raise Python support from `>=3.12` to `>=3.14,<3.15`, add `tdt-core>=0.3,<0.4`, regenerate its lock, and document the breaking floor change. `tdt-sheets` already targets 3.14 and adds the same provider floor. Optional-import fallback is forbidden for the required path contract.
4. `ai-harness-skills`: either adopt a tiny public provider dependency or retain its local resolver behind conformance tests. Because it is standalone, it must continue using `$TDT_HOME/ai-harness` and never agent runtime state paths.
5. Live `~/.tdt`: dry-run, backup, apply, strict doctor, and smoke verification only after all code changes pass.

Every implementation repository uses its own feature worktree. No two writers own the same repository concurrently.

## Verification Strategy

- Provider RED/GREEN unit tests for resolution, tilde/empty values, runtime reevaluation, profiles, precedence, redaction, permission findings, symlink containment, and rollback.
- Cross-repo AST audit for direct `~/.tdt` construction; explicit approved exceptions only.
- Full `uv run pytest`, Ruff, and strict mypy in every changed repo.
- Build/publish verification for `tdt-core` 0.3.0 and clean installs of every consumer from the configured distribution channel so editable siblings cannot mask version-floor or metadata errors.
- Release rollback rehearsal: install pre-change consumer metadata/wheels against the retained legacy path behavior, then reinstall migrated consumers; published provider helpers remain available throughout.
- Temporary-home end-to-end test: generate a representative legacy tree, dry-run, apply, run strict doctor, run consumer smoke commands, then rollback and compare hashes/modes.
- Live-home migration only after the synthetic end-to-end test passes twice.

## Risks and Mitigations

- Import cycles from making low-level packages depend on `tdt-core`: inspect dependency metadata first; keep the provider module dependency-free within `tdt-core`, and add explicit dependencies only where architecture permits.
- Python compatibility break in `tdt-observability`: raise its declared/runtime/type-check floor to 3.14, document it in release notes, test metadata rejection on 3.12/3.13, and retain the pre-change wheel as the rollback artifact.
- Production behavior change from local `.env`: default remains compatible; production-safe profile is explicit and covered by tests.
- Permission changes break launchd/container users: doctor reports ownership and process identity before apply; migration refuses foreign-owned paths.
- Broken credential repair points at the wrong key: migration never guesses among multiple credentials; an explicit operator-selected source is required if the canonical target is absent.
- Secret values leak in diagnostics/tests: golden tests scan stdout, stderr, JSON, logs, and exceptions for seeded canary values.
- Editable dependencies mask release floors: clean wheel/install checks are mandatory before consumer rollout.
- No configured package distribution channel: implementation stops after building/signing the provider wheel and requests the missing release authority; consumers and live config are not migrated.

## Rejected Alternatives

- Leave each consumer's resolver in place: preserves current drift and makes `TDT_HOME` unreliable.
- Put all config into one YAML: mixes unrelated application domains and increases secret exposure blast radius.
- Make process environment the only source immediately: breaks the established local automation ecosystem.
- Tighten modes without moving secret values: reduces local readability but leaves ambiguity, duplication, and accidental diagnostic leakage.
- Introduce a cloud secret manager now: valuable later, but materially expands scope and operational dependencies.
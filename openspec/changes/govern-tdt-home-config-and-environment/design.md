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

`TDT_HOME` MUST resolve to an absolute path after `~` expansion; relative paths are rejected. The root itself may be a symlink only when doctor opens and records its stable resolved directory target. That resolved directory descriptor becomes the canonical anchor; no-follow ancestor checks apply only below it, so the one validated root link is not re-rejected. Namespace arguments (`app`, `kind`) use allowlisted identifiers (`[a-z0-9][a-z0-9-]*`), and `kind` is an enum. A filename is a single basename matching `[A-Za-z0-9][A-Za-z0-9._-]*`; separators, NUL, empty names, `.`/`..`, and leading-dot names are rejected unless a dedicated helper owns a fixed hidden filename such as `.env`. Writes use descriptor-relative/no-follow operations from the anchor where supported, reject descendant symlink ancestors and non-regular/hard-linked secret targets, and revalidate the opened object against the anchor.

Why: this preserves the proven resolver and removes divergent implementations without creating another configuration framework.

## Decision 2: Explicit Precedence Profiles

Effective precedence for development compatibility:

1. repo-local `./.env` (explicit development override)
2. process environment
3. `$TDT_HOME/.env`
4. typed non-secret app config under `$TDT_HOME`
5. code defaults

An unset profile defaults to `development` so existing callers retain the current repo-local `.env` override without configuration changes. Explicit production-safe mode disables repo-local `.env`; process environment then wins. A set mode uses `TDT_ENV_PROFILE=development|production` rather than being inferred from a directory name. Unknown non-empty profiles fail closed.

`TDT_ENV_PROFILE` is read only from the inherited process environment before any `.env` file is opened. Neither `$TDT_HOME/.env`, repo-local `.env`, YAML, nor TOML may select or change the profile. Loading then has two distinct phases: select and load only the resolved home `.env`; afterwards, development mode may load repo-local `.env` with `override=True`. “No other home `.env`” never prohibits the separately governed repo-local development override.

`load_tdt_env()` uses a process-local re-entrant lock and a terminal initialized state so concurrent callers perform one complete load or observe its result; failed loads do not publish partial initialized state. A test-only isolation context acquires the same lock, refuses entry while another load/isolation context is active, snapshots/restores only keys it changes, and is unsupported for production concurrency. Diagnostics report source names and overridden key names, never values.

Why: the unset default preserves the currently specified local override for all existing callers, while an explicit production profile prevents accidental checkout-local overrides. It follows python-dotenv's documented distinction between `override=False` and `override=True`.

## Decision 3: Config Ownership and Secret References

- `config.toml`: legacy application/report configuration. It remains readable during migration but gains no new sections.
- `config.yaml`: canonical shared platform configuration for scheduler, skills, and agent framework settings.
- Application-specific files (`code-daily-scan.yaml`, observability files, schedule manifests): remain separate and typed by their owning packages.
- `.env` or injected process environment: secret values and deploy-specific credentials.

Secret-shaped keys in YAML/TOML (`*_secret`, `*_token`, `*_password`, `*_dsn`, `*_api_key`, credentials) must contain an environment reference such as `${SCHEDULER_POSTGRES_DSN}`, not a literal. The loader resolves references after environment loading and emits only typed missing-key errors.

The only supported reference grammar is the full scalar `${VAR_NAME}`, where `VAR_NAME` matches `[A-Z][A-Z0-9_]*`. Concatenation, defaults (`:-`), nested expansion, `$VAR`, and escaping are rejected. Classification is recursive and schema-aware; aliases are normalized to a canonical logical key before duplicate detection. The implementation maintains a committed ownership table mapping each shared logical key and alias to one typed model and one file surface.

Duplicate logical settings across `config.toml` and `config.yaml` are diagnostic errors until migrated. Scheduler settings become owned by `config.yaml`; legacy TOML reads warn for one release, then are removed in a later change.

The committed ownership/migration table is executable input, not prose. For each key it records aliases, legacy sources, canonical destination, secret classification, rewrite, and conflict policy. For scheduler keys: non-secret duplicates with equal normalized values remove the TOML copy; unequal values block apply for operator selection. A literal `postgres_dsn` is never copied into YAML: migration requires a selected existing process/`$TDT_HOME/.env` value, writes `${SCHEDULER_POSTGRES_DSN}`, and blocks when literal and environment values disagree or the referenced value is absent. Backups preserve the original bytes for rollback.

Why: the live files prove that file mode alone is insufficient. Separating secret values makes config reviewable and aligns with Twelve-Factor and OWASP guidance.

## Decision 4: Layout and Effective-Access Policy

Canonical layout:

- `$TDT_HOME/.env` and credential targets: readable only by verified runtime principals that require them.
- `$TDT_HOME/credentials/`: credential links and targets, with least-privilege traversal/read access.
- `$TDT_HOME/config.yaml`, schedules, state, logs, and backups: access derived from their declared reader/writer principals.

No fixed numeric mode is applied blindly. The doctor records host owner/group/ACL and the effective principals for launchd and Docker Compose. The current Compose app and scheduler run as container user `agent` over a host bind mount, so migration MUST prove traversal and required read/write access before tightening any mode. A default single-principal installation may use `0700` directories and `0600` files; shared host/container installations use the narrowest verified group/ACL mapping. Unknown or unmapped principals block apply.

Symlinks are allowed only when `lstat` identifies a link, its opened target is an approved regular file, ownership/access policy passes, and replacement races are detected. Explicit credential environment paths outside `$TDT_HOME/credentials` remain allowed only as declared external credential sources; doctor reports their metadata without enforcing root containment or reading content. The migration supports the legacy root-level `google-service-account.json` name as a compatibility link to `credentials/google-service-account.json`.

Why: logs, state, and config can contain operational identifiers or payloads even if they are not credential stores. Least privilege remains the goal, but effective access must include every verified host/container principal rather than assuming one numeric owner.

## Decision 5: Redacting Doctor and Manifest

The base `tdt-core` wheel owns a new Typer entrypoint `tdt = "tdt_core.cli:app"`. Typer and PyYAML become base runtime dependencies because doctor and config parsing must work without scheduler extras. `tdt_core.cli` owns the `config` group; doctor, source-audit, migrate, and recover are separate subcommands and modules.

`tdt config doctor [--json] [--strict]` is a runtime/configuration check that requires no source checkout. It checks:

- root existence, ownership, and permissions;
- expected directories and file permissions;
- broken or escaping symlinks;
- parse validity for known YAML/TOML/.env files;
- duplicate logical config keys and secret literals in general config;
- effective source/key provenance with values redacted.

JSON output contains paths, key names, source classes, modes, and reason codes—never values or file contents. `--strict` exits non-zero on security, ambiguity, or broken-link findings.

`tdt config source-audit --workspace-root <path> [--json] [--strict]` is the separate source-governance command. The explicit workspace root contains the registered repositories. Missing repositories are failures in strict source-audit mode, while runtime doctor neither discovers nor requires repositories. The manifest names relative repository paths and allowed legacy exceptions with owner, reason, and expiry. Tests cover a complete workspace, a missing repository, an installed-wheel invocation outside a workspace, and an expired exception.

Source audit never follows repository symlinks and excludes `.git`, virtual environments, dependency/vendor trees, caches, generated artifacts, `.env*`, credential/key files, runtime databases, logs, and `$TDT_HOME`. It analyzes Python AST plus shell/YAML/TOML/config literals using a value-free rule inventory; parser failures report path/rule/reason only and never source excerpts.

## Decision 6: Migration, Compatibility, and Recovery Boundaries

Migration command: `tdt config migrate --dry-run` then `tdt config migrate --apply`.

Transaction boundary for live files:

1. discover every configured writer/reader (launchd, scheduler container, observability poller/collector, report processes) and require verified quiescence or explicit shared-lock participation;
2. acquire the migration lock and create/fsync a durable journal with generation ID and `prepared` state;
3. create a timestamped backup manifest with path, link, owner/access metadata, size, and SHA-256 (never content in logs);
4. stage and fsync a complete destination generation, then validate parsing, links, and effective principals;
5. for each sorted path, fsync an `intent(path, old_digest, staged_digest)` record, replace, fsync its parent, verify the active digest, then fsync `completed(path, active_digest)`; after every path is complete, fsync `switched`;
6. run strict doctor and old/new consumer smoke checks, then fsync `committed`;
7. recovery is fixed: `prepared`/`staged` journals discard staging and keep the old generation; `switching` journals always roll back every path with an intent record in reverse order from backup copies, regardless of whether `completed` was recorded; `switched` reruns verification and either records `committed` or rolls back; `rolling_back` resumes reverse rollback; only `committed` is success-terminal and `rolled_back` is rollback-terminal;
8. retain originals and backup for rollback; no deletion in this change.

Atomic rename is per path, not a tree-wide transaction. Safety therefore comes from quiescence, backup copies, the fixed journal oracle above, idempotent recovery, and a path-by-path compatibility policy. Tests terminate the migrator before/after each intent, replace, directory fsync, completion record, and state transition.

A committed path map under `tdt-core` records, for every executable legacy path: repository/owner, old path, canonical helper/new path, reader/writer principals, read fallback, write target, compatibility mechanism (symlink, read-old/write-new, quiesced cutover, or explicit unsupported legacy reader), access policy, and removal milestone. Old and migrated consumers are tested against the same synthetic generation.

## Repository Rollout

1. `tdt-core`: add contract tests, helpers, CLI, doctor, source audit, migration/recovery, maps, and docs; bump to `0.3.0`; build an offline-complete local wheelhouse containing the provider plus locked runtime/transitive dependencies, record hashes, and verify with fresh cache-disabled installation without sibling source paths. Publish to Nexus only after a non-secret reachability/auth/authority preflight succeeds.
2. Direct provider importers add `tdt-core>=0.3,<0.4`. `agent-docs-sync` becomes a direct dependency because its source will import path helpers; editable sources remain only in `[tool.uv.sources]` for development. Clean-install verification uses copied metadata with editable source mappings excluded and `uv pip install --no-index --find-links <wheelhouse>`.
3. `tdt-observability`: explicitly raise Python support from `>=3.12` to `>=3.14,<3.15`, add `tdt-core>=0.3,<0.4`, regenerate its lock, and document the breaking floor change. `tdt-sheets` already targets 3.14 and adds the same provider floor. Optional-import fallback is forbidden for the required path contract.
4. Source-migration owners are the eleven repositories named in the proposal. `ai-review` and `jira-epic-report` are verification/classification consumers. The conformance manifest enumerates all fourteen non-provider repositories and promotes any newly detected executable bypass to migration ownership.
5. `ai-harness-skills` retains standalone `$TDT_HOME/ai-harness` isolation. If dependency review permits, it imports the provider; otherwise it implements a dependency-free `TdtRootContract` compatibility adapter generated/tested from the same contract vectors. Either route MUST conform for unset/empty, tilde, absolute-root rejection, dynamic reevaluation, filename validation, and containment semantics.
6. Release graph: `tdt-core` → `agent-core` → `agent-docs-sync`/`agent-harness`; independent consumers follow after provider verification. Rollback is the reverse downstream order while provider compatibility exports remain installed.
7. Deploy/restart migrated consumers and verify active versions plus `TDT_ENV_PROFILE=production` for production launchd/Compose processes before any live path switch.
8. Live `~/.tdt`: quiescence, dry-run, backup, journaled apply/recovery, strict doctor, Compose/launchd smoke, and consumer smoke verification only after all migrated consumers are active.

Every implementation repository uses its own feature worktree. No two writers own the same repository concurrently.

## Verification Strategy

- Provider RED/GREEN unit tests for resolution, tilde/empty values, runtime reevaluation, profiles, precedence, redaction, permission findings, symlink containment, and rollback.
- Cross-repo AST audit for direct `~/.tdt` construction; explicit approved exceptions only.
- Full `uv run pytest`, Ruff, and strict mypy in every changed repo.
- Build verification for `tdt-core` 0.3.0 and clean local-wheelhouse installs of every consumer so editable siblings cannot mask version-floor or metadata errors; Nexus publication is verified separately when its preflight is available.
- Release rollback rehearsal: install pre-change consumer metadata/wheels against retained legacy behavior, then reinstall migrated consumers; the verified provider artifact/helpers remain available throughout.
- Temporary-home end-to-end test: generate a representative legacy tree, dry-run, apply, run strict doctor, run consumer smoke commands, then rollback and compare hashes/modes.
- Live-home migration only after the synthetic end-to-end test passes twice.

## Risks and Mitigations

- Import cycles from making low-level packages depend on `tdt-core`: inspect dependency metadata first; keep the provider module dependency-free within `tdt-core`, and add explicit dependencies only where architecture permits.
- Python compatibility break in `tdt-observability`: raise its declared/runtime/type-check floor to 3.14, document it in release notes, test metadata rejection on 3.12/3.13, and retain the pre-change wheel as the rollback artifact.
- Python floor choice: `tdt-core` already declares `>=3.14,<3.15`, and the workspace standard is Python 3.14. This change intentionally aligns `tdt-observability` rather than creating a second compatibility provider. Supporting 3.12 would require a separately versioned low-level package and is outside this capability; the breaking floor remains explicit and reversible through the prior observability wheel.
- Production behavior change from local `.env`: default remains compatible; production-safe profile is explicit and covered by tests.
- Permission changes break launchd/container users: doctor reports ownership and process identity before apply; migration refuses foreign-owned paths.
- Broken credential repair points at the wrong key: migration never guesses among multiple credentials; an explicit operator-selected source is required if the canonical target is absent.
- Secret values leak in diagnostics/tests: golden tests scan stdout, stderr, JSON, logs, and exceptions for seeded canary values.
- Editable dependencies mask release floors: clean wheel/install checks are mandatory before consumer rollout.
- Unavailable Nexus: record the conditional external-release blocker and continue in-workspace migration/verification from the hashed offline-complete wheelhouse; no claim of Nexus publication is made.

## Rejected Alternatives

- Leave each consumer's resolver in place: preserves current drift and makes `TDT_HOME` unreliable.
- Put all config into one YAML: mixes unrelated application domains and increases secret exposure blast radius.
- Make process environment the only source immediately: breaks the established local automation ecosystem.
- Tighten modes without moving secret values: reduces local readability but leaves ambiguity, duplication, and accidental diagnostic leakage.
- Introduce a cloud secret manager now: valuable later, but materially expands scope and operational dependencies.
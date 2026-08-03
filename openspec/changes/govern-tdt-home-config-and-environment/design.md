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

### Blocker evidence and architectural correction

The first provider draft passed ordinary unit, lint, type, wheel, and clean-install gates but failed two independent fail-closed reviews and adversarial tests. The failures were architectural rather than isolated defects: the provider guessed consumer paths and writers before consumer manifests existed; migration accepted caller-asserted quiescence; recovery trusted mutable journal paths/records; pathname-based fallback operations broke the no-follow threat model; doctor tried to infer container access without deployment-owned evidence; and source audit treated its packaged manifest as optional.

This revision resets the implementation boundary. Existing draft code is evidence and may not be promoted task-by-task. The provider first implements a small security kernel, strict schemas, and synthetic contract vectors. Consumer/deployment owners then provide concrete facts. Only after those manifests are complete may the provider compile a migration plan and exercise apply/recovery. No task is complete merely because the prior draft contains code or a previously built wheel.

## Decision 1: One Dynamic Path Provider

Add typed helpers in `tdt-core`, all backed by `tdt_root()` and evaluated at call time:

- `tdt_config_path(format)`
- `tdt_credentials_path(name)`
- `tdt_schedules_dir()`
- `tdt_logs_dir()` / `tdt_log_path(app, name)`
- existing `tdt_state_path()` / `ensure_tdt_state_dir()`
- `tdt_runtime_path(app, kind, name)` for bounded app-owned files

No public constant may capture `TDT_HOME` at import time. Consumers may accept an explicit path for tests and dependency injection; their default must call the provider helper.

`TDT_HOME` MUST resolve to an absolute path after `~` expansion; relative paths are rejected. One explicitly configured final root symlink may be resolved before anchoring: the provider records the link's `lstat` identity and text for diagnostics, resolves its target to an absolute path, opens that target through the same component-walk policy, and thereafter trusts only the retained target descriptor/device/inode. Replacing the root link later cannot redirect the active operation; a later command must anchor again and report any changed link identity. Arbitrary symlinks in root ancestors are not implicitly trusted—deployment configuration must name an approved absolute anchor path or final root link. Every descendant path is a tuple of validated relative components: no absolute component, separator, NUL, empty string, `.` or `..`. Directory traversal opens each component relative to the retained parent descriptor with `O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC`; creation uses `mkdir(..., dir_fd=...)`, then reopens and `fstat`s the result. Files are opened relative to retained parent descriptors with `O_NOFOLLOW|O_CLOEXEC`; secret, credential, journal, plan, backup, and staged regular files require `st_nlink == 1`. Temporary writes use `O_CREAT|O_EXCL`, `fchmod`, complete writes, file `fsync`, descriptor-relative `os.rename(src_dir_fd=..., dst_dir_fd=...)`, destination-parent `fsync`, reopen, identity/type/link-count validation, and digest verification. Pathname-based `Path.resolve`, `rglob`, `shutil.copy*`, `symlink_to`, `replace`, or arbitrary journal paths are prohibited in the mutation/recovery trust boundary.

Root bootstrap is a separate operation from descendant creation. An existing root is opened and pinned directly. A missing default `~/.tdt` may be created only from an already-opened `$HOME` anchor that is a verified directory owned by the current host principal and satisfies the declared bootstrap policy. Any other missing root requires an explicit, existing approved bootstrap anchor supplied through a typed API/plan field; the requested root must be represented solely as validated relative components below that anchor. The kernel walks existing components and creates missing components one at a time with `mkdir(..., dir_fd=...)`, fsyncs the parent, reopens with `O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC`, and verifies type, identity, owner, and policy after every step. It never searches upward for an implicit ancestor or uses recursive pathname creation. A missing, replaced, symlinked, foreign, or policy-incompatible bootstrap anchor fails before creation.

Python 3.14.6 on this macOS host exposes `dir_fd` for `open`, `mkdir`, `rename`, `unlink`, `stat`, `chmod`, `readlink`, and `symlink`, plus `O_NOFOLLOW`, `O_NOFOLLOW_ANY`, `O_DIRECTORY`, and `O_CLOEXEC`. Absolute root/target opens use `O_NOFOLLOW_ANY` as defense in depth when the runtime exposes it; component-by-component `openat` semantics with `O_NOFOLLOW` and `fstat` remain the required baseline for precise traversal, creation, and recovery. Python does not expose macOS `O_RESOLVE_BENEATH`, `O_UNIQUE`, or `renameatx_np`; the implementation SHALL NOT hard-code undocumented numeric constants or add a ctypes syscall shim in this change. If neither the stronger flag nor the required baseline primitives are available on a future platform, mutation fails closed while read-only path construction remains available.

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

No fixed numeric mode is applied blindly. Each deployment owner publishes a principal manifest containing stable principal IDs, host UID/GID or a declared unmapped status, required per-path operations, and an adapter capable of executing a value-free access probe in the real launchd/container context. Doctor can prove the current host principal directly through descriptor-based operations; it MUST NOT claim to simulate another UID. Container or launchd access is proven only by fresh adapter evidence bound to root identity, plan digest, principal ID, operation set, and expiry. Unknown, unmapped, stale, unavailable, or failed probes block apply and leave modes unchanged. A default single-principal installation may use `0700` directories and `0600` files; shared installations use the narrowest verified group/ACL policy demonstrated by those probes.

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

`tdt config source-audit --workspace-root <path> [--json] [--strict]` is the separate source-governance command and consumes two layers. The provider wheel contains mandatory versioned registry data loaded through `importlib.resources`: schema versions, rule inventory, the closed-world fifteen participant IDs, each repository-owned manifest location, and required fields. It contains no guessed concrete include roots, deployment facts, exceptions, path rows, or live plan. Each participant repository owns a versioned concrete manifest at its registered location with identity marker, include roots/path families, exclusions, role, concrete path rows or an evidenced no-path declaration, exceptions, and deployment/principal references. Source audit validates the provider registry first, then loads each concrete manifest only from the explicit workspace root through the registered relative location. Missing data, invalid UTF-8/JSON, unknown versions/fields, duplicate IDs, unsafe paths, missing concrete manifests, malformed exceptions, or incomplete fields are operational failures before scanning. Unrelated sibling repositories are ignored; adding a participant requires a reviewed provider-registry and repository-manifest update. Every registered participant must exist as a non-symlink directory, match its declared identity marker, and provide a complete concrete manifest. Operational manifest/inventory/parser/traversal failures always exit non-zero; `--strict` additionally makes policy findings non-zero. Runtime doctor loads neither registry layer and remains workspace-independent.

Python analysis builds a scope-aware import/symbol table and recognizes `pathlib.Path`, `import pathlib as pl`, `from pathlib import Path as P`, `os`, aliased `os`, imported/aliased `getenv`, aliases of `os.environ`, subscripts, and `.get` only when lexical binding resolves to those symbols; shadowed aliases and unrelated dictionary `.get` calls are ignored. Module-level snapshots are a separate rule. Sink-aware literal analysis flags executable defaults/path construction such as Pydantic `Field(default=...)`, not docstrings, CLI help, logs, or remediation messages. Shell is parsed without execution through a bounded lexer; plist uses `plistlib`; YAML/TOML scanners visit bounded typed values and known configuration/default fields rather than splitting raw lines. Inputs must be regular non-symlink strict-UTF-8 files under bounded include roots and size/depth/node/alias limits. Exception metadata is validated once independently of findings; every exception requires a unique ID, exact registered repository-relative path/rule selector, owner, reason, and unexpired ISO date. Expired, malformed, duplicate, unknown-rule, out-of-scope, excluded-path, or orphan exceptions fail and cannot suppress operational findings.

Source audit never follows repository symlinks and excludes `.git`, virtual environments, dependency/vendor trees, caches, generated artifacts, `.env*`, credential/key files, runtime databases, logs, and `$TDT_HOME`. It analyzes Python AST plus shell/YAML/TOML/config literals using a value-free rule inventory; parser failures report path/rule/reason only and never source excerpts.

## Decision 6: Migration, Compatibility, and Recovery Boundaries

Migration has four distinct commands: `tdt config plan compile`, `tdt config migrate --dry-run --plan <plan>`, `tdt config migrate --apply --plan <plan>`, and `tdt config recover --generation <uuid>`. There is no `--quiesced` Boolean, arbitrary journal-path option, or mutable PID inventory.

Transaction boundary for live files:

1. Every consumer/deployment manifest declares concrete old/new relative paths, helper, compatibility behavior, declared owner/group/mode/ACL/xattr/flag policy, required read/write operations, reader/writer principals, launch adapter, lock participation, and value-free smoke verifier. Wildcards, placeholders, shell strings, arbitrary executable paths, and unknown adapters are rejected.
2. The plan compiler validates the complete manifest set, config ownership decisions, selected credential sources, and root identity; sorts operations canonically; and emits immutable JSON with schema version, plan UUID, root device/inode, manifest hashes, operation IDs, writer/principal/verifier IDs, declared metadata/access policies, and SHA-256 of canonical plan bytes. Apply recomputes this digest and accepts plan/journal control files only when invoking-user-owned, private, regular, and single-linked. Governed runtime paths are compared against their manifest-declared owner/group/mode/ACL/xattr/flag policy and required operations; valid shared group/ACL writers are allowed only when the metadata adapter and fresh principal attestations prove that exact policy. Foreign, overbroad, undeclared, or unprovable access fails before mutation.
3. At dry-run and again immediately before apply, registered adapters discover configured launchd/Compose/scheduler/observability/report writers from their real configuration and produce fresh attestations. Every writer must be stopped or prove participation in the same descriptor-anchored lock. PID existence alone and caller assertions are never evidence. Every declared principal must have a fresh access-probe attestation bound to plan digest and root identity.
4. Apply opens/locks the canonical migration lock before selecting or reading a journal, revalidates plan/root/evidence, creates a private generation directory by UUID, and writes a `prepared` journal header containing the plan bytes/digest and root identity. Recovery accepts only a UUID, opens the corresponding generation below the anchored `.tdt-migrations` directory, and validates owner, mode, type, link count, schema, and hash chain before interpreting records.
5. Every source is opened no-follow through the root anchor and `fstat`ed before copy. The backup/staging metadata records relative path, type, link text where applicable, device/inode, UID/GID, mode, size, and SHA-256. Copying occurs from the retained source descriptor to exclusive private files; source identity is rechecked after copy; copied digest/size are verified; each file and containing directory is fsynced. A registered macOS metadata adapter detects ACLs/xattrs/flags during planning. If any governed path has metadata the core cannot capture and restore through a tested adapter, plan compilation/apply fails closed; the core SHALL NOT claim exact ACL/xattr restoration or silently drop metadata.
6. For each sorted operation, append/durably sync a hash-chained `intent`, perform descriptor-relative replacement, fsync every affected source/destination parent, reopen/verify type/identity/link count/digest, then append/durably sync `completed`. After all operations, append/durably sync `switched`. Ordinary files and directories use `fsync`; journal state barriers additionally use macOS `fcntl.F_FULLFSYNC` when available. If the stronger barrier is unavailable, the platform capability report and plan explicitly classify the durability level, and live apply requires operator approval for that downgraded power-loss guarantee.
7. Run strict descriptor-based doctor plus the plan's typed verifier adapters (argv arrays or registered Python verifier IDs, never shell strings). Append `committed` only when all fresh results match the plan. `switched` recovery reruns the same verification.
8. Recovery is state-specific under the same lock: `prepared`/`staged` discard only validated private staging; `switching` and `rolling_back` restore every intended path in reverse order using descriptor-relative exclusive temporary writes/links, file and parent fsync, and exact metadata/digest/link-text verification; `switched` verifies and commits or enters rollback. Repeated terminal recovery is idempotent. Unknown state, malformed/tampered record, mismatched plan/root/generation, unsafe component, backup identity/digest failure, or unverifiable operation fails closed without mutation.
9. Journal hash chaining detects corruption and accidental/unauthorized modification under the declared ownership policy; it is not a cryptographic signature against a malicious process running as the same authorized owner. Strong same-owner adversary protection requires an external signing key and is outside this change.
10. Retain originals and backup for rollback; no deletion in this change.

Atomic rename is per path, not a tree-wide transaction. Safety therefore comes from quiescence, backup copies, the fixed journal oracle above, idempotent recovery, and a path-by-path compatibility policy. Tests terminate the migrator before/after each intent, replace, directory fsync, completion record, and state transition.

`tdt-core` ships the path/principal/writer/verifier schemas and compiler. Concrete rows are owned beside each consumer/deployment and become one compiled plan only after consumer work. The compiled plan records every executable legacy path without placeholders: repository/owner, old path, canonical helper/new path, reader/writer principals, read fallback, write target, compatibility mechanism, access policy, quiescence adapter, verifier, and removal milestone. Old and migrated consumers are tested against the same synthetic generation.

## Repository Rollout

1. `tdt-core`: add contract tests, helpers, CLI, doctor, source audit, security kernel, strict manifest/plan/attestation/journal schemas, and a synthetic-only plan compiler/executor; bump to `0.3.0`; build an offline-complete local wheelhouse containing the provider plus locked runtime/transitive dependencies, record hashes, and verify with fresh cache-disabled installation without sibling source paths. This artifact contains schemas and test vectors, not guessed consumer/deployment rows or a live plan. Publish to Nexus only after a non-secret reachability/auth/authority preflight succeeds.
2. Direct provider importers add `tdt-core>=0.3,<0.4`. `agent-docs-sync` becomes a direct dependency because its source will import path helpers; editable sources remain only in `[tool.uv.sources]` for development. Clean-install verification uses copied metadata with editable source mappings excluded and `uv pip install --no-index --find-links <wheelhouse>`.
3. `tdt-observability`: explicitly raise Python support from `>=3.12` to `>=3.14,<3.15`, add `tdt-core>=0.3,<0.4`, regenerate its lock, and document the breaking floor change. `tdt-sheets` already targets 3.14 and adds the same provider floor. Optional-import fallback is forbidden for the required path contract.
4. Source-migration owners are the eleven repositories named in the proposal. `ai-review` and `jira-epic-report` are verification/classification consumers. The closed-world conformance manifest enumerates `tdt-core` plus all fourteen non-provider repositories. A new participant or a verification consumer promoted to migration ownership requires a reviewed manifest-role update.
5. `ai-harness-skills` retains standalone `$TDT_HOME/ai-harness` isolation. If dependency review permits, it imports the provider; otherwise it implements a dependency-free `TdtRootContract` compatibility adapter generated/tested from the same contract vectors. Either route MUST conform for unset/empty, tilde, absolute-root rejection, dynamic reevaluation, filename validation, and containment semantics.
6. Release graph: `tdt-core` → `agent-core` → `agent-docs-sync`/`agent-harness`; independent consumers follow after provider verification. Rollback is the reverse downstream order while provider compatibility exports remain installed.
7. Deploy/restart migrated consumers and verify active versions plus `TDT_ENV_PROFILE=production` for production launchd/Compose processes before any live path switch.
8. Live `~/.tdt`: quiescence, dry-run, backup, journaled apply/recovery, strict doctor, Compose/launchd smoke, and consumer smoke verification only after all migrated consumers are active.

Every implementation repository uses its own feature worktree. No two writers own the same repository concurrently.

### Dependency and order graphs

All arrows below mean “left side must be available before right side” and are validated as separate directed acyclic graphs; they are not interchangeable:

| Graph | Required edges |
|---|---|
| Runtime/import | `tdt-core → agent-core`; `tdt-core → agent-docs-sync`; `tdt-core → agent-harness`; `agent-core → agent-docs-sync`; `agent-core → agent-harness`; independent direct consumers depend on `tdt-core`; `tdt-core` depends on no consumer |
| Build/package | provider wheel/wheelhouse → every consumer build; `agent-core` reviewed artifact → `agent-docs-sync` and `agent-harness` build verification |
| Release/deployment | `tdt-core` → `agent-core` → `agent-docs-sync`/`agent-harness`; other direct consumers follow the provider independently; complete manifests/plan follow consumer repository commits |
| Editable development only | `[tool.uv.sources]` may point from a consumer checkout to sibling provider/agent checkouts; these edges are excluded from release artifacts and clean-install gates |
| Rollback | migrated leaf consumers → `agent-docs-sync`/`agent-harness` → `agent-core`; provider compatibility artifact remains installed and is not removed in routine rollback |

The graph inventory records repository, dependency class, direction, version floor, and evidence source. A deterministic cycle checker runs before provider packaging and again after every consumer metadata change. Any cycle, undeclared reverse edge, consumer dependency from `tdt-core`, or mismatch between metadata and the graph blocks the dependent task.

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

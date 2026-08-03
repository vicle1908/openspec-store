## MODIFIED Requirements

### Requirement: `load_tdt_env()` honours `TDT_HOME` when set

The function `tdt_core.env.load_tdt_env()` SHALL resolve the environment file at `$TDT_HOME/.env` when `TDT_HOME` is set, and SHALL fall back to `Path.home() / ".tdt" / ".env"` when it is unset or empty. All public path helpers SHALL use the same dynamically evaluated root resolver; consumers SHALL NOT capture or independently parse `TDT_HOME` at import time.

#### Scenario: `TDT_HOME` set

- **GIVEN** `TDT_HOME=/home/agent/.tdt`
- **WHEN** `load_tdt_env()` is called for the first time in a process
- **THEN** it SHALL read `/home/agent/.tdt/.env` via python-dotenv
- **AND** the initial home-environment load SHALL NOT read any other `.env` location
- **AND** subsequent loader calls in the same process SHALL remain no-ops unless the explicit test isolation API is used

#### Scenario: `TDT_HOME` unset

- **GIVEN** `TDT_HOME` is not set
- **WHEN** `load_tdt_env()` is called
- **THEN** it SHALL read `Path.home() / ".tdt" / ".env"` via python-dotenv when the file exists
- **AND** the function SHALL NOT raise, whether or not the optional file exists

#### Scenario: `TDT_HOME` set to empty string

- **GIVEN** `TDT_HOME=""`
- **WHEN** `load_tdt_env()` is called
- **THEN** it SHALL treat the value as unset and read `Path.home() / ".tdt" / ".env"` via python-dotenv when the file exists
- **AND** the function SHALL NOT raise, whether or not the optional file exists
- **AND** it SHALL NOT create or resolve paths below the current working directory

#### Scenario: Environment changes after module import

- **GIVEN** a consumer module has already been imported
- **WHEN** `TDT_HOME` changes before a path helper is called
- **THEN** the helper SHALL use the current environment value
- **AND** no public import-time constant SHALL redirect the call to the old root

### Requirement: Tilde expansion is applied

The canonical root resolver SHALL apply user expansion to a non-empty `TDT_HOME` value before constructing any descendant path.

The expanded root SHALL be absolute. Relative roots SHALL be rejected before file I/O. Helper namespace components SHALL be validated identifiers, and filenames SHALL be validated single basenames rather than arbitrary path fragments. Dedicated helpers MAY own fixed hidden filenames such as `.env`.

#### Scenario: Tilde-prefixed `TDT_HOME`

- **GIVEN** `TDT_HOME=~/.tdt` and `$HOME=/Users/operator`
- **WHEN** `load_tdt_env()` is called
- **THEN** it SHALL read `/Users/operator/.tdt/.env` via python-dotenv when the file exists
- **AND** the function SHALL NOT raise, whether or not the optional file exists
- **AND** the selected environment-file path SHALL contain no literal `~` segment

#### Scenario: Relative `TDT_HOME`

- **GIVEN** `TDT_HOME` is a relative path
- **WHEN** the canonical resolver is called
- **THEN** it SHALL reject the root before reading or creating files

#### Scenario: Runtime filename with extension

- **GIVEN** a valid namespace and filename such as `config.yaml`, `state.sqlite`, or `worker.pid`
- **WHEN** a runtime path helper validates the request
- **THEN** it SHALL accept the single basename and preserve its extension
- **AND** it SHALL reject separators, NUL, empty names, `.`/`..`, and unowned leading-dot names

### Requirement: Local `.env` override behaviour is preserved

An unset environment profile SHALL default to development behavior and preserve the existing repo-local `.env` override. Explicit development profile SHALL behave identically. Explicit production profile SHALL disable repo-local `.env` loading. Unknown non-empty profile values SHALL fail closed.

`TDT_ENV_PROFILE` SHALL be read only from the inherited process environment before any `.env` file is opened. File-based values SHALL NOT select or change the profile.

#### Scenario: Environment profile is unset

- **GIVEN** `TDT_ENV_PROFILE` is unset or empty
- **AND** `$TDT_HOME/.env` exists
- **AND** the current repository contains `.env`
- **WHEN** `load_tdt_env()` is called
- **THEN** it SHALL use development behavior without requiring new caller configuration
- **AND** `$TDT_HOME/.env` SHALL be loaded without overriding values already in the process environment
- **AND** the repo-local file SHALL be loaded with python-dotenv `override=True`
- **AND** repo-local values SHALL therefore override process and `$TDT_HOME/.env` values exactly as before this change

#### Scenario: Local .env exists

- **GIVEN** `$TDT_HOME/.env` exists
- **AND** the current repository contains `.env`
- **AND** the environment profile is `development`
- **WHEN** `load_tdt_env()` is called
- **THEN** `$TDT_HOME/.env` SHALL be loaded without overriding values already in the process environment
- **AND** the repo-local file SHALL be loaded with python-dotenv `override=True`
- **AND** repo-local values SHALL therefore override process and `$TDT_HOME/.env` values for compatibility
- **AND** diagnostics SHALL identify overridden key names without values

#### Scenario: Local .env exists in production

- **GIVEN** the environment profile is `production`
- **AND** the current repository contains `.env`
- **WHEN** `load_tdt_env()` is called
- **THEN** the repo-local file SHALL NOT be read
- **AND** process environment values SHALL take precedence over `$TDT_HOME/.env`

#### Scenario: Unknown environment profile

- **GIVEN** an unsupported environment profile
- **WHEN** environment loading begins
- **THEN** loading SHALL fail before applying file values
- **AND** the error SHALL not include secret values

### Requirement: Idempotency is preserved

The default loader SHALL complete at most once per process under concurrent calls. It SHALL publish initialized state only after a complete successful load. A documented lock-scoped isolation API MAY scope loader/environment state for tests, but production consumers SHALL NOT mutate private module state.

#### Scenario: Repeated calls

- **GIVEN** `load_tdt_env()` completed once
- **WHEN** it is called again in the same process
- **THEN** the second call SHALL perform no file I/O
- **AND** it SHALL not raise

#### Scenario: Isolated test context

- **GIVEN** a test enters the documented environment-loader isolation context
- **WHEN** it selects a temporary `TDT_HOME`
- **THEN** loading SHALL be isolated to that context
- **AND** original environment and loader state SHALL be restored on exit

#### Scenario: Concurrent first load

- **GIVEN** multiple threads call `load_tdt_env()` before initialization completes
- **WHEN** the calls execute concurrently
- **THEN** exactly one complete file-loading sequence SHALL occur
- **AND** all callers SHALL observe the same terminal success or failure
- **AND** a failed load SHALL NOT leave partial initialized state

#### Scenario: Retry after failed load

- **GIVEN** the sole first loading sequence fails after a file parser temporarily mutates process environment
- **WHEN** all concurrent first callers observe that failure and a later caller retries after the cause is removed
- **THEN** the failed sequence SHALL have restored every environment key it changed
- **AND** all callers in the failed cohort SHALL have observed the same terminal failure
- **AND** the later call SHALL perform one new complete loading sequence and publish success only after completion

## ADDED Requirements

### Requirement: Canonical TDT_HOME layout and path containment

`tdt-core` SHALL provide dynamically evaluated helpers for config, credentials, schedules, logs, state, and app runtime paths. Generated paths MUST remain within the resolved `TDT_HOME`. Participating consumers SHALL use these helpers or pass an explicit injected path; a formally standalone repository MAY instead use a dependency-free compatibility adapter only when it passes the same committed contract vectors and preserves its declared isolation boundary.

Filesystem mutation and security inspection SHALL operate from one retained descriptor for the validated resolved root. Every descendant component SHALL be validated and opened relative to its retained parent without following symlinks. Security-sensitive regular files SHALL be single-linked. Creation, replacement, backup, restoration, and verification SHALL use descriptor-relative operations, file and parent-directory fsync, and post-open identity/type/link-count/digest checks. If required platform primitives are unavailable, mutation SHALL fail closed.

#### Scenario: Consumer requests a runtime path

- **WHEN** a consumer requests its log, state, config, or credential path without an explicit override
- **THEN** the path SHALL be derived by the canonical provider at call time
- **AND** the path SHALL be namespaced to the owning application where applicable

#### Scenario: Descendant escapes the root

- **GIVEN** a requested app or filename contains traversal or resolves outside `TDT_HOME`
- **WHEN** a path helper validates it
- **THEN** the helper SHALL reject the request before file I/O

#### Scenario: Descendant ancestor is replaced

- **GIVEN** the resolved root has been opened and recorded by device/inode
- **AND** a descendant directory is replaced with a symlink before an operation
- **WHEN** the provider opens, creates, renames, deletes, backs up, restores, or inspects the descendant
- **THEN** it SHALL reject the operation through no-follow descriptor-relative traversal
- **AND** it SHALL NOT access or mutate the symlink target

#### Scenario: Unsupported secure mutation primitive

- **GIVEN** the host lacks a required descriptor-relative or no-follow primitive
- **WHEN** a mutating or recovery operation is requested
- **THEN** the operation SHALL fail before mutation
- **AND** read-only path construction MAY remain available

#### Scenario: First-run root creation

- **GIVEN** the selected root does not exist
- **AND** the default home or an explicit approved existing parent anchor is safely openable and satisfies bootstrap policy
- **WHEN** the provider creates the root
- **THEN** it SHALL create each validated missing component relative to the retained parent descriptor
- **AND** fsync and reopen each component no-follow before descending
- **AND** verify type, identity, owner, and declared policy before retaining the final root descriptor
- **AND** a missing, replaced, symlinked, foreign, or unapproved bootstrap anchor SHALL fail without creation

#### Scenario: Target platform capabilities are available

- **GIVEN** the supported macOS and Python 3.14 runtime
- **WHEN** the platform capability gate runs
- **THEN** it SHALL prove the required `dir_fd` operations, no-follow/directory/close-on-exec flags, descriptor-relative create/rename/link/unlink behavior, directory fsync, and selected journal durability barrier
- **AND** provider packaging SHALL remain blocked unless the recorded positive matrix passes without undocumented constants or pathname fallbacks

#### Scenario: Standalone harness isolation

- **WHEN** `ai-harness-skills` resolves durable runtime state
- **THEN** it SHALL remain below `$TDT_HOME/ai-harness`
- **AND** it SHALL NOT read or write agent-core or agent-harness state directories
- **AND** if it does not depend on `tdt-core`, its compatibility adapter SHALL pass the same root/path contract vectors as the provider

### Requirement: Typed config ownership and precedence

Shared settings SHALL have one declared owning config surface. Effective values SHALL follow the selected environment profile, `$TDT_HOME/.env`, typed non-secret config, and documented defaults. Duplicate logical settings across config files SHALL be rejected or reported as an expiring compatibility finding.

#### Scenario: Duplicate scheduler setting

- **GIVEN** the same scheduler key exists in `config.toml` and `config.yaml`
- **WHEN** strict configuration validation runs
- **THEN** it SHALL report both source paths and the key name
- **AND** it SHALL not silently select one value

#### Scenario: Scheduler duplicate migration

- **GIVEN** a scheduler key exists in both legacy TOML and canonical YAML
- **WHEN** migration evaluates it
- **THEN** equal normalized non-secret values SHALL retain YAML and remove the TOML duplicate from the staged generation
- **AND** unequal values SHALL block apply for an explicit operator choice
- **AND** literal DSNs SHALL be rewritten only to a validated `${SCHEDULER_POSTGRES_DSN}` reference whose selected environment value is present and non-conflicting

#### Scenario: Missing typed value uses default

- **GIVEN** a non-secret optional key is absent from environment and owned config
- **WHEN** typed configuration is constructed
- **THEN** the documented default SHALL be used
- **AND** provenance SHALL identify the source as `default`

#### Scenario: Environment reference grammar

- **GIVEN** a secret-shaped config scalar
- **WHEN** typed config parses it
- **THEN** only a full scalar `${VAR_NAME}` with `VAR_NAME` matching `[A-Z][A-Z0-9_]*` SHALL be accepted
- **AND** concatenation, defaults, nested expansion, `$VAR`, and malformed references SHALL fail without disclosing values

#### Scenario: Non-string secret value

- **GIVEN** a secret-shaped key contains a number, boolean, list, mapping, or null rather than a full-scalar reference
- **WHEN** typed config parses it
- **THEN** validation SHALL fail before accepting the value
- **AND** no representation of the rejected value SHALL appear in outputs

#### Scenario: Scheduler consumes governed config

- **GIVEN** canonical scheduler YAML contains `${SCHEDULER_POSTGRES_DSN}`
- **WHEN** scheduler settings are constructed
- **THEN** the scheduler SHALL consume the governed typed parser and selected environment value
- **AND** a literal scheduler DSN of any scalar/container type SHALL fail closed
- **AND** missing optional scheduler values SHALL record `default` provenance

### Requirement: Secret values are excluded from general config and diagnostics

Secret values SHALL come from the process environment, `$TDT_HOME/.env`, or a future approved secret provider. YAML/TOML config MAY contain environment references but SHALL NOT contain literal secret values. Values SHALL NOT appear in outputs produced by the governed loader, config parser, doctor, source audit, or migration, including their diagnostics, logs, exceptions, JSON, and manifests.

#### Scenario: Literal DSN in general config

- **GIVEN** a secret-shaped setting such as a database DSN has a literal value in YAML or TOML
- **WHEN** strict validation runs
- **THEN** it SHALL fail with the source path, key name, and reason code
- **AND** it SHALL not print the value

#### Scenario: Missing referenced secret

- **GIVEN** config references an environment key that is absent
- **WHEN** typed configuration is constructed
- **THEN** construction SHALL fail with the missing key name
- **AND** no neighboring environment values SHALL be disclosed

#### Scenario: Canary secret audit

- **GIVEN** test fixtures contain unique canary secrets
- **WHEN** loader, config parser, doctor, source audit, and migration success/failure paths are exercised
- **THEN** the canaries SHALL be absent from every output sink produced by those components

### Requirement: Effective-access filesystem policy

The canonical root and security-sensitive subtrees SHALL grant access only to declared host, launchd, and container principals that require it. Numeric modes or ACLs SHALL be derived from verified effective access rather than applied blindly. Credential symlinks SHALL resolve safely to approved regular files whose targets satisfy their declared policy.

The provider SHALL prove only the current host principal directly. Other launchd/container principals SHALL be accepted only through typed, fresh access attestations produced by registered deployment adapters and bound to root identity, plan digest, principal ID, required operation set, and expiry. The provider SHALL NOT infer another principal's access from mode bits alone.

#### Scenario: Private tree creation

- **WHEN** the provider creates root, credentials, schedules, state, logs, or backup paths
- **THEN** single-principal directories/files SHOULD use `0700`/`0600`
- **AND** shared host/container paths SHALL use the narrowest verified group/ACL policy that preserves required traversal and read/write access
- **AND** unknown runtime principals SHALL block migration apply

#### Scenario: Valid shared access policy

- **GIVEN** a governed path declares a shared group or ACL writer policy
- **AND** the metadata adapter plus fresh principal attestations prove the exact owner/group/mode/ACL/xattr/flag policy and required operations
- **WHEN** doctor and migration preflight evaluate it
- **THEN** the path SHALL be accepted even when a narrowly declared group write bit or ACL is required
- **AND** foreign, overbroad, undeclared, or unprovable access SHALL fail without changing metadata

#### Scenario: Bind-mounted container access

- **GIVEN** `$TDT_HOME` is bind-mounted into a service running under a different container principal
- **WHEN** doctor or migration evaluates access
- **THEN** it SHALL prove required traversal and file operations for that principal before tightening access
- **AND** a failed proof SHALL leave modes unchanged and fail strict apply

#### Scenario: Broken credential symlink

- **GIVEN** a canonical credential path is a broken symlink
- **WHEN** strict doctor or credential discovery runs
- **THEN** it SHALL report a failure without guessing another credential
- **AND** authentication SHALL fail with remediation that does not reveal credential content

#### Scenario: Escaping credential symlink

- **GIVEN** a credential symlink resolves outside approved credential locations
- **WHEN** strict doctor runs
- **THEN** it SHALL fail before the credential is read

#### Scenario: Credential target policy drift

- **GIVEN** a credential target is non-regular, hard-linked, foreign-owned, broader than its declared policy, or unreadable by a declared principal
- **WHEN** strict doctor or migration preflight runs
- **THEN** it SHALL report the path class and reason without reading content
- **AND** migration apply SHALL fail without changing modes

#### Scenario: Stale or unmapped principal evidence

- **GIVEN** a required principal has no adapter, cannot be mapped, or has an expired/mismatched/failed access attestation
- **WHEN** migration apply begins
- **THEN** apply SHALL fail before journal preparation or filesystem mutation

### Requirement: Redacting configuration doctor

The ecosystem SHALL provide a deterministic, workspace-independent doctor command with human and JSON output that checks runtime root resolution, ownership, permissions, links, parse validity, config ambiguity, and secret placement. Repository conformance SHALL be checked only by a separate source-audit command with an explicit workspace root.

The base `tdt-core` distribution SHALL expose these commands through a `tdt` console entrypoint without requiring scheduler extras or a source checkout.

#### Scenario: Healthy alternate root

- **GIVEN** a valid temporary `TDT_HOME`
- **AND** no repository workspace is available
- **WHEN** strict doctor runs
- **THEN** it SHALL exit zero
- **AND** JSON output SHALL contain only paths, key names, source classes, modes, and reason codes

#### Scenario: Multiple findings

- **GIVEN** permission, broken-link, duplicate-key, and literal-secret findings coexist
- **WHEN** strict doctor runs
- **THEN** it SHALL report every finding in a stable machine-readable schema
- **AND** exit non-zero

### Requirement: Reversible live migration

Migration from the legacy layout SHALL support writer quiescence, dry-run, exclusive locking, a durable generation journal, value-free backup manifests, per-path atomic replacement with parent-directory fsync, restart recovery, verification, idempotent rerun, and rollback. It SHALL NOT claim tree-wide atomic rename and SHALL NOT delete legacy source files in this change.

Migration SHALL be driven by a canonical immutable plan compiled from versioned consumer/deployment manifests. The plan SHALL bind root device/inode, exact concrete operations, config/credential choices, principal/writer/verifier IDs, source-manifest hashes, and a digest of canonical bytes. Placeholders, wildcards, shell strings, arbitrary executable paths, mutable PID inventories, caller-asserted quiescence, and unresolved choices SHALL be rejected.

Apply and recovery SHALL acquire the canonical lock before selecting or reading a journal. Recovery SHALL accept only a generation UUID and SHALL resolve it below the anchored private migration directory. Journal header/records, plan, generation, root identity, relative path components, owner/mode/type/link count, backup metadata/digests, and hash chain SHALL be validated before mutation. This detects corruption and unauthorized modification under the declared ownership policy; it does not claim protection from a malicious process running as the same authorized owner without an external signing key.

#### Scenario: Dry run

- **WHEN** migration runs with `--dry-run`
- **THEN** it SHALL report planned path and mode operations with values redacted
- **AND** no file metadata, content, or link SHALL change

#### Scenario: Mid-migration failure

- **GIVEN** a failure occurs after temporary targets are written
- **WHEN** the migration aborts
- **THEN** active paths SHALL remain or be restored to their pre-run hashes, links, and modes
- **AND** the lock SHALL be released

#### Scenario: Process termination during switch

- **GIVEN** the migration process terminates after any individual path replacement
- **WHEN** `tdt config recover` starts
- **THEN** `prepared` or `staged` SHALL discard staging without active changes
- **AND** `switching` or `rolling_back` SHALL restore every intended path in reverse order from backup copies
- **AND** `switched` SHALL verify and commit only on success, otherwise restore
- **AND** repeated recovery SHALL be idempotent

#### Scenario: Journal or backup is tampered

- **GIVEN** a generation contains an unsafe path, unknown schema/state, mismatched root/plan/generation, broken hash chain, or backup whose type/link-count/digest differs from recorded metadata
- **WHEN** recovery starts with that generation UUID
- **THEN** recovery SHALL fail closed without mutating active paths
- **AND** it SHALL not accept an arbitrary journal pathname

#### Scenario: Backup metadata is complete before switching

- **GIVEN** a compiled plan contains file, symlink, and previously absent destinations
- **WHEN** backup and staging complete
- **THEN** every operation SHALL have validated metadata for relative path, preimage type, link text where applicable, device/inode, UID/GID, mode, size, digest, and prior absence
- **AND** ACL/xattr/flag presence SHALL be captured by a registered metadata adapter or block the plan when exact restoration is unavailable
- **AND** no active path SHALL switch until every required backup object and metadata record is durable and verified

#### Scenario: Active writer is not quiescent

- **GIVEN** a registered launchd, Compose, scheduler, observability, or report writer remains active and does not honor the shared lock
- **WHEN** migration apply begins
- **THEN** apply SHALL fail before switching any path

#### Scenario: Writer quiescence evidence is incomplete

- **GIVEN** any consumer/deployment manifest lacks a registered discovery/lock adapter
- **OR** any configured writer is omitted, active without the shared lock, identified only by caller assertion/PID existence, or has stale evidence
- **WHEN** dry-run or apply preflight runs
- **THEN** the plan or preflight SHALL fail before switching any path

#### Scenario: Successful migration and rerun

- **WHEN** migration succeeds and strict doctor passes
- **THEN** a second migration run SHALL make no further changes
- **AND** rollback evidence and legacy source files SHALL remain available

#### Scenario: Switched verification fails

- **GIVEN** all path replacements completed
- **AND** strict descriptor-based doctor or any plan verifier fails
- **WHEN** commit or switched-state recovery evaluates the generation
- **THEN** it SHALL enter durable reverse rollback rather than record `committed`
- **AND** restored objects SHALL match recorded type, link text, owner, mode, size, and digest

### Requirement: Cross-repository conformance is enforced

A committed manifest and AST-based verifier SHALL govern participating repositories. Direct home literals, private `TDT_HOME` parsing, and import-time root snapshots SHALL be rejected unless an exception has an owner, reason, and unexpired date.

The verifier SHALL require an explicit workspace root. Missing registered repositories SHALL fail strict source audit but SHALL NOT affect runtime doctor.

The manifest SHALL enumerate every registered participating repository and executable path family. Omission, identity mismatch, or an unreviewed role change for a registered participant SHALL fail audit; unrelated sibling repositories SHALL be ignored, and comments and diagnostic messages MAY be classified separately from executable defaults.

The provider wheel SHALL contain mandatory versioned registry/rule package data loaded through the package-resource API: schema versions, rule IDs, the closed-world fifteen participant IDs, registered concrete-manifest locations, and required fields. Each participant repository SHALL own the concrete identity, include/path-family, exclusion, role, path/no-path, exception, deployment, and principal data at its registered location. Source audit SHALL validate and merge both layers. Missing, malformed, unknown-version, duplicate, unsafe, incomplete, or identity-mismatched provider or repository data SHALL fail before scanning. Provider-first release MAY be built with synthetic concrete manifests, but real workspace source audit and migration-plan generation SHALL remain unhealthy until all registered repository manifests exist and validate. Unrelated sibling repositories SHALL be ignored. Exceptions SHALL be validated independently and suppress only exact registered repository-relative path/rule matches. Operational manifest, inventory, parser, or traversal failures SHALL always exit non-zero; strict mode SHALL additionally make policy findings non-zero.

Audit SHALL NOT follow repository symlinks or inspect `.env`, credential/key files, runtime databases/logs, dependency/vendor directories, virtual environments, caches, generated artifacts, or `$TDT_HOME`. Failures SHALL report no source excerpts or values.

#### Scenario: New hard-coded consumer path

- **GIVEN** a registered consumer adds direct `Path.home()/".tdt"` construction
- **WHEN** the conformance verifier runs
- **THEN** it SHALL exit non-zero with repository, file, line, and rule ID

#### Scenario: Expired exception

- **GIVEN** an exception expiry is in the past
- **WHEN** the verifier runs
- **THEN** the exception SHALL not suppress the finding
- **AND** verification SHALL fail

#### Scenario: Missing or malformed packaged manifest

- **GIVEN** the installed provider lacks the source-audit manifest or its schema/content is invalid
- **WHEN** source audit runs
- **THEN** the report SHALL be unhealthy and strict mode SHALL exit non-zero
- **AND** it SHALL not silently scan an empty repository set

#### Scenario: Python alias and unrelated dictionary access

- **GIVEN** one file uses `from pathlib import Path as P; P.home() / ".tdt"`
- **AND** another file calls an unrelated dictionary's `.get("TDT_HOME")`
- **WHEN** source audit runs
- **THEN** it SHALL report the aliased executable path with repository, file, line, and rule ID
- **AND** it SHALL not classify the unrelated dictionary call as environment access

#### Scenario: Shadowed alias and executable default

- **GIVEN** one lexical scope shadows an imported `Path` or `getenv` alias
- **AND** another config model uses an executable default such as `Field(default="~/.tdt/state")`
- **WHEN** source audit runs
- **THEN** it SHALL not report the shadowed unrelated call
- **AND** it SHALL report the executable default with repository, file, line, and rule ID
- **AND** an equivalent docstring/help/log message SHALL not be a policy finding

#### Scenario: Unrelated workspace repository

- **GIVEN** the workspace contains a Git repository with no capability index, provider dependency, consumer manifest marker, or executable governed-path pattern
- **WHEN** source audit runs
- **THEN** it SHALL not require that repository in the TDT manifest
- **AND** every registered participating repository that is missing SHALL still make the report unhealthy

#### Scenario: Registered deployment artifact is unresolved

- **GIVEN** a registered Compose or launchd artifact is missing, identity-mismatched, ambiguously active, has unresolved interpolation, or declares a writer/principal without a reconciled owner/access contract
- **WHEN** source/deployment inventory validation runs
- **THEN** validation SHALL fail before migration plan generation
- **AND** unrelated Compose/plist artifacts outside the closed inventory SHALL be ignored

#### Scenario: Installed runtime outside a workspace

- **GIVEN** `tdt-core` is installed without sibling repository checkouts
- **WHEN** runtime doctor runs
- **THEN** it SHALL complete without repository discovery
- **AND** source audit SHALL require an explicit workspace root before scanning

### Requirement: Provider-first compatible release

The first provider artifact containing this contract SHALL be versioned, built, and installable from an isolated local wheelhouse before consumers adopt it. Nexus publication MAY follow only after its independent preflight. Consumers SHALL declare a dependency floor that resolves to the verified artifact, and provider helpers SHALL remain compatibility exports during consumer rollback.

#### Scenario: Clean consumer install

- **GIVEN** no editable sibling checkout is importable
- **WHEN** a migrated consumer is installed from its declared dependencies
- **THEN** it SHALL resolve a `tdt-core` version containing the canonical helpers
- **AND** the hashed wheelhouse SHALL contain the complete locked runtime/transitive dependency closure
- **AND** installation SHALL require no index, ambient cache, checkout, or `PYTHONPATH`
- **AND** its import and configuration smoke tests SHALL pass

#### Scenario: Installed provider artifact is internally consistent

- **GIVEN** the reviewed provider artifact is installed from an empty-cache no-index wheelhouse without a checkout or `PYTHONPATH`
- **WHEN** provider release verification runs
- **THEN** distribution metadata and `tdt_core.__version__` SHALL both report `0.3.0`
- **AND** the wheel SHALL contain the mandatory provider registry/rule package data
- **AND** `tdt --help` SHALL work without scheduler extras
- **AND** installed-wheel doctor, missing/invalid concrete-manifest failure, synthetic concrete-manifest source audit, plan-schema, and synthetic recovery smokes SHALL pass
- **AND** any version, entrypoint, package-data, or smoke mismatch SHALL block consumer adoption

#### Scenario: Consumer-first rollback

- **GIVEN** migrated consumers and the provider release have been deployed
- **WHEN** the rollout is rolled back
- **THEN** consumer imports, dependency metadata, and lockfiles SHALL be restored before provider rollback
- **AND** the verified provider artifact and helpers SHALL remain available
- **AND** a clean installation of the rolled-back consumer SHALL pass

### Requirement: Participating consumers have compatible Python metadata

Consumers that require the canonical provider SHALL declare a Python range compatible with the provider. This change SHALL raise `tdt-observability` to Python `>=3.14,<3.15` rather than shipping a second resolver.

#### Scenario: Observability installation on unsupported Python

- **GIVEN** Python 3.12 or 3.13
- **WHEN** the migrated `tdt-observability` package is resolved
- **THEN** package metadata SHALL reject the installation with an interpreter-version error

#### Scenario: Observability installation on Python 3.14

- **GIVEN** Python 3.14 and access to the provider distribution channel
- **WHEN** the migrated `tdt-observability` package is installed cleanly
- **THEN** `tdt-core>=0.3,<0.4` SHALL resolve
- **AND** observability path smoke tests SHALL pass

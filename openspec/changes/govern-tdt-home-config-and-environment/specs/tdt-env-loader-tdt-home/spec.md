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

#### Scenario: Tilde-prefixed `TDT_HOME`

- **GIVEN** `TDT_HOME=~/.tdt` and `$HOME=/Users/operator`
- **WHEN** `load_tdt_env()` is called
- **THEN** it SHALL read `/Users/operator/.tdt/.env` via python-dotenv when the file exists
- **AND** the function SHALL NOT raise, whether or not the optional file exists
- **AND** the selected environment-file path SHALL contain no literal `~` segment

### Requirement: Local `.env` override behaviour is preserved

An unset environment profile SHALL default to development behavior and preserve the existing repo-local `.env` override. Explicit development profile SHALL behave identically. Explicit production profile SHALL disable repo-local `.env` loading. Unknown non-empty profile values SHALL fail closed.

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

The default loader SHALL run at most once per process. A documented isolation API MAY reset or scope loader state for tests, but production consumers SHALL NOT mutate private module state.

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

## ADDED Requirements

### Requirement: Canonical TDT_HOME layout and path containment

`tdt-core` SHALL provide dynamically evaluated helpers for config, credentials, schedules, logs, state, and app runtime paths. Generated paths MUST remain within the resolved `TDT_HOME`, and participating consumers SHALL use these helpers or pass an explicit injected path.

#### Scenario: Consumer requests a runtime path

- **WHEN** a consumer requests its log, state, config, or credential path without an explicit override
- **THEN** the path SHALL be derived by the canonical provider at call time
- **AND** the path SHALL be namespaced to the owning application where applicable

#### Scenario: Descendant escapes the root

- **GIVEN** a requested app or filename contains traversal or resolves outside `TDT_HOME`
- **WHEN** a path helper validates it
- **THEN** the helper SHALL reject the request before file I/O

#### Scenario: Standalone harness isolation

- **WHEN** `ai-harness-skills` resolves durable runtime state
- **THEN** it SHALL remain below `$TDT_HOME/ai-harness`
- **AND** it SHALL NOT read or write agent-core or agent-harness state directories

### Requirement: Typed config ownership and precedence

Shared settings SHALL have one declared owning config surface. Effective values SHALL follow the selected environment profile, `$TDT_HOME/.env`, typed non-secret config, and documented defaults. Duplicate logical settings across config files SHALL be rejected or reported as an expiring compatibility finding.

#### Scenario: Duplicate scheduler setting

- **GIVEN** the same scheduler key exists in `config.toml` and `config.yaml`
- **WHEN** strict configuration validation runs
- **THEN** it SHALL report both source paths and the key name
- **AND** it SHALL not silently select one value

#### Scenario: Missing typed value uses default

- **GIVEN** a non-secret optional key is absent from environment and owned config
- **WHEN** typed configuration is constructed
- **THEN** the documented default SHALL be used
- **AND** provenance SHALL identify the source as `default`

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

### Requirement: Private filesystem policy

The canonical root and security-sensitive subtrees SHALL default to owner-only access. Credential symlinks SHALL resolve to existing regular files within approved locations whose targets satisfy the same permission policy.

#### Scenario: Private tree creation

- **WHEN** the provider creates root, credentials, schedules, state, logs, or backup paths
- **THEN** directories SHALL be mode `0700`
- **AND** created files SHALL be mode `0600` subject to platform-equivalent ACL semantics

#### Scenario: Broken credential symlink

- **GIVEN** a canonical credential path is a broken symlink
- **WHEN** strict doctor or credential discovery runs
- **THEN** it SHALL report a failure without guessing another credential
- **AND** authentication SHALL fail with remediation that does not reveal credential content

#### Scenario: Escaping credential symlink

- **GIVEN** a credential symlink resolves outside approved credential locations
- **WHEN** strict doctor runs
- **THEN** it SHALL fail before the credential is read

### Requirement: Redacting configuration doctor

The ecosystem SHALL provide a deterministic, workspace-independent doctor command with human and JSON output that checks runtime root resolution, ownership, permissions, links, parse validity, config ambiguity, and secret placement. Repository conformance SHALL be checked only by a separate source-audit command with an explicit workspace root.

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

Migration from the legacy layout SHALL support dry-run, exclusive locking, value-free backup manifests, atomic destination replacement, verification, idempotent rerun, and rollback. It SHALL NOT delete legacy source files in this change.

#### Scenario: Dry run

- **WHEN** migration runs with `--dry-run`
- **THEN** it SHALL report planned path and mode operations with values redacted
- **AND** no file metadata, content, or link SHALL change

#### Scenario: Mid-migration failure

- **GIVEN** a failure occurs after temporary targets are written
- **WHEN** the migration aborts
- **THEN** active paths SHALL remain or be restored to their pre-run hashes, links, and modes
- **AND** the lock SHALL be released

#### Scenario: Successful migration and rerun

- **WHEN** migration succeeds and strict doctor passes
- **THEN** a second migration run SHALL make no further changes
- **AND** rollback evidence and legacy source files SHALL remain available

### Requirement: Cross-repository conformance is enforced

A committed manifest and AST-based verifier SHALL govern participating repositories. Direct home literals, private `TDT_HOME` parsing, and import-time root snapshots SHALL be rejected unless an exception has an owner, reason, and unexpired date.

The verifier SHALL require an explicit workspace root. Missing registered repositories SHALL fail strict source audit but SHALL NOT affect runtime doctor.

#### Scenario: New hard-coded consumer path

- **GIVEN** a registered consumer adds direct `Path.home()/".tdt"` construction
- **WHEN** the conformance verifier runs
- **THEN** it SHALL exit non-zero with repository, file, line, and rule ID

#### Scenario: Expired exception

- **GIVEN** an exception expiry is in the past
- **WHEN** the verifier runs
- **THEN** the exception SHALL not suppress the finding
- **AND** verification SHALL fail

#### Scenario: Installed runtime outside a workspace

- **GIVEN** `tdt-core` is installed without sibling repository checkouts
- **WHEN** runtime doctor runs
- **THEN** it SHALL complete without repository discovery
- **AND** source audit SHALL require an explicit workspace root before scanning

### Requirement: Provider-first compatible release

The first provider release containing this contract SHALL be versioned and distributable before consumers adopt it. Consumers SHALL declare a dependency floor that resolves to that release, and published provider helpers SHALL remain compatibility exports during consumer rollback.

#### Scenario: Clean consumer install

- **GIVEN** no editable sibling checkout is importable
- **WHEN** a migrated consumer is installed from its declared dependencies
- **THEN** it SHALL resolve a `tdt-core` version containing the canonical helpers
- **AND** its import and configuration smoke tests SHALL pass

#### Scenario: Consumer-first rollback

- **GIVEN** migrated consumers and the provider release have been deployed
- **WHEN** the rollout is rolled back
- **THEN** consumer imports, dependency metadata, and lockfiles SHALL be restored before provider rollback
- **AND** already-published provider helpers SHALL remain available
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
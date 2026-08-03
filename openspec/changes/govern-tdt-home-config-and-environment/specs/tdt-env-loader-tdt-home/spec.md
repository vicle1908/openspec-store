## MODIFIED Requirements

### Requirement: `load_tdt_env()` honours `TDT_HOME` when set

The function `tdt_core.env.load_tdt_env()` SHALL resolve the environment file at `$TDT_HOME/.env` when `TDT_HOME` is set, and SHALL fall back to `Path.home() / ".tdt" / ".env"` when it is unset or empty. All public path helpers SHALL use the same dynamically evaluated root resolver; consumers SHALL NOT capture or independently parse `TDT_HOME` at import time.

#### Scenario: `TDT_HOME` set

- **GIVEN** `TDT_HOME=/home/agent/.tdt`
- **WHEN** the loader or a public path helper is called
- **THEN** it SHALL resolve below `/home/agent/.tdt`
- **AND** the loader SHALL NOT read another home environment file
- **AND** subsequent loader calls in the same process SHALL remain no-ops unless the explicit test isolation API is used

#### Scenario: `TDT_HOME` unset

- **GIVEN** `TDT_HOME` is not set
- **WHEN** the loader or a public path helper is called
- **THEN** it SHALL resolve below `Path.home() / ".tdt"`
- **AND** it SHALL NOT raise solely because the optional environment file is absent

#### Scenario: `TDT_HOME` set to empty string

- **GIVEN** `TDT_HOME=""`
- **WHEN** the loader or a public path helper is called
- **THEN** it SHALL treat the value as unset and use `Path.home() / ".tdt"`
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
- **WHEN** a loader or path helper is called
- **THEN** it SHALL resolve below `/Users/operator/.tdt`
- **AND** the returned path SHALL contain no literal `~` segment

### Requirement: Local `.env` override behaviour is preserved

Development profile SHALL preserve the existing repo-local `.env` override. Production profile SHALL disable repo-local `.env` loading. Profile selection SHALL be explicit, and unknown values SHALL fail closed.

#### Scenario: Local .env exists

- **GIVEN** `$TDT_HOME/.env` exists
- **AND** the current repository contains `.env`
- **AND** the environment profile is `development`
- **WHEN** `load_tdt_env()` is called
- **THEN** both files SHALL be loaded
- **AND** repo-local values SHALL override process and `$TDT_HOME/.env` values for compatibility
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

Secret values SHALL come from the process environment, `$TDT_HOME/.env`, or a future approved secret provider. YAML/TOML config MAY contain environment references but SHALL NOT contain literal secret values. Values SHALL NOT appear in diagnostics, logs, prompts, artifacts, exceptions, or migration manifests.

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
- **WHEN** doctor, migration, and config failures are exercised
- **THEN** the canaries SHALL be absent from stdout, stderr, JSON, logs, exceptions, and manifests

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

The ecosystem SHALL provide a deterministic doctor command with human and JSON output that checks root resolution, ownership, permissions, links, parse validity, config ambiguity, secret placement, and registered consumer conformance.

#### Scenario: Healthy alternate root

- **GIVEN** a valid temporary `TDT_HOME`
- **WHEN** strict doctor runs
- **THEN** it SHALL exit zero
- **AND** JSON output SHALL contain only paths, key names, source classes, modes, and reason codes

#### Scenario: Multiple findings

- **GIVEN** permission, broken-link, duplicate-key, and consumer-bypass findings coexist
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

#### Scenario: New hard-coded consumer path

- **GIVEN** a registered consumer adds direct `Path.home()/".tdt"` construction
- **WHEN** the conformance verifier runs
- **THEN** it SHALL exit non-zero with repository, file, line, and rule ID

#### Scenario: Expired exception

- **GIVEN** an exception expiry is in the past
- **WHEN** the verifier runs
- **THEN** the exception SHALL not suppress the finding
- **AND** verification SHALL fail
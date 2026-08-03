# tdt-env-loader-tdt-home Specification

## Purpose

Define the canonical `TDT_HOME` configuration and environment loading contract for the TDT ecosystem. This capability provides:

1. **Single root resolver** — `tdt_root()` dynamically evaluates `TDT_HOME` at call time; no import-time snapshots.
2. **Typed path helpers** — `tdt_config_path()`, `tdt_credentials_path()`, `tdt_schedules_dir()`, `tdt_logs_dir()`, `tdt_state_path()`, `tdt_runtime_path()` — all backed by `tdt_root()` with component validation.
3. **Governed environment loading** — `load_tdt_env()` with thread-safe one-time initialization, `TDT_ENV_PROFILE` precedence (development/production), and test isolation.
4. **Secret separation** — YAML/TOML config MAY contain environment references (`${VAR_NAME}`) but SHALL NOT contain literal secret values.
5. **Descriptor-relative security kernel** — filesystem operations use `dir_fd` + `O_NOFOLLOW` semantics; no pathname-based fallback.
6. **Journaled migration** — plan/apply/recover/rollback with hash-chained journal, typed attestations, and idempotent recovery.
7. **Runtime diagnostics** — `tdt config doctor` checks layout, permissions, links, config ambiguity, and secret placement.
8. **Cross-repo conformance** — AST-based source audit rejects hard-coded `~/.tdt` construction outside approved sites.

This capability is owned by `tdt-core` and enforced across 15 participating repositories.

## Requirements

### Requirement: `load_tdt_env()` honours `TDT_HOME` when set

The environment loader SHALL evaluate the effective `TDT_HOME` value at load time and use that root for the home environment file.

#### Scenario: Explicit root is selected

- **GIVEN** `TDT_HOME` names an absolute directory
- **WHEN** the loader initializes
- **THEN** it reads only the environment file under that directory before applying any separately governed development override

#### Scenario: Root is unset

- **GIVEN** `TDT_HOME` is absent
- **WHEN** the loader initializes
- **THEN** it uses the default home root and does not raise solely because the optional file is absent

#### Scenario: Root is empty

- **GIVEN** `TDT_HOME` is present but empty
- **WHEN** the loader initializes
- **THEN** it treats the value as unset and uses the default home root

#### Scenario: Root changes after import

- **GIVEN** the module was imported before `TDT_HOME` was changed
- **WHEN** the loader or a path helper is called
- **THEN** the effective value reflects the call-time environment rather than an import-time snapshot

### Requirement: Tilde expansion is applied

The environment loader SHALL expand a supported user-home prefix before validating and using `TDT_HOME`.

#### Scenario: Tilde-prefixed root

- **GIVEN** `TDT_HOME=~/.tdt` and a known home directory
- **WHEN** the loader initializes
- **THEN** it reads the expanded home-relative root

### Requirement: Local `.env` override behaviour is preserved

The environment loader SHALL keep the existing development-local override while preventing a repository-local file from changing an explicitly selected production profile.

#### Scenario: Development default keeps local override

- **GIVEN** the profile is unset or `development`
- **AND** both the home environment file and the current repository `.env` exist
- **WHEN** the loader initializes
- **THEN** the repository values override colliding home-file values

#### Scenario: Production excludes local override

- **GIVEN** the process selected the `production` profile before loading files
- **AND** both the home environment file and the current repository `.env` exist
- **WHEN** the loader initializes
- **THEN** the repository file is not loaded
- **AND** process values take precedence over home-file values

#### Scenario: Unknown profile fails closed

- **GIVEN** the process selected a non-empty unsupported profile
- **WHEN** the loader initializes
- **THEN** it returns a redacted profile error without loading either dotenv file

### Requirement: Idempotency is preserved

The environment loader SHALL publish only a complete initialization result and leave no initialized state after a failed attempt.

#### Scenario: Repeated calls

- **GIVEN** initialization completed successfully
- **WHEN** the loader is called again
- **THEN** it performs no second load and returns without error

#### Scenario: Concurrent first load

- **GIVEN** multiple threads call the loader before initialization completes
- **WHEN** the calls overlap
- **THEN** one complete load is published and all callers observe the same terminal result

#### Scenario: Failed load can retry

- **GIVEN** a transient load failure occurs
- **WHEN** the loader is called again after the failure is corrected
- **THEN** the retry performs a complete load rather than treating partial state as initialized

#### Scenario: Test isolation restores only loader changes

- **GIVEN** a supported test isolation context changes selected environment keys
- **WHEN** the context exits
- **THEN** only keys changed by that context are restored

### Requirement: Canonical runtime paths remain contained

The provider SHALL return absolute paths whose validated descendants remain under the effective `TDT_HOME` root.

#### Scenario: Valid provider path

- **GIVEN** an application name, runtime kind, and filename that satisfy the provider namespace rules
- **WHEN** a caller requests a config, credential, schedule, log, state, or runtime path
- **THEN** the returned path is rooted under the effective `TDT_HOME`

#### Scenario: Unsafe component is rejected

- **GIVEN** a component is empty, absolute, contains a separator, or is `.` or `..`
- **WHEN** a caller requests a provider path
- **THEN** the request fails before a path outside the root can be returned

#### Scenario: Relative root is rejected

- **GIVEN** `TDT_HOME` is a non-empty relative path without a supported user-home prefix
- **WHEN** a root-dependent operation starts
- **THEN** it rejects the value before reading or creating descendants

#### Scenario: Descendant substitution is detected

- **GIVEN** an ancestor or descendant is replaced by a symlink or incompatible object during a provider-owned operation
- **WHEN** the provider opens or creates the path
- **THEN** the operation fails closed and does not mutate the substituted location

### Requirement: Provider-owned private mutations fail closed

Provider-owned creation and replacement SHALL either complete with verified private objects or leave no partial mutation when the platform cannot provide the required safety guarantees.

#### Scenario: Secure directory creation

- **GIVEN** the effective root and approved bootstrap anchor satisfy the provider policy
- **WHEN** a missing provider-owned directory is created
- **THEN** the directory is private, verified, and usable by the current principal

#### Scenario: Required primitive is unavailable

- **GIVEN** a required no-follow, descriptor-relative, synchronization, or identity check is unavailable
- **WHEN** a mutating provider operation starts
- **THEN** it fails before mutation rather than falling back to an unsafe pathname operation

#### Scenario: Link-count or object-type policy fails

- **GIVEN** a protected regular file is a symlink, hard-linked, or the wrong object type
- **WHEN** the provider opens or replaces it
- **THEN** it rejects the object and does not treat it as a trusted secret or journal file

### Requirement: Typed configuration uses secret references

The provider SHALL accept secret-shaped configuration only when it uses the supported full-scalar environment-reference grammar after environment loading; literal secret values are rejected.

#### Scenario: Full-scalar reference resolves

- **GIVEN** a secret-shaped setting contains exactly `${UPPER_SNAKE_CASE_NAME}`
- **AND** the named environment value is available
- **WHEN** typed configuration is loaded
- **THEN** the setting resolves without emitting the secret value in diagnostics

#### Scenario: Literal or composite secret is rejected

- **GIVEN** a secret-shaped setting contains a literal, a collection, or a composite string containing a reference
- **WHEN** typed configuration is loaded
- **THEN** validation fails with the logical key and source but not the value

#### Scenario: Conflicting scheduler sources are visible

- **GIVEN** the same logical scheduler setting appears in competing supported sources
- **WHEN** governed configuration is loaded
- **THEN** equal normalized values are reported as a deterministic compatibility condition and conflicting values fail closed

#### Scenario: Missing reference is redacted

- **GIVEN** a referenced environment name is unavailable
- **WHEN** governed configuration is loaded
- **THEN** the error identifies the missing logical setting and reference name without revealing any credential value

### Requirement: Configuration diagnostics are redacted and reproducible

The provider SHALL expose a `tdt config doctor` result that reports layout, configuration, link, permission, and access findings without requiring a repository checkout or revealing secret values.

#### Scenario: Healthy alternate root

- **GIVEN** an isolated alternate root satisfies the provider policy
- **WHEN** doctor runs in text or JSON mode
- **THEN** it reports a healthy result with stable relative paths and source names

#### Scenario: Multiple findings

- **GIVEN** an alternate root has malformed configuration, a broken link, and permission drift
- **WHEN** doctor runs in strict mode
- **THEN** it reports each finding, returns a non-zero result, and omits secret contents from output and exceptions

#### Scenario: Installed runtime is independent

- **GIVEN** the provider is installed without sibling repositories
- **WHEN** doctor runs against an explicit root
- **THEN** it performs the runtime audit without importing workspace source files

### Requirement: Packaged provider contracts are mandatory

The provider SHALL validate its packaged registry and schema resources before reporting provider contract readiness.

#### Scenario: Packaged resources are valid

- **GIVEN** registry and rule resources have the expected identity, version, and participant invariants
- **WHEN** the installed provider loads its contract data
- **THEN** contract readiness succeeds

#### Scenario: Resource is missing or malformed

- **GIVEN** a required packaged resource is absent, malformed, duplicated, or has the wrong identity marker
- **WHEN** the installed provider loads its contract data
- **THEN** readiness fails closed with a redacted diagnostic

### Requirement: Provider artifact is internally consistent

The provider SHALL expose a base `tdt` command whose installed distribution metadata, runtime version, package resources, and documented provider behavior agree in a clean environment.

#### Scenario: Clean base installation

- **GIVEN** a fresh wheelhouse contains the provider and its locked runtime closure
- **WHEN** the provider is installed without a checkout or `PYTHONPATH`
- **THEN** `tdt --help` and provider-only diagnostics run successfully without scheduler extras

#### Scenario: Version disagreement

- **GIVEN** distribution metadata and the imported runtime report different versions
- **WHEN** the installed provider is checked
- **THEN** the release gate fails before the artifact is eligible for consumers

#### Scenario: Provider rollback remains available

- **GIVEN** the provider is rejected by a clean-install or contract check
- **WHEN** the pre-change artifact is restored
- **THEN** existing consumer behavior remains available because this change has not modified consumer repositories or the live root

# tdt-env-loader-tdt-home Specification

## Purpose

Define the canonical `TDT_HOME` configuration and environment loading contract for the TDT ecosystem. This capability provides:

1. **Single root resolver** — `tdt_root()` dynamically evaluates `TDT_HOME` at call time; no import-time snapshots.
2. **Typed path helpers** — `tdt_config_path()`, `tdt_credentials_path()`, `tdt_schedules_dir()`, `tdt_logs_dir()`, `tdt_state_path()`, `tdt_runtime_path()` — all backed by `tdt_root()` with component validation.
3. **Governed environment loading** — `load_tdt_env()` with thread-safe one-time initialization, `TDT_ENV_PROFILE` precedence (development/production), and test isolation.
4. **Authoritative config injection** — `config.toml` values are written directly to `os.environ`; no backward-compatibility bridge.
5. **Secret separation** — YAML/TOML config MAY contain environment references (`${VAR_NAME}`) but SHALL NOT contain literal secret values.
6. **Descriptor-relative security kernel** — filesystem operations use `dir_fd` + `O_NOFOLLOW` semantics; no pathname-based fallback.
7. **Runtime diagnostics** — `tdt config doctor` checks layout, permissions, links, config ambiguity, and secret placement.
8. **Cross-repo conformance** — AST-based source audit rejects hard-coded `~/.tdt` construction outside approved sites.

This capability is owned by `tdt-core` and enforced across 15 participating repositories.
## Requirements
### Requirement: `load_tdt_env()` honours `TDT_HOME` when set

The canonical environment loader SHALL evaluate `TDT_HOME` at call time, load the selected home environment according to the active environment profile, and expose the supported loader through the public tdt-core package API. Typed configuration and agent-profile resolution SHALL use the same root and loader state. An explicitly supported environment-file override SHALL be honored by the caller that selected it rather than silently replaced with the default home file.

#### Scenario: Explicit root is selected

- **GIVEN** `TDT_HOME` names an absolute directory
- **WHEN** the loader initializes
- **THEN** it SHALL read only that root's home environment before any separately governed development override

#### Scenario: Root is unset

- **GIVEN** `TDT_HOME` is absent
- **WHEN** the loader initializes
- **THEN** it SHALL use the canonical default home root
- **AND** it SHALL not require the variable to be exported for default paths to resolve

#### Scenario: Root is empty

- **GIVEN** `TDT_HOME` is present but empty
- **WHEN** the loader initializes
- **THEN** it SHALL treat the value as unset

#### Scenario: Root changes after import

- **GIVEN** tdt-core was imported before `TDT_HOME` changed
- **WHEN** the loader or a path helper is called
- **THEN** the effective root SHALL reflect the call-time environment

#### Scenario: TDTSettings loads from same root

- **GIVEN** `TDT_HOME` names an absolute directory
- **WHEN** typed settings or an agent profile is resolved
- **THEN** it SHALL read configuration and environment inputs from that same root

#### Scenario: Public loader import

- **WHEN** a consumer imports the documented environment loader from the public tdt-core package
- **THEN** the import SHALL succeed without reaching into a private module

#### Scenario: Explicit environment file

- **GIVEN** a supported caller supplies an explicit environment-file path for isolation
- **WHEN** settings are loaded
- **THEN** that file SHALL be the selected dotenv input
- **AND** the default TDT home environment file SHALL not replace it silently

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

The environment loader SHALL publish only a complete initialization result for one effective root, profile, and selected environment-file identity. Repeated equivalent calls SHALL be idempotent. A changed root, profile, or explicit file SHALL not reuse incompatible initialized state. Failed attempts SHALL remain retryable, and test isolation SHALL restore only loader-owned changes.

#### Scenario: Repeated calls

- **GIVEN** initialization completed for one effective identity
- **WHEN** the same call is repeated
- **THEN** it SHALL perform no second load

#### Scenario: Concurrent first load

- **GIVEN** multiple threads initialize the same effective identity
- **WHEN** the calls overlap
- **THEN** one complete result SHALL be published and all callers SHALL observe it

#### Scenario: Failed load can retry

- **GIVEN** initialization fails before completion
- **WHEN** the problem is corrected and loading is retried
- **THEN** a complete load SHALL be attempted rather than treating partial state as initialized

#### Scenario: Root or profile changes

- **GIVEN** one effective identity was initialized
- **WHEN** the root, environment profile, or explicit file changes
- **THEN** the loader SHALL either initialize the new identity or require an explicit reset with a clear diagnostic
- **AND** it SHALL not silently reuse the old identity

#### Scenario: Test isolation restores only loader changes

- **GIVEN** a supported isolation context changes selected environment keys
- **WHEN** the context exits
- **THEN** only values changed by that context SHALL be restored

### Requirement: Canonical runtime paths remain contained

The provider SHALL return absolute paths whose validated descendants remain under the effective TDT root. Provider-owned configuration reads and writes MUST reject unsafe components, unresolved variables, disallowed symlinks, hard-link ambiguity where applicable, and descendant substitution.

#### Scenario: Valid provider path

- **GIVEN** all namespace components satisfy provider rules
- **WHEN** a caller requests a config, credential, schedule, log, state, runtime, agent-overlay, or artifact path
- **THEN** the returned path SHALL be rooted under the effective TDT root

#### Scenario: Unsafe component is rejected

- **GIVEN** a component is empty, absolute, contains a separator or NUL, or equals `.` or `..`
- **WHEN** a provider path is requested
- **THEN** the request SHALL fail before an escaped path is returned

#### Scenario: Hidden fixed filename remains safe

- **GIVEN** a supported fixed hidden filename such as `.env`
- **WHEN** its provider path is requested
- **THEN** it SHALL be accepted only as an explicitly registered filename
- **AND** arbitrary dot-prefixed traversal components SHALL remain rejected

#### Scenario: Relative root is rejected

- **GIVEN** `TDT_HOME` is a non-empty unsupported relative path
- **WHEN** a root-dependent operation starts
- **THEN** it SHALL fail before reading or creating descendants

#### Scenario: Descendant substitution is detected

- **GIVEN** an ancestor or descendant is replaced by a symlink or incompatible object
- **WHEN** a provider-owned read or mutation starts
- **THEN** it SHALL fail closed and SHALL not trust or mutate the substituted location

#### Scenario: Explicit external file is separately governed

- **GIVEN** a caller explicitly selects a config file outside the standard TDT root
- **WHEN** the API permits external explicit files
- **THEN** the source SHALL be labeled explicit and validated under the API's separate containment policy
- **AND** it SHALL not be mistaken for a standard contained agent file

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

The provider SHALL accept secret-shaped configuration only when it uses the supported full-scalar environment-reference grammar after environment loading; literal secret values are rejected. Retired credential-field names (such as `api_key_env`) SHALL receive no backward-compatibility exemption in the configuration loader's secret policy; they SHALL be classified as secret-shaped so that literal values are rejected and only full-scalar `${ENV}` references pass the loader, exactly as for any other secret-shaped key. The canonical credential field is `auth_env`, and the canonical schema parser SHALL reject the retired field name itself regardless of value form.

#### Scenario: Full-scalar reference resolves

- **GIVEN** a secret-shaped setting contains exactly `${UPPER_SNAKE_CASE_NAME}`
- **AND** the named environment value is available
- **WHEN** typed configuration is loaded
- **THEN** the setting resolves without emitting the secret value in diagnostics

#### Scenario: Literal or composite secret is rejected

- **GIVEN** a secret-shaped setting contains a literal, a collection, or a composite string containing a reference
- **WHEN** typed configuration is loaded
- **THEN** validation fails with the logical key and source but not the value

#### Scenario: Retired api_key_env field with a literal value is rejected by the loader

- **GIVEN** a configuration mapping contains `providers.<id>.api_key_env` with a bare environment-variable name or any other literal value
- **WHEN** the configuration loader applies its secret policy
- **THEN** the loader SHALL reject the mapping with a secret-shaped-key error identifying the `api_key_env` path
- **AND** the loader SHALL NOT carry a backward-compatibility exemption for the retired field

#### Scenario: Retired api_key_env field is rejected by the canonical schema regardless of value form

- **GIVEN** a configuration mapping contains `providers.<id>.api_key_env` with any value, including a full-scalar `${ENV}` reference that passes the loader's secret policy
- **WHEN** the canonical schema parser validates the provider definition
- **THEN** the parser SHALL reject the mapping because `api_key_env` is not a declared provider field
- **AND** the retired field SHALL NOT reach profile resolution in any value form

#### Scenario: Canonical auth_env field passes the loader

- **GIVEN** a configuration mapping contains `providers.<id>.auth_env` with a bare environment-variable name
- **WHEN** the configuration loader applies its secret policy
- **THEN** the loader SHALL accept the mapping without a secret-shaped-key error

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

### Requirement: Config.toml injection is deprecated

The environment loader SHALL emit a deprecation warning when injecting `config.toml` values into `os.environ`. `load_sprint_config()` SHALL remain available as a backward-compat shim.

#### Scenario: Deprecated function warns

- **WHEN** `load_sprint_config()` is called
- **THEN** it SHALL emit a `DeprecationWarning`
- **AND** it SHALL inject values into `os.environ` for backward compatibility

### Requirement: Canonical environment authority

Participating Python consumers MUST delegate TDT dotenv loading and LLM environment-key interpretation to tdt-core. They SHALL NOT call a dotenv parser directly, scan the home environment file themselves, or implement a second model-secret lookup path.

#### Scenario: Consumer source audit

- **WHEN** participating consumer source is audited
- **THEN** direct dotenv reads and direct TDT home environment-file parses for LLM configuration SHALL be absent

#### Scenario: Provider credential is resolved once

- **WHEN** a selected provider requires a credential environment key
- **THEN** the canonical environment authority SHALL determine its availability
- **AND** model construction and diagnostics SHALL consume the resulting redacted status rather than rereading the file

### Requirement: Explicit dotenv profile and file ownership

`tdt_core.env.load_tdt_env` SHALL be the only public dotenv authority for participating
Python consumers. Development and production SHALL have distinct, tested repository
`.env` behavior, and an explicitly selected environment file SHALL be honored through
the same loader. This change chooses to make the existing `load_settings(env_file=...)`
parameter functional by passing its selected file identity to `load_tdt_env`; silently
ignoring that parameter is not permitted.

#### Scenario: Development repository dotenv is governed

- **GIVEN** the active profile is development and both the selected TDT-home file and repository `.env` exist
- **WHEN** `load_tdt_env` initializes
- **THEN** the documented development override order SHALL apply
- **AND** the consumer SHALL not parse either file directly

#### Scenario: Production repository dotenv is excluded

- **GIVEN** the active profile is production and both the selected TDT-home file and repository `.env` exist
- **WHEN** `load_tdt_env` initializes
- **THEN** the repository `.env` SHALL not be loaded
- **AND** no participating consumer SHALL bypass that decision with a local parser

#### Scenario: Explicit env_file is honored

- **GIVEN** `load_settings(env_file=explicit_path)` is called for an isolated run
- **WHEN** the loader initializes
- **THEN** `explicit_path` SHALL be the selected dotenv input and part of the loader identity
- **AND** the default TDT-home file SHALL not silently replace it

#### Scenario: Direct dotenv ownership audit

- **WHEN** participating consumer and model-layer source is audited
- **THEN** only the public `tdt_core.env.load_tdt_env` boundary SHALL load dotenv files for LLM configuration
- **AND** direct `dotenv_values`, `load_dotenv`, and home-file parsing in those consumers SHALL be absent

### Requirement: Environment-key registry

The system SHALL publish a machine-readable registry for LLM and consumer environment keys. Each entry SHALL define the logical field, owner, type, precedence class, secret classification, supported consumers, and compatibility status. Duplicate logical ownership or incompatible aliases SHALL fail validation.

#### Scenario: Registered key drives resolution

- **WHEN** a registered environment key is present
- **THEN** the resolver SHALL coerce and apply it according to its declared type and precedence

#### Scenario: Alias deprecation is visible

- **WHEN** a supported legacy alias is used
- **THEN** diagnostics SHALL identify its deprecated status and canonical replacement
- **AND** both aliases SHALL not produce ambiguous effective values

#### Scenario: Conflicting aliases

- **WHEN** canonical and legacy keys for one field are both set to different values
- **THEN** resolution SHALL fail with the key names and logical field
- **AND** it SHALL not reveal protected values

#### Scenario: Provider credential registered and bound

- **GIVEN** the registry contains a credential entry with `secret: true` and `provider: "giaoduc"`
- **AND** a canonical provider declares `auth_env: HERMES_CUSTOM_GIAODUC_API_KEY`
- **WHEN** `resolve_agent_profile()` resolves that provider
- **THEN** the resolved route SHALL record `CredentialAvailability(key_name="HERMES_CUSTOM_GIAODUC_API_KEY", available=<bool>, provider="giaoduc")`
- **AND** credential availability SHALL be recorded without the secret value

#### Scenario: Unregistered credential key is rejected

- **WHEN** the registry's `credential_entry()` validation is asked for a key not present in the registry
- **THEN** it SHALL raise `ProfileResolutionError` identifying that the key is not registered
- **AND** the error SHALL NOT reveal credential values

#### Scenario: Credential availability reflects the environment, not registry membership

- **GIVEN** a canonical provider declares an `auth_env` value
- **WHEN** `resolve_agent_profile()` resolves that provider
- **THEN** the resolved route SHALL record `available` as true only when the named environment variable is present
- **AND** the registry SHALL serve as credential metadata (secret classification and provider binding), not as a resolution-time gate on `auth_env`
- **AND** no credential value SHALL be recorded or revealed

#### Scenario: Credential key assigned to wrong provider is rejected

- **GIVEN** the registry binds `ANTHROPIC_API_KEY` to provider `anthropic`
- **WHEN** a canonical provider for `openai-chat` declares `auth_env: ANTHROPIC_API_KEY`
- **THEN** the resolver SHALL reject the cross-provider assignment
- **AND** it SHALL not silently accept the mismatched credential binding


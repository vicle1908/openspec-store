## MODIFIED Requirements

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

## ADDED Requirements

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
- **WHEN** a provider entry references `api_key_env: HERMES_CUSTOM_GIAODUC_API_KEY`
- **THEN** the resolver SHALL accept the entry and bind it to the `giaoduc` provider
- **AND** credential availability SHALL be recorded without the secret value

#### Scenario: Unregistered credential key is rejected

- **WHEN** a provider entry references an `api_key_env` value not present in the registry
- **THEN** `credential_entry()` SHALL raise `ProfileResolutionError`
- **AND** the error SHALL name the missing key without revealing other credential values

#### Scenario: Credential key assigned to wrong provider is rejected

- **GIVEN** the registry binds `ANTHROPIC_API_KEY` to provider `anthropic`
- **WHEN** a provider entry for `openai-chat` references `api_key_env: ANTHROPIC_API_KEY`
- **THEN** the resolver SHALL reject the cross-provider assignment
- **AND** it SHALL not silently accept the mismatched credential binding

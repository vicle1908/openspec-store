## MODIFIED Requirements

### Requirement: Canonical configuration and CLI truthfulness

`agent-docs-sync` SHALL load one documented domain configuration schema and one canonical resolved agent profile per public operation. LLM model, fallback, provider, and behavior precedence SHALL be explicit run override > registered docs-sync environment > registered shared model environment > agent-specific TDT YAML > global TDT YAML > defaults. Repository configuration MAY define supported docs-sync domain behavior and runtime controls but MUST NOT define LLM fields. Configuration, discovery, validation, generation, diagnostics, normalized results, and reports SHALL consume the same profile, provenance, source fingerprints, effective timeout and iteration controls, and non-secret configuration identity without independently reopening configuration sources. Every public diagnostic, normalized workflow result, JSON output, and report SHALL expose provenance and fingerprint data through one stable serializable mapping that excludes protected values, private fields, and implementation object representations. Retries within one public operation SHALL reuse its captured profile and effective controls. A resumed operation SHALL proceed only after restoring and validating its retained non-secret configuration identity and effective controls; if that identity cannot be safely restored, resumption SHALL fail before model, persistence, or write-capable tool construction. The system SHALL validate unknown, legacy, malformed, secret-invalid, provider-invalid, fallback-invalid, and retained-identity-invalid values before model, persistence, or write-capable tool construction.

#### Scenario: Repository configuration is loaded

- **WHEN** a public docs-sync command runs for a repository
- **THEN** supported domain settings SHALL resolve from the documented repository root
- **AND** LLM settings SHALL resolve from the centralized TDT profile
- **AND** committed configuration SHALL contain no credential literal

#### Scenario: Unsupported configuration section

- **WHEN** configuration contains an unknown or legacy section
- **THEN** validation SHALL fail before model, persistence, or write-capable tool construction
- **AND** the error SHALL identify the supported replacement without echoing protected values

#### Scenario: Public option is accepted

- **WHEN** a documented option is accepted
- **THEN** the execution plan and report SHALL record its effective behavior
- **AND** the command SHALL NOT discard it through a compatibility placeholder

#### Scenario: Deprecated option is removed

- **WHEN** an option cannot be supported by the canonical pipeline
- **THEN** it SHALL be removed or rejected with actionable migration guidance
- **AND** help output and tests SHALL not advertise ignored behavior

#### Scenario: Environment variables override all config layers

- **GIVEN** a registered docs-sync model environment key is set
- **AND** agent and global YAML specify different models
- **WHEN** docs-sync loads configuration
- **THEN** its effective model and model-construction input SHALL use the environment value

#### Scenario: Repository config overrides TDT global

- **GIVEN** no higher-priority source is set for a supported docs-sync domain field
- **AND** repository configuration and a typed global/default projection specify different values for that field
- **WHEN** docs-sync loads configuration
- **THEN** the supported repository domain value SHALL win
- **AND** this precedence SHALL not authorize repository LLM fields

#### Scenario: Repository model override is rejected

- **GIVEN** repository configuration specifies a model, fallback, provider, or model behavior
- **WHEN** docs-sync loads configuration
- **THEN** it SHALL fail with migration guidance to the agent-specific TDT file

#### Scenario: Missing TDT global config is non-fatal

- **GIVEN** the selected TDT root has no global config
- **AND** no higher-priority model source is set
- **WHEN** docs-sync loads configuration
- **THEN** agent-specific configuration or typed defaults SHALL be used without error

#### Scenario: Invalid environment variable type rejected

- **GIVEN** a registered docs-sync numeric environment value is invalid
- **WHEN** docs-sync loads configuration
- **THEN** it SHALL fail with the logical key and no protected value

#### Scenario: Settings and model projections agree

- **WHEN** callers inspect `DocsSyncConfig.settings.model.primary`, the model shortcut, the generation runtime profile, the constructed primary/fallback chain, and the redacted diagnostics/report
- **THEN** all SHALL identify the same effective per-agent model, fallback order, provider route, behavior settings, source provenance, and source fingerprints
- **AND** none SHALL trigger a second configuration load or choose a different effective value

#### Scenario: Malformed configuration fails closed

- **GIVEN** the selected global, agent, repository, or explicit configuration source is malformed or has a non-mapping root
- **WHEN** docs-sync configuration is constructed
- **THEN** construction SHALL fail before model, persistence, or write-capable tool creation
- **AND** it SHALL not substitute typed defaults or report an apparently successful generation

#### Scenario: Secret-invalid configuration fails closed

- **GIVEN** a selected configuration source contains a literal credential or invalid secret reference
- **WHEN** docs-sync configuration or its diagnostic is constructed
- **THEN** it SHALL fail closed with only the logical field, source class, and environment-key metadata
- **AND** it SHALL not render the protected value or fall back to another credential

#### Scenario: Nested report preserves the effective profile

- **WHEN** a completed or failed generation report is normalized from a nested workflow result
- **THEN** its model, fallback/provider diagnostics, generation profile, completion state, provider error, and usage metadata SHALL describe the same profile used for construction
- **AND** outer default fields SHALL not replace missing nested values

#### Scenario: Nested full-sync report is normalized

- **WHEN** the workflow returns its report under a nested results object
- **THEN** the CLI SHALL present the nested report counts, generation outcome, approval state, and compliance result
- **AND** it SHALL not substitute zero-valued outer workflow fields

#### Scenario: Execution failure has a distinct exit status

- **WHEN** the normalized report says execution did not complete successfully
- **THEN** the command SHALL print the report and return the execution-failure exit code
- **AND** it SHALL not classify the result as ordinary documentation non-compliance

#### Scenario: Generation or documentation compliance fails

- **WHEN** execution completes but generation is incomplete, provider resolution fails, or actionable findings remain
- **THEN** the report SHALL mark compliance false and preserve the generation reason
- **AND** the command SHALL return the documented compliance-failure exit code

#### Scenario: Informational findings are reported

- **WHEN** a non-strict reporting command finds actionable gaps
- **THEN** it MAY return zero only where the command contract explicitly permits informational findings
- **AND** JSON and human-readable compliance SHALL remain false

#### Scenario: Discovery validation and generation share one profile

- **WHEN** one docs-sync operation constructs discovery, validation, and generation agent paths
- **THEN** every path SHALL receive the same resolved model, fallbacks, provider route, behavior, provenance, and source fingerprints
- **AND** no path SHALL independently load a replacement profile

#### Scenario: Invalid provider or fallback relationship fails before side effects

- **GIVEN** the selected profile contains an undefined provider, malformed fallback, unregistered model identifier, or cross-provider credential binding
- **WHEN** docs-sync configuration is constructed
- **THEN** construction SHALL fail before persistence initialization or write-capable tool construction
- **AND** no lower-priority model or other provider credential SHALL be substituted

#### Scenario: Runtime controls use one effective operation projection

- **GIVEN** the canonical resolved profile supplies timeout and iteration values
- **AND** no documented repository-domain override replaces either value
- **WHEN** docs-sync produces its configuration, settings projection, runtime profile, execution plan, agents, diagnostics, and report for the operation
- **THEN** every projection SHALL expose the same effective timeout and iteration values from the captured profile
- **AND** no projection SHALL silently replace either value with constructor, runtime, or compatibility defaults

#### Scenario: Supported repository runtime override remains consistent

- **GIVEN** repository configuration declares a supported docs-sync runtime control
- **WHEN** the operation applies that documented domain override
- **THEN** the resulting value SHALL be recorded as the effective operation value in configuration, settings, runtime, execution plan, diagnostics, and report
- **AND** the canonical source profile SHALL remain unchanged
- **AND** the override SHALL NOT authorize repository model, fallback, provider, behavior, or credential fields

#### Scenario: Typed provenance is normalized for public results

- **GIVEN** the captured profile stores typed or immutable provenance and fingerprint values
- **WHEN** docs-sync exposes diagnostics, normalized workflow results, JSON output, or reports
- **THEN** those public surfaces SHALL use one stable serializable mapping representation
- **AND** the representation SHALL preserve the logical field, source class, non-secret source-key or source-path metadata, alias metadata, and source fingerprint where present
- **AND** it SHALL contain no implementation object representation, private field, or protected value
- **AND** normalization SHALL NOT trigger another configuration load

#### Scenario: Retry reuses the captured operation configuration

- **GIVEN** a workflow attempt captured a resolved profile and effective operation controls
- **WHEN** execution retries a generation, validation, or orchestration step within the same public operation
- **THEN** the retry SHALL reuse the same non-secret configuration identity, model, fallback order, provider route, behavior, timeout, iteration values, provenance, and source fingerprints
- **AND** it SHALL NOT reopen configuration sources or silently substitute newly resolved values

#### Scenario: Resume restores the retained operation identity

- **GIVEN** retained workflow state contains sufficient non-secret configuration identity, source fingerprints, and effective operation controls
- **WHEN** resume validates that retained identity and reconstructs the operation successfully
- **THEN** the reconstructed operation SHALL expose the same model, fallback order, provider route, behavior, timeout, iteration values, provenance, and source fingerprints
- **AND** protected credential material SHALL NOT be persisted in or restored from workflow state
- **AND** any required credential access SHALL remain subject to the canonical process-local provider-binding boundary

#### Scenario: Resume fails when operation identity cannot be restored

- **GIVEN** retained configuration identity is missing, ambiguous, internally inconsistent, or cannot validate the required provider relationship and effective controls
- **WHEN** workflow resume is requested
- **THEN** resumption SHALL fail before model, persistence, or write-capable tool construction
- **AND** a newly resolved model, fallback, provider, credential binding, behavior, timeout, or iteration value SHALL NOT be silently substituted
- **AND** no pending approval or write state SHALL be advanced

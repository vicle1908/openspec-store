## MODIFIED Requirements

### Requirement: Canonical configuration and CLI truthfulness

`agent-docs-sync` SHALL load one documented domain configuration schema and one canonical resolved agent profile. LLM model, fallback, provider, and behavior precedence SHALL be explicit run override > registered docs-sync environment > registered shared model environment > agent-specific TDT YAML > global TDT YAML > defaults. Repository configuration MAY define docs-sync domain behavior but MUST NOT define LLM fields. Every public config projection and generation path SHALL use the same resolved profile. The system SHALL validate unknown, legacy, and invalid typed values before model, persistence, or write-capable tool construction.

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
- **THEN** all SHALL identify the same effective per-agent model, fallback order, provider route, behavior settings, and source provenance
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

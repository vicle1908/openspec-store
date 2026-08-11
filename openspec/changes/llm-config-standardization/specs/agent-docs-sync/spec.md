## MODIFIED Requirements

### Requirement: Canonical configuration and CLI truthfulness

`agent-docs-sync` SHALL load one documented repository-root configuration schema with 4-layer precedence: environment variables > repository config > TDT global config > code defaults. The system SHALL validate unknown or legacy keys and ensure every public CLI option either changes canonical execution or is removed with migration guidance. The system SHALL reject environment variables with invalid types for numeric fields.

#### Scenario: Repository configuration is loaded

- **WHEN** a public docs-sync command runs for a repository
- **THEN** configuration SHALL resolve from the documented repository root and centralized TDT environment boundary
- **AND** committed configuration SHALL contain no credential literal

#### Scenario: Unsupported configuration section

- **WHEN** configuration contains an unknown or legacy section that is not supported by the canonical schema
- **THEN** validation SHALL fail before model, persistence, or write-capable tool construction
- **AND** the error SHALL identify the supported replacement without echoing protected values

#### Scenario: Public option is accepted

- **WHEN** `base-ref`, `full`, LLM classification, override review, durability, or another documented option is accepted
- **THEN** the resulting execution plan and report SHALL record the option's effective behavior
- **AND** the command SHALL NOT discard the value through a compatibility placeholder

#### Scenario: Deprecated option is removed

- **WHEN** an option cannot be supported by the canonical pipeline
- **THEN** it SHALL be removed or rejected with an actionable migration error
- **AND** help output and tests SHALL not continue to advertise ignored behavior

#### Scenario: Environment variables override all config layers

- **GIVEN** `DOCS_SYNC_MODEL=openai-chat:gpt-4` is set
- **AND** the repo config.yaml specifies a different model
- **AND** TDT global config specifies a different model
- **WHEN** docs-sync loads configuration
- **THEN** the effective model SHALL be `openai-chat:gpt-4`

#### Scenario: Repository config overrides TDT global

- **GIVEN** no `DOCS_SYNC_*` env vars are set
- **AND** the repo config.yaml specifies `model: openai-chat:gpt-4`
- **AND** TDT global config specifies a different model
- **WHEN** docs-sync loads configuration
- **THEN** the effective model SHALL be `openai-chat:gpt-4`

#### Scenario: Missing TDT global config is non-fatal

- **GIVEN** `TDT_HOME` points to a directory without config.yaml
- **AND** no `DOCS_SYNC_*` env vars are set
- **WHEN** docs-sync loads configuration
- **THEN** code defaults SHALL be used without error

#### Scenario: Invalid environment variable type rejected

- **GIVEN** `DOCS_SYNC_MAX_ITERATIONS=abc`
- **WHEN** docs-sync loads configuration
- **THEN** a `ValueError` SHALL be raised with a descriptive message

#### Scenario: Nested full-sync report is normalized

- **WHEN** the workflow returns its report under a nested results object
- **THEN** the CLI SHALL present the nested report counts, generation outcome, approval state, and compliance result
- **AND** it SHALL not display zero-valued fields from the outer workflow state in place of the report

#### Scenario: Execution failure has a distinct exit status

- **WHEN** the normalized report says execution did not complete successfully
- **THEN** `docs-sync sync` SHALL print the report and return the execution-failure exit code
- **AND** it SHALL not classify the result as ordinary documentation non-compliance

#### Scenario: Generation or documentation compliance fails

- **WHEN** workflow execution completes but generation is incomplete, provider resolution fails, or actionable documentation findings remain
- **THEN** the report SHALL mark documentation compliance false and preserve the generation reason/error
- **AND** `docs-sync sync` SHALL return the documentation/compliance failure exit code

#### Scenario: Informational findings are reported

- **WHEN** a non-strict reporting command finds actionable gaps
- **THEN** it MAY return zero only where the command contract explicitly permits informational findings
- **AND** the JSON and human-readable compliance field SHALL remain false

### Requirement: Truthful audit outcome contract

Docs-sync audit results SHALL distinguish successful execution from documentation compliance. The report SHALL expose stable counts for actionable gaps, excluded findings, broken links, and Diataxis violations. A strict mode SHALL fail when actionable compliance findings remain or execution does not complete successfully. A discovery failure SHALL NOT be represented as a successful empty scan. Generation failures (max_iterations, timeout, provider_error) SHALL be treated as non-compliant regardless of audit-phase compliance status.

#### Scenario: Audit completes with gaps

- **WHEN** scanning succeeds but actionable documentation gaps or Diataxis violations are found
- **THEN** execution SHALL be reported as successful
- **AND** documentation compliance SHALL be reported as failed
- **AND** the result SHALL not use one ambiguous `validation_passed=true` field to represent both outcomes

#### Scenario: Strict audit has findings

- **WHEN** `docs-sync audit --strict` finds actionable gaps, broken local links, or Diataxis violations
- **THEN** the command SHALL return non-zero with deterministic finding counts

#### Scenario: Strict audit discovery fails

- **WHEN** `docs-sync audit --strict` cannot discover the requested repository
- **THEN** the report SHALL set `execution_succeeded` to false
- **AND** the command SHALL return non-zero rather than reporting an empty compliant scan

#### Scenario: Informational audit has findings

- **WHEN** audit runs without strict mode and finds actionable gaps
- **THEN** it MAY return zero to support reporting workflows
- **AND** the JSON compliance field SHALL still be false

#### Scenario: Compatibility alias during migration

- **WHEN** audit JSON is emitted during the first compatibility release
- **THEN** `validation_passed` SHALL remain present as a deprecated alias of `documentation_compliant`
- **AND** it SHALL NOT represent `execution_succeeded`
- **AND** the alias SHALL be removed after that one compatibility release

#### Scenario: Generation failure overrides compliance

- **GIVEN** the audit phase found no documentation gaps
- **AND** the generation phase failed with `max_iterations` reached
- **WHEN** the CLI exit code is computed for `sync`
- **THEN** the exit code SHALL be 1 (non-compliant)
- **AND** the report SHALL indicate the generation failure reason

#### Scenario: Execution failure maps to exit 2

- **GIVEN** `execution_succeeded` is false
- **WHEN** the CLI exit code is computed
- **THEN** the exit code SHALL be 2 (execution failure)

#### Scenario: Provider error treated as non-compliant

- **GIVEN** `generation_provider_error` is set in the report
- **WHEN** the CLI exit code is computed for `sync`
- **THEN** the exit code SHALL be 1 (non-compliant)

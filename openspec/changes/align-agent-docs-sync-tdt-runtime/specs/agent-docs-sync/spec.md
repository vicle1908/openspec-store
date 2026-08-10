## MODIFIED Requirements

### Requirement: Canonical configuration and CLI truthfulness

`agent-docs-sync` SHALL load one documented repository-root configuration schema, resolve the shared TDT runtime boundary, validate unknown or legacy keys, and ensure every public CLI option either changes canonical execution or is removed with migration guidance. Full-sync reports SHALL be normalized before presentation, and exit status SHALL distinguish execution failure from documentation or generation non-compliance.

#### Scenario: Repository configuration is loaded

- **WHEN** a public docs-sync command runs for a repository
- **THEN** configuration SHALL resolve from the documented repository root and centralized TDT environment boundary
- **AND** committed configuration SHALL contain no credential literal

#### Scenario: Unsupported configuration section

- **WHEN** configuration contains an unknown or legacy section that is not supported by the canonical schema
- **THEN** validation SHALL fail before model, persistence, or write-capable tool construction
- **AND** the error SHALL identify the supported replacement without echoing protected values

#### Scenario: Public option is accepted

- **WHEN** `base-ref`, `full`, LLM classification, override review, durability, thread identity, or another documented option is accepted
- **THEN** the resulting execution plan and report SHALL record the option's effective behavior
- **AND** the command SHALL NOT discard the value through a compatibility placeholder

#### Scenario: Deprecated option is removed

- **WHEN** an option cannot be supported by the canonical pipeline
- **THEN** it SHALL be removed or rejected with an actionable migration error
- **AND** help output and tests SHALL not continue to advertise ignored behavior

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

## ADDED Requirements

### Requirement: Generation outcome is preserved

The canonical generation stage SHALL preserve whether each agent request completed, its machine-readable reason, bounded iteration count, approval state, and redacted provider error through the workflow report.

#### Scenario: Generation completes with output

- **WHEN** an agent returns a completed output
- **THEN** the report SHALL count the generated update and record completion and iteration metadata

#### Scenario: Generation stops without output

- **WHEN** an agent returns `max_iterations`, timeout, provider, connectivity, budget, or approval-needed status without output
- **THEN** the report SHALL record the reason and relevant metadata
- **AND** it SHALL report zero generated updates for that request

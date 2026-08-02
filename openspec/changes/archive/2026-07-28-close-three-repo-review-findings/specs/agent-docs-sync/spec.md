## MODIFIED Requirements

### Requirement: Production documentation discovery boundary

By default, docs-sync discovery and audit SHALL scan production source while
deriving actionable documentation obligations from package exports, configured
console-script/CLI entrypoints, deployment and configuration artifacts, and
explicit documentation mappings. Tests, virtual environments, caches,
generated artifacts, and repository metadata SHALL be excluded unless an
explicit option requests them. Unexported production internals SHALL remain
visible in scan evidence but SHALL be informational unless explicitly mapped.
Explicit directory mappings SHALL apply to descendant files using deterministic
most-specific-prefix precedence, while an exact file mapping SHALL remain
authoritative.

#### Scenario: Default repository discovery

- **WHEN** `docs-sync discover` scans a Python repository with default options
- **THEN** scan evidence SHALL include production source modules and
  documentation files
- **AND** actionable mappings SHALL identify their public-surface provenance
  as export, CLI entrypoint, deployment/config artifact, or explicit mapping
- **AND** tests, `.venv`, `__pycache__`, `.pyc`, coverage output, and generated
  build directories SHALL not be classified as documentation needs

#### Scenario: Internal production module has no explicit mapping

- **WHEN** an unexported production module is not a CLI/deployment/config
  surface and has no explicit documentation mapping
- **THEN** its scan finding SHALL be retained as informational evidence
- **AND** absence of a one-to-one document SHALL not count as an actionable gap

#### Scenario: Explicit test-source discovery

- **WHEN** a caller explicitly enables test or internal source discovery
- **THEN** those files MAY be classified
- **AND** the report SHALL identify that non-default boundary

#### Scenario: Explicit directory mapping covers descendants

- **WHEN** a source file is a descendant of one or more configured directory mappings
- **THEN** the most-specific matching directory mapping SHALL determine its target documentation
- **AND** an exact file mapping SHALL take precedence over directory mappings

### Requirement: Truthful audit outcome contract

Docs-sync audit results SHALL distinguish successful execution from
documentation compliance. The report SHALL expose stable counts for actionable
gaps, excluded findings, broken links, and Diataxis violations. A strict mode
SHALL fail when actionable compliance findings remain or execution does not
complete successfully. A discovery failure SHALL NOT be represented as a
successful empty scan.

#### Scenario: Audit completes with gaps

- **WHEN** scanning succeeds but actionable documentation gaps or Diataxis
  violations are found
- **THEN** execution SHALL be reported as successful
- **AND** documentation compliance SHALL be reported as failed
- **AND** the result SHALL not use one ambiguous `validation_passed=true` field
  to represent both outcomes

#### Scenario: Strict audit has findings

- **WHEN** `docs-sync audit --strict` finds actionable gaps, broken local links,
  or Diataxis violations
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
- **THEN** `validation_passed` SHALL remain present as a deprecated alias of
  `documentation_compliant`
- **AND** it SHALL NOT represent `execution_succeeded`
- **AND** the alias SHALL be removed after that one compatibility release

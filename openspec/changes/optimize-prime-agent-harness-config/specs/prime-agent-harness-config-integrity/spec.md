# Spec Delta

## Purpose

Defines the verifiable invariants a Prime Agent user-level configuration must
satisfy before it counts as a working harness: the selected model actually
receives the assembled system prompt, every declared MCP credential reference
resolves, the always-loaded prompt surface stays bounded, model metadata is
complete enough to report usage, and degraded-mode recovery is configured.

## ADDED Requirements

### Requirement: A model SHALL NOT be selected as default unless it is verified to receive the assembled system prompt

Before a Prime Agent provider/model selection becomes `defaultProvider`/`defaultModel`, it SHALL be verified that the endpoint delivers the harness system prompt: the assembled static layers, the project-context section, and the skills inventory. A selection that returns a constant prompt-token count regardless of system-prompt size SHALL be treated as non-delivering and SHALL NOT be the default.

#### Scenario: Non-delivering selection is rejected as default

- **WHEN** a candidate selection is probed with a baseline request and the same request carrying a large appended system prompt
- **THEN** the prompt-token counts SHALL differ by approximately the appended size for the selection to qualify
- **AND** a selection whose prompt-token count is unchanged SHALL NOT be written as the default

#### Scenario: A delivering selection is confirmed before it replaces the default

- **WHEN** a replacement default selection is proposed
- **THEN** a request SHALL confirm the model echoes a value supplied only in the system prompt
- **AND** the selection SHALL report a prompt-token count consistent with the assembled prompt for the working directory

#### Scenario: Deliverability is recorded per registration, not per endpoint

- **WHEN** two providers share one `baseUrl` but differ in credential or model ID
- **THEN** deliverability SHALL be recorded per provider/model registration
- **AND** a verified registration SHALL NOT be assumed to make a sibling registration deliver

### Requirement: Every MCP stdio environment reference SHALL resolve from the kernel environment

Each `mcpServers` stdio `env` entry SHALL name a variable that is exported into the environment the Python kernel inherits. A reference that names an unexported variable SHALL be treated as a configuration defect, not a runtime condition to tolerate.

#### Scenario: Unresolved reference fails loudly

- **WHEN** the configured reference names a variable absent from the kernel environment
- **THEN** the server SHALL fail with an explicit unresolved-reference error naming the variable
- **AND** the configuration SHALL be corrected so the named variable is exported by the login shell profile

#### Scenario: Divergent token values for one service are reported

- **WHEN** the same service token is held in more than one client configuration
- **THEN** the divergence SHALL be reported by length and hash without printing either value
- **AND** the configuration SHALL converge on the value the kernel environment can resolve

#### Scenario: A kernel restart is required after the reference is repaired

- **WHEN** the exported variable changes but the running kernel predates the change
- **THEN** the reference SHALL remain unresolved until the daemon and kernel are restarted
- **AND** verification SHALL confirm resolution after restart rather than assuming it

### Requirement: The always-loaded prompt surface SHALL be bounded and counted

The skills inventory and discovered project-context files SHALL be measured in prompt tokens for the active working directory, and their combined size SHALL be recorded. A single discovered context file SHALL NOT dominate the prompt by loading unconditionally into every descendant session.

#### Scenario: Prompt cost is attributed by ablation

- **WHEN** the assembled prompt is measured with skills discovery and with context-file discovery separately disabled
- **THEN** the token delta SHALL attribute cost to the skills inventory and to the context files
- **AND** the measurement SHALL be recorded per working directory

#### Scenario: An oversized workspace context file is relocated

- **WHEN** a discovered context file exceeds the applicable instruction-hygiene line target
- **THEN** task-specific content SHALL move to an on-demand location while load-bearing boundaries remain in the discovered file
- **AND** the relocated content SHALL remain reachable by an explicit path

#### Scenario: Duplicated skill discovery is eliminated rather than deduplicated at load

- **WHEN** the same skill is reachable from more than one discovery root
- **THEN** the redundant exposure SHALL be removed at the source
- **AND** the remaining inventory SHALL report a count that matches the intended skill set

### Requirement: Registered models SHALL carry complete usage and reasoning metadata

Each model registered for Prime Agent SHALL declare cost metadata and, where the model supports reasoning, a thinking-level mapping. A model lacking cost metadata SHALL NOT silently report zero cost for its usage.

#### Scenario: Cost metadata produces non-zero usage reporting

- **WHEN** a session runs on a registered model and usage is reported
- **THEN** the reported cost SHALL reflect the declared per-model rates
- **AND** a model with no declared rates SHALL be identifiable as unreported rather than free

#### Scenario: Thinking level is mapped or clamped explicitly

- **WHEN** a global default thinking level is configured and a model declares a supported-level mapping
- **THEN** the level sent to the provider SHALL be the mapped level or an explicitly documented clamp
- **AND** an unmapped level SHALL NOT be silently discarded

#### Scenario: Output limits are declared against the context window

- **WHEN** a model declares a context window
- **THEN** its maximum output SHALL be declared and SHALL be consistent with that window
- **AND** a model omitting the limit SHALL be reported

### Requirement: Degraded-mode provider recovery SHALL be configured for reseller endpoints

Where a provider is a reseller endpoint subject to quota exhaustion, the configuration SHALL declare a backup model or an explicit wait policy so an exhausted quota degrades predictably instead of parking indefinitely.

#### Scenario: Backup model takes over an exhausted primary

- **WHEN** the primary provider reports quota exhaustion and a backup model is configured
- **THEN** the failed turn SHALL continue on the backup model
- **AND** the session SHALL return to the primary on the next turn

#### Scenario: Absent a backup, the wait bounds are explicit

- **WHEN** no backup model is configured
- **THEN** the wait and park bounds SHALL be recorded as the intended behavior
- **AND** an unbounded park SHALL NOT be the unstated default

### Requirement: Prime Agent configuration SHALL be free of drift and stale artifacts

The configuration SHALL NOT retain superseded backup files, duplicate provider entries that share one endpoint without a stated reason, or an npm command whose configured prefix disagrees with the machine's global npm root.

#### Scenario: Superseded backups are removed

- **WHEN** the agent directory is inspected
- **THEN** superseded configuration backups SHALL be removed or relocated out of the live configuration directory

#### Scenario: Duplicate endpoints are consolidated or justified

- **WHEN** two provider entries share one `baseUrl`
- **THEN** they SHALL be consolidated, or the reason for the distinct entries SHALL be recorded

#### Scenario: npm prefix agrees with the machine global root

- **WHEN** the configured npm command is inspected
- **THEN** its prefix SHALL resolve to the same global modules root the machine reports
- **AND** any non-standard flag SHALL be documented or removed

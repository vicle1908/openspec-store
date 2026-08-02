# Jira Space Setup Standard

## ADDED Requirements

### Requirement: Setup workflow SHALL begin with project-style and permission preflight and SHALL route into a style-specific workflow family

The Jira space setup workflow SHALL identify the target project's Jira style, required permissions, and viable reference-project candidates before attempting any field, board, filter, or dashboard alignment. The workflow SHALL use the shared `tdt_core.clients` Jira factory and Jira Cloud API v3-compatible access paths for all automated inspection. After identifying style, the workflow SHALL route into the appropriate setup family: `team-managed / modern` or `classic / legacy`.

#### Scenario: Target project style is determined before alignment

- **WHEN** an operator or agent starts setup or alignment for a Jira project
- **THEN** the workflow SHALL determine whether the project behaves as `next-gen`, `classic`, or an otherwise constrained shape before choosing any alignment strategy
- **AND** the workflow SHALL record that style in the setup evidence

#### Scenario: Permissions are insufficient for automation

- **WHEN** the authenticated Jira account lacks admin or project-admin capabilities required for a planned operation
- **THEN** the workflow SHALL report the missing capability as an actionable blocker
- **AND** the workflow SHALL NOT claim the project is setup-ready

#### Scenario: Reference project is selected

- **WHEN** the workflow chooses an existing Jira project as the baseline for parity or alignment
- **THEN** it SHALL record the chosen project key, the reason it was selected, and any known deltas between the target and reference projects

#### Scenario: Target project style selects the setup workflow family

- **WHEN** the workflow has determined whether the target project behaves as `next-gen`, `classic`, or an otherwise constrained shape
- **THEN** it SHALL select the corresponding setup workflow family before attempting any apply or remediation step
- **AND** it SHALL preserve that workflow-family selection in the setup evidence

### Requirement: Team-managed / modern setup SHALL be detection-first and API-surface-bound

For team-managed or otherwise `next-gen` Jira projects, the setup workflow SHALL treat project+issue-type metadata as the primary automated detection surface, SHALL treat public REST responses as evidence rather than full layout-control surfaces, and SHALL limit remediation attempts to explicitly supported Jira Cloud API surfaces.

#### Scenario: Team-managed project enters modern setup workflow

- **WHEN** the target Jira project is classified as `next-gen` or team-managed
- **THEN** the workflow SHALL use the `team-managed / modern` setup family
- **AND** it SHALL NOT invoke classic screen/tab alignment as if it were the authoritative control plane

#### Scenario: Team-managed remediation exceeds supported write surfaces

- **WHEN** required work-item field exposure depends on behavior that is not confirmed to be writable through supported public Jira Cloud APIs
- **THEN** the workflow SHALL stop at detection, evidence capture, and an explicit `unsupported-by-current-api-surface` or `supported-but-unvalidated-here` result, whichever is accurate
- **AND** it SHALL NOT report that an automated apply step completed the remediation

#### Scenario: Team-managed inspection proves global field existence but not project exposure

- **WHEN** Jira Cloud exposes instance-level evidence that `Original Estimate`, `Time Tracking`, or comparable planning fields exist globally or that time tracking is enabled instance-wide
- **THEN** the workflow SHALL treat that evidence as necessary but insufficient for project readiness
- **AND** it SHALL still verify per-issue-type exposure in the target team-managed project before reporting setup readiness

#### Scenario: Team-managed setup inspects visibility through project metadata surfaces

- **WHEN** the workflow inspects a team-managed project's planning/time-tracking readiness
- **THEN** it SHALL use project+issue-type metadata surfaces such as create-metadata, issue-type metadata, edit-metadata, project field search, project properties, project feature readback, and supported field-association APIs when available
- **AND** it SHALL record which surfaces were inspected, what each surface proved, and whether the result reflects global Jira capability or target-project exposure

### Requirement: Classic / legacy setup SHALL use explicit alignment semantics

For classic Jira projects, the setup workflow SHALL treat screens, tabs, schemes, and other classic Jira configuration objects as the primary alignment surfaces. When supported APIs, permissions, and explicit identifiers are available, the workflow MAY perform guarded apply operations against those surfaces, but it SHALL still require read-back validation before reporting success.

#### Scenario: Classic project enters legacy setup workflow

- **WHEN** the target Jira project is classified as `classic`
- **THEN** the workflow SHALL use the `classic / legacy` setup family
- **AND** it MAY plan or execute guarded screen/tab alignment steps when the required identifiers and permissions are available

### Requirement: Setup workflow SHALL produce canonical filter outputs

The Jira space setup workflow SHALL create, validate, or explicitly preserve a canonical set of shared Jira filters that become the durable automation entry points for dashboards, ticket intelligence, reporting, and future setup runs.

#### Scenario: Canonical filters are created or validated

- **WHEN** a setup run reaches the filter-definition phase
- **THEN** the workflow SHALL produce a stable set of named filters with captured JQL, filter IDs, and sharing state
- **AND** each filter SHALL be suitable for reuse by downstream automation without requiring ad hoc operator name discovery

#### Scenario: Filter sharing state is validated

- **WHEN** a canonical filter is expected to support team-visible dashboards or reports
- **THEN** the workflow SHALL verify whether the filter is shared appropriately for the intended audience
- **AND** it SHALL record any sharing mismatch as follow-up work

#### Scenario: Existing filters drift from the standard

- **WHEN** a project already contains similarly named or historically used filters
- **THEN** the workflow SHALL compare them against the intended canonical set
- **AND** it SHALL record whether they can be reused, must be replaced, or require explicit programmatic follow-up due to naming, sharing, or scope drift

### Requirement: Setup workflow SHALL validate planning and time-tracking capabilities per issue type

The Jira space setup workflow SHALL inspect setup-readiness capabilities per issue type instead of treating estimation as a single project-wide boolean. For team-managed software projects, the workflow SHALL use Jira Cloud create-metadata or equivalent project+issue-type metadata endpoints as the primary detection surface, SHALL treat `Story`, `Task`, `Bug`, and `Subtask` support for `Story Points`, `Original Estimate`, and `Time Tracking` as the target planning-ready standard, and SHALL record both the live baseline observed in reference spaces and any remaining issue-type or capability gaps explicitly before claiming parity.

#### Scenario: Team-managed work item types support required setup capabilities

- **WHEN** the target Jira project is a team-managed or otherwise `next-gen` software project
- **THEN** the workflow SHALL verify whether work item types such as `Story`, `Task`, `Bug`, and `Subtask` expose supported `Story Points`, `Original Estimate`, and `Time Tracking` fields using Jira Cloud project+issue-type metadata such as create-metadata
- **AND** it SHALL capture the field ID, field name, canonical capability kind, detection source, and supported issue types in the setup evidence

#### Scenario: Work item type omits a required capability

- **WHEN** any required work item type such as `Story`, `Task`, `Bug`, or `Subtask` does not expose one or more required capabilities
- **THEN** the workflow SHALL treat that as a blocking setup-readiness gap
- **AND** it SHALL preserve the missing capability list in the setup evidence for downstream consumers

#### Scenario: Capability support is only partially aligned

- **WHEN** some required planning or time-tracking capabilities are present but others are not
- **THEN** the workflow SHALL report a partial-success outcome for setup readiness
- **AND** it SHALL distinguish between the stricter target standard and the weaker live baseline currently observed in other spaces before claiming parity

#### Scenario: Reference spaces show weaker live baselines

- **WHEN** reference team-managed spaces expose only a subset of the target capabilities, such as `Story Points` plus `Time Tracking` without `Original Estimate`
- **THEN** the workflow SHALL record that observed baseline as comparative evidence
- **AND** it SHALL NOT downgrade the canonical target standard solely to match incomplete reference spaces
- **AND** it SHALL guide the operator to bring the target project to at least the best observed reference baseline while preserving the stricter desired standard in the final readiness report

#### Scenario: Instance-level capability and project-level exposure diverge

- **WHEN** Jira instance metadata proves that time tracking is enabled globally and that system fields such as `timeoriginalestimate` or `timetracking` exist, but the target team-managed project does not expose them in create/edit metadata for required work item types
- **THEN** the workflow SHALL classify the gap as `project exposure missing` rather than `field unavailable`
- **AND** it SHALL preserve both the instance-level proof and the project-level absence in the setup evidence

### Requirement: Existing project boards SHALL be audited before setup changes are declared complete

The Jira space setup workflow SHALL inspect existing boards for the target project and SHALL verify that each board’s resolved filter wiring matches the intended project scope before the project is declared setup-ready.

#### Scenario: Existing board is discovered for the target project

- **WHEN** the target project already has one or more Jira boards, such as the live EW board `953`
- **THEN** the workflow SHALL capture each board ID, board name, and board type as part of the setup evidence
- **AND** it SHALL treat those boards as audit targets rather than assuming a new board must be created

#### Scenario: Existing board points at an unexpected filter

- **WHEN** the workflow inspects an existing Jira board for the target project
- **THEN** it SHALL capture the board ID, board name, and resolved filter metadata
- **AND** it SHALL flag any mismatch between the board's intended project scope and the actual filter JQL

#### Scenario: Existing board cannot be fully validated automatically

- **WHEN** the workflow can identify the board but cannot fully confirm the effective filter wiring or backlog behavior through supported automated checks
- **THEN** it SHALL record the board as partially validated
- **AND** it SHALL emit an explicit `validation-incomplete` result rather than claiming the board is fully setup-ready

### Requirement: Board and dashboard setup SHALL be validated against live Jira behavior

The Jira space setup workflow SHALL treat boards and dashboards as validation-sensitive layers above canonical filters. It SHALL verify board/filter wiring and SHALL report unsupported or non-persisted dashboard gadget configuration instead of assuming API success equals correct live behavior. Dashboard validation and rollback behavior SHALL follow the canonical contract in `openspec/changes/jira-dashboard-automation/specs/dashboard-automation-core/spec.md`.

#### Scenario: Dashboard gadget configuration does not persist

- **WHEN** the workflow attempts to configure dashboard gadgets through Jira Cloud APIs
- **THEN** it SHALL validate the resulting gadget configuration through read-back or equivalent live checks
- **AND** it SHALL record unsupported gadget-property behavior as an explicit `api-write-nonpersistent` or `unsupported-by-current-api-surface` result rather than reporting success

#### Scenario: No dashboard should be created automatically

- **WHEN** the project is not yet filter-ready or gadget behavior is known to be unsupported for the intended layout
- **THEN** the workflow SHALL allow dashboards to be skipped
- **AND** it SHALL still capture the reason and validation outcome

### Requirement: Setup evidence SHALL capture automation-ready identifiers and blocked/unsupported outcomes

A completed Jira space setup or alignment run SHALL emit durable evidence that downstream operators and agents can use without repeating the original research. The evidence SHALL include identifiers, naming conventions, validation outcomes, unsupported or blocked API states, and an explicit setup-readiness outcome.

#### Scenario: Setup run succeeds partially

- **WHEN** some automated steps succeed but other steps remain blocked by permissions, Jira Cloud API limits, or project-shape constraints
- **THEN** the workflow SHALL report a partial-success outcome
- **AND** it SHALL distinguish completed outputs from remaining blocked or unsupported actions

#### Scenario: Automation-ready identifiers are captured

- **WHEN** a setup run creates or validates reusable Jira artifacts
- **THEN** it SHALL record project keys, board IDs, filter IDs, dashboard IDs when applicable, canonical names, and relevant JQL or configuration summaries

#### Scenario: Required setup step is unsupported or blocked

- **WHEN** a required setup step cannot be completed safely through the available API-supported workflows
- **THEN** the workflow SHALL record the exact blocked or unsupported operation and the reason it remains unresolved
- **AND** it SHALL classify the state as one of: `implemented-and-supported`, `supported-but-unvalidated-here`, `unsupported-by-current-api-surface`, `permission-blocked`, or `validation-incomplete`
- **AND** it SHALL preserve enough context for a future automation improvement or API-surface reassessment

#### Scenario: Success criteria are evaluated

- **WHEN** the workflow finishes
- **THEN** it SHALL determine whether the project is setup-ready for downstream automation based on preflight status, canonical filter readiness, board/dashboard validation, and captured blocked or unsupported items
- **AND** it SHALL report that outcome explicitly

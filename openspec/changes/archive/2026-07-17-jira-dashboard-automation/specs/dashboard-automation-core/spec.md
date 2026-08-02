# Dashboard Automation Core — Specification

**Capability:** dashboard-automation-core

## ADDED Requirements

### Requirement: Jira dashboard lifecycle commands

The `jira-skill` CLI SHALL provide a dashboard command group that creates, rebuilds, inspects, validates, and dry-runs Jira Cloud dashboards using `tdt_core.clients.jira.JiraClientFactory` and `PatchedJira` dashboard REST helpers.

#### Scenario: Create dashboard from the default saved filter

- **WHEN** an operator runs `jira-skill dashboard create --name <name>` without a filter override and default-filter resolution yields exactly one configured filter
- **THEN** the CLI SHALL use that resolved saved filter for the baseline dashboard workflow and place the default dashboard gadget layout on the created or matched dashboard

#### Scenario: Default filter resolution is ambiguous

- **WHEN** an operator runs `jira-skill dashboard create --name <name>` without `--filter-id` and the configured default-filter source yields multiple filters
- **THEN** the CLI SHALL fail fast with an error that instructs the operator to pass `--filter-id` explicitly

#### Scenario: Create dashboard from an explicit saved filter

- **WHEN** an operator runs `jira-skill dashboard create --name <name> --filter-id 15269`
- **THEN** the CLI SHALL find or create a Jira Cloud dashboard with that exact name and place the default dashboard gadget layout on it for filter `15269`

#### Scenario: Rebuild an existing dashboard

- **WHEN** an operator runs `jira-skill dashboard rebuild --dashboard-id <id> --layout <layout-file> --filter-id 15269`
- **THEN** the CLI SHALL remove all existing gadgets from that dashboard and replace them with the gadgets declared in the requested layout

#### Scenario: Dry-run a dashboard layout

- **WHEN** an operator runs `jira-skill dashboard create --dry-run --layout <layout-file> --filter-id 15269`
- **THEN** the CLI SHALL print the planned dashboard payload and gadget placement plan without sending Jira mutation requests

### Requirement: Layout-driven gadget declarations

The system SHALL represent dashboard gadget sets as declarative layout files so operators and agents can define dashboard metric sets without editing Python source.

#### Scenario: Load a bundled layout file

- **WHEN** an operator passes `--layout default-bug-dashboard.yaml`
- **THEN** the CLI SHALL resolve the bundled layout and expand its gadget declarations into concrete placement operations

#### Scenario: Reject an invalid layout

- **WHEN** a layout file omits a required gadget field such as `title`, `uri`, `column`, or `row`
- **THEN** the CLI SHALL fail fast with a validation error that identifies the missing field and the affected gadget entry

### Requirement: Logged-in view sharing as the default dashboard policy

The canonical dashboard workflow SHALL default every created or updated dashboard to view access for all logged-in Jira users and SHALL NOT grant authenticated edit access unless explicit edit permissions are supplied.

#### Scenario: New dashboard gets logged-in view access

- **WHEN** the CLI creates a new dashboard through the canonical workflow
- **THEN** the dashboard SHALL be created with view sharing for all logged-in Jira users

#### Scenario: Dashboard update preserves view-only default

- **WHEN** the CLI updates dashboard sharing without explicit edit-permission input
- **THEN** the workflow SHALL set logged-in view access and SHALL leave authenticated edit access disabled by default

### Requirement: Filter-backed gadget configuration policy

The system SHALL apply filter-backed gadget configuration using Jira Cloud dashboard item property APIs, and it SHALL fully configure the supported built-in gadget set without requiring manual Jira UI follow-up. The bundled default dashboard SHALL treat every supported gadget as required. For unrecognized gadgets, the workflow MAY still fall back to best-effort handling.

#### Scenario: Configure required Filter Results gadget

- **WHEN** the CLI places a required Filter Results gadget for filter `15269`
- **THEN** it SHALL write a `config` property containing `filterId: "15269"` and any declared display properties such as `num` or `columnNames`
- **AND** the default bundled layout SHALL include a fully configured baseline payload with `columnNames`, `refresh`, and `isConfigured` so the gadget mirrors Jira UI expectations more closely
- **AND** dashboard creation SHALL be considered unsuccessful until that required filter binding validates cleanly

#### Scenario: Configure supported built-in chart and statistics gadgets

- **WHEN** the CLI places a supported built-in gadget such as Pie Chart, Work Item Statistics, Issue Type Statistics, Created vs. Resolved, Average Age, or Time Since for filter `15269`
- **THEN** it SHALL write the filter mapping to the v3 `config` property using `projectOrFilterId: "filter-15269"`
- **AND** it SHALL persist the gadget-native fields declared by the bundled layout, including `isConfigured: "true"` for every supported gadget in the default dashboard, `isCumulative: "false"` for the Time Since gadget
- **AND** validation SHALL treat any mismatch in those supported-gadget invariants as a required failure

#### Scenario: Configure unrecognized gadget in best-effort mode

- **WHEN** a layout includes a gadget type outside the supported built-in set
- **THEN** the workflow MAY attempt the declared properties best-effort
- **AND** validation SHALL surface the gadget as unsupported or best-effort instead of silently reporting success

### Requirement: Native variant dashboard layouts

The system SHALL support richer native Jira dashboard variants that use multiple saved filters, custom-field pivots, and effort-oriented gadgets when those are useful for the dashboard question being answered.

#### Scenario: Layout declares a per-gadget filter override

- **WHEN** a layout entry declares its own `filterId` instead of inheriting the dashboard-level filter
- **THEN** the CLI SHALL use that gadget-specific saved filter when placing and validating the gadget
- **AND** validation SHALL compare the stored gadget config against the gadget-specific filter binding rather than the dashboard-level default

#### Scenario: Layout uses a Workload Pie Chart

- **WHEN** a layout includes the native Workload Pie Chart gadget
- **THEN** the CLI SHALL treat it as a supported native gadget when the underlying Jira data contains the required time-tracking fields such as Original estimate, Time spent, or Current estimate
- **AND** validation SHALL report a clear mismatch if the source filter does not expose the expected effort fields or if Jira does not persist the gadget's saved configuration cleanly

#### Scenario: Layout uses custom-field statistics pivots

- **WHEN** a layout entry declares a Pie Chart gadget with `statType` pointing at a searchable custom field
- **THEN** the dashboard workflow SHALL preserve those field identifiers in the gadget properties and SHALL treat them as first-class native pivots
- **AND** validation SHALL surface unsupported or unsearchable field choices as a configuration mismatch so operators can adjust the filter or field selection

### Requirement: Dashboard validation workflow

The system SHALL provide a validation mode that reads back dashboard gadget configuration and reports whether each filter-backed gadget is configured as intended, distinguishing required contract failures from best-effort follow-up.

#### Scenario: Validation reports configured supported dashboard

- **WHEN** an operator runs `jira-skill dashboard validate --dashboard-id <id> --filter-id 15269` for a dashboard made only of supported built-in gadgets
- **THEN** the CLI SHALL list each gadget with its title, gadget ID, and whether its stored configuration matches the expected gadget profile invariants
- **AND** overall validation success SHALL require every supported gadget in the bundled layout to validate cleanly

#### Scenario: Validation reports configuration mismatch

- **WHEN** a gadget exists but its stored configuration does not match the expected filter or required property values
- **THEN** the CLI SHALL report that gadget as mismatched and SHALL identify the missing or incorrect property values
- **AND** mismatches for required gadgets SHALL fail validation while best-effort mismatches SHALL be surfaced as follow-up warnings

#### Scenario: Validation reports missing declared gadget

- **WHEN** a gadget declared in the bundled layout is absent from the dashboard
- **THEN** the CLI SHALL report that gadget as missing
- **AND** missing gadgets in a required bundled layout SHALL fail validation

### Requirement: Strict supported-gadget contract with explicit unsupported signaling

The system MUST treat Jira Cloud gadget property automation as strict for the supported built-in gadget set and SHALL surface warnings whenever validation detects unsupported or unrecognized gadget behavior.

#### Scenario: Unsupported gadget property behavior

- **WHEN** a gadget property write is ignored or not persisted by Jira Cloud for an unrecognized gadget type
- **THEN** the CLI SHALL emit a warning identifying the gadget, the attempted properties, and that manual Jira UI follow-up may be required

#### Scenario: Partial dashboard success

- **WHEN** one gadget is added successfully but another gadget fails placement or validation
- **THEN** the CLI SHALL preserve the successful gadget operations and SHALL return a summary that identifies both successful and failed gadget actions

### Requirement: Agent skill guidance for dashboard operations

The `.agents` skill set SHALL document the supported Jira dashboard workflow, known API limits, recommended gadget sets for filter-backed issue dashboards, and required validation steps.

#### Scenario: Agent needs dashboard workflow guidance

- **WHEN** an agent is asked to create or update a Jira dashboard for a saved filter
- **THEN** the dashboard skill SHALL guide the agent to use `jira-skill` dashboard commands, layout files, validation mode, and current contract notes instead of ad hoc REST experimentation

#### Scenario: Agent needs metric recommendations

- **WHEN** an agent is asked to build an important-metrics dashboard for a bug or issue filter
- **THEN** the dashboard skill SHALL recommend a native Jira gadget profile that starts with Filter Results or a compact table anchor, adds Pie Chart and/or Work Item Statistics for cross-sectional breakdowns, and includes Work item Statistics when the question is about assignee, component, label, or other field distribution
- **AND** when the dashboard domain already has stable saved filters or custom field IDs, the dashboard skill SHALL prefer multi-filter fan-out and custom-field pivots over forcing a single shared filter across every gadget
- **AND** the dashboard skill SHALL keep Forge app-owned dashboards as a separate recommendation path for custom rendering, not the default answer for native Jira gadget dashboards

#### Scenario: Agent needs native time and flow gadgets

- **WHEN** an agent asks for time-based flow metrics beyond the baseline dashboard set
- **THEN** the dashboard skill SHALL recommend the bundled `default-flow-metrics.yaml` layout as the primary answer
- **AND** the skill SHALL note that the bundled flow layout uses Resolution Time, Average Time in Status, Time to First Response, and Recently Created Chart
- **AND** the skill SHALL keep Average Number of Times in Status and Voted Work items as niche follow-up options unless the dashboard question specifically needs churn or vote-driven prioritization


### Requirement: Work Item Breakdown layout

The system SHALL provide a dedicated "Work Item Breakdown" dashboard layout that focuses on distribution across owner, component, and label dimensions rather than time trends.

#### Scenario: Load the work-item-breakdown layout

- **WHEN** an operator runs `jira-skill dashboard create --name "<name>" --layout default-work-item-breakdown.yaml --filter-id <id>`
- **THEN** the CLI SHALL create a dashboard with 6 gadgets: Status Distribution, Priority Distribution, Assignee Breakdown, Component Breakdown, Label Breakdown, and Work Item Table
- **AND** the Assignee Breakdown, Component Breakdown, and Label Breakdown gadgets SHALL each use `stats-gadget` URI with `statType` set to `assignee`, `components`, and `labels` respectively
- **AND** the Work Item Table gadget SHALL use `filter-results-gadget` URI with `filterId`, column list, and `num: "20"`

#### Scenario: Validate work-item-breakdown gadget configuration

- **WHEN** an operator runs `jira-skill dashboard validate --dashboard-id <id> --filter-id <id> --layout default-work-item-breakdown.yaml`
- **THEN** validation SHALL treat the six required gadgets as `required` filter-binding contracts and SHALL fail if any gadget's `projectOrFilterId` or `filterId` does not match the expected filter
- **AND** validation SHALL match the `stats-gadget` URI pattern (`rest/gadgets/1.0/g/com.atlassian.jira.gadgets:stats-gadget/gadgets/stats-gadget.xml`) and SHALL NOT route them to the `__unrecognized__` fallback

#### Scenario: stats-gadget property persistence

- **WHEN** the workflow places a `stats-gadget` with `statType` set to any standard field (assignee, components, labels, issuetype, reporter, priority, status)
- **THEN** the workflow SHALL persist `{"projectOrFilterId": "filter-<id>", "isConfigured": "true"}` merged with the declared layout properties
- **AND** validation SHALL treat `statType` values as layout-passed properties, not validation invariants, except when the layout entry explicitly declares them as validation keys


### Requirement: Flow metrics layout

The system SHALL provide a dedicated flow-metrics layout that prioritizes the most valuable native Jira flow gadgets for resolution speed, bottlenecks, first response, and intake monitoring.

#### Scenario: Load the flow-metrics layout

- **WHEN** an operator runs `jira-skill dashboard create --name "<name>" --layout default-flow-metrics.yaml --filter-id <id>`
- **THEN** the CLI SHALL create a dashboard with 4 gadgets: Resolution Time, Average Time in Status, Time to First Response, and Recently Created Chart
- **AND** each gadget SHALL use the live Jira Cloud gadget URIs verified from the dashboard gadget directory
- **AND** each gadget SHALL persist the minimal filter-backed config `{"projectOrFilterId": "filter-<id>", "isConfigured": "true"}`

#### Scenario: Validate the flow-metrics layout

- **WHEN** an operator runs `jira-skill dashboard validate --dashboard-id <id> --filter-id <id> --layout default-flow-metrics.yaml`
- **THEN** validation SHALL treat the four gadgets as required and SHALL fail if any gadget's filter binding or `projectOrFilterId` does not match the expected filter
- **AND** the workflow SHALL recognize the configured native gadgets by URI and title instead of routing them to the unrecognized-gadget fallback

#### Scenario: Extra native gadgets stay documented but not bundled

- **WHEN** an operator asks for the most valuable next gadgets after the flow-metrics bundle
- **THEN** the workflow SHALL recommend Average Number of Times in Status and Voted Work items as niche follow-up gadgets rather than bundling them by default
- **AND** the workflow SHALL note that those gadgets are lower-priority than the flow-metrics set unless the user specifically needs churn or vote-driven prioritization

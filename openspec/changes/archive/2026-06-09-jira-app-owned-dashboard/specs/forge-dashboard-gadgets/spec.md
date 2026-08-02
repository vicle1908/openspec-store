## ADDED Requirements

### Requirement: Forge dashboard gadget module
The system SHALL expose app-owned Jira dashboard items as Forge `jira:dashboardGadget` modules with a title, description, thumbnail, and a view resource, and it SHALL support an edit resource when the gadget is configurable. The system SHALL only claim support when the Jira site exposes the Forge dashboard gadget module. The Forge manifest SHALL declare the gadget under `modules.jira:dashboardGadget` and SHALL provide `resource` plus `edit.resource` entry points for the view and edit surfaces.

#### Scenario: Gadget appears in Jira dashboard picker
- **WHEN** a Jira administrator installs the app and opens the dashboard gadget picker
- **THEN** the app-owned gadget SHALL be available to add to a dashboard
- **AND** the gadget SHALL show its configured title, description, and thumbnail

### Requirement: Dashboard module availability gate
The system SHALL fail gracefully when the Jira site does not expose Forge dashboard modules, and it SHALL present a clear unsupported or unavailable state instead of pretending the app-owned gadget can be installed.

#### Scenario: Site does not expose the gadget module
- **WHEN** an administrator opens the app on a Jira site that does not expose the Forge dashboard gadget module
- **THEN** the app SHALL not claim success or silently misconfigure a gadget
- **AND** the app SHALL show guidance that the modern app-owned dashboard path is unavailable on that site

### Requirement: Rich dashboard rendering
The system SHALL render rich dashboard content inside the app-owned gadget, including summary information and at least one visualization such as a chart, table, or KPI card. The view surface SHALL retrieve its dataset through a Forge resolver or background-script-backed data path rather than relying on the persisted config object alone.

#### Scenario: Dashboard renders visualization and summary
- **WHEN** a gadget receives data from a configured Jira saved filter
- **THEN** the gadget SHALL render both a human-readable summary and a visualization of the same data set
- **AND** the visualization SHALL be usable without leaving the dashboard page

### Requirement: Separate view and edit modes
The system SHALL support separate view and edit behavior for app-owned dashboard gadgets so configuration can be changed from within the dashboard experience, and it SHALL use `context.extension.entryPoint` from `useProductContext()` to decide whether to render view or edit behavior. The edit flow SHALL persist changes with `view.submit()`.

#### Scenario: User opens gadget edit mode
- **WHEN** a user clicks the gadget edit action
- **THEN** the app SHALL render the edit surface instead of the view surface using the Forge edit entry point
- **AND** the edit surface SHALL allow the user to change the gadget configuration without editing Jira legacy gadget prefs

### Requirement: Dashboard context contract
The system SHALL read the Forge dashboard runtime context from `context.extension.gadgetConfiguration`, `context.dashboard.id`, `context.gadget.id`, and `context.extension.entryPoint`, and it SHALL not depend on Connect-era `dashboardItem.*` parameters for the app-owned gadget flow.

#### Scenario: Gadget renders with Forge runtime context
- **WHEN** the gadget loads in view or edit mode
- **THEN** the gadget SHALL branch on `extension.entryPoint`
- **AND** the gadget SHALL restore its current configuration from `gadgetConfiguration`
- **AND** the gadget SHALL still know which dashboard it belongs to via `dashboard.id`

### Requirement: Shared dashboard data flow
The system SHALL support a `jira:dashboardBackgroundScript` for shared dashboard data, heavy precomputation, or refresh fan-out when more than one gadget needs the same underlying data. The background script SHALL communicate with gadgets using `@forge/bridge` events.

#### Scenario: Background script publishes updated data
- **WHEN** the background script computes a new dataset
- **THEN** it SHALL publish the dataset to one or more dashboard gadgets
- **AND** the gadgets SHALL update their displayed content without requiring a full page reload when the platform supports that flow

### Requirement: Permission-scoped Jira data access
The system SHALL fetch Jira data using app-scoped access that respects the active user's permissions, and it SHALL not display data the user cannot access in Jira. The implementation SHALL use Forge user-scoped Jira requests for authenticated data access.

#### Scenario: User lacks issue access
- **WHEN** the current user cannot access one of the issues in the source dataset
- **THEN** the gadget SHALL omit that issue from the rendered output or show a permission-safe fallback
- **AND** the gadget SHALL not expose the restricted issue summary, status, or other private fields

### Requirement: App-owned dashboard state
The system SHALL store gadget configuration in Forge-managed app-owned state rather than Jira legacy dashboard gadget prefs, and the dashboard experience SHALL not depend on the native built-in gadget persistence contract. The implementation SHALL treat the Forge gadget configuration object as the source of truth after submit.

#### Scenario: Gadget reloads after configuration change
- **WHEN** a user saves gadget configuration and reopens the dashboard
- **THEN** the gadget SHALL restore its state from Forge-managed gadget configuration
- **AND** the rendered output SHALL not require Jira legacy gadget prefs to remain correct


### Requirement: Saved filter source contract
The system SHALL use a Jira saved filter as the canonical input for the first release of the app-owned dashboard gadget, and it SHALL not require a ticket-intelligence bundle to render or validate the gadget. The saved filter SHALL be captured in the gadget configuration and SHALL drive the resolver input for dashboard data.

#### Scenario: Gadget is configured from a saved filter
- **WHEN** a user configures the app-owned dashboard gadget with a saved filter ID
- **THEN** the gadget SHALL fetch data from that filter and render its dashboard content
- **AND** the gadget SHALL remain functional without any ticket-intelligence bundle being present

### Requirement: First-release scope fence
The system SHALL ship one gadget family for the first release, driven by a saved filter and one visualization path. Additional gadget families, alternate source adapters, and multi-gadget federation MAY be added later, but they are out of scope for the first execution-ready release.

#### Scenario: Developer deploys first release
- **WHEN** a developer deploys the initial Forge app
- **THEN** only one dashboard gadget family SHALL be available
- **AND** the gadget SHALL still satisfy the saved-filter contract and render a summary plus one visualization

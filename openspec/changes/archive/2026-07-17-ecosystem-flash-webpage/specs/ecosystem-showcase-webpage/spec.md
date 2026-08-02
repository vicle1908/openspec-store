## ADDED Requirements

### Requirement: Single-file showcase page
The system SHALL provide a single-file HTML showcase page for the TDT ecosystem.

#### Scenario: Page loads without build tooling
- **WHEN** a user opens the page directly in a browser
- **THEN** the page SHALL render without requiring a build step or external app runtime
- **AND** the page SHALL present the ecosystem content from a single HTML entrypoint.

### Requirement: Validated ecosystem claims only
The showcase page SHALL present only claims that are grounded in current local source-of-truth documents.

#### Scenario: Feature claim is displayed
- **WHEN** the page shows a feature, command, status, or capability
- **THEN** that claim SHALL be traceable to one or more of the following sources: repo README, AGENTS.md, skill docs, OpenSpec spec/design/tasks, or validated research notes
- **AND** stale or unverified claims SHALL be excluded or labeled as archived / historical.

### Requirement: Maturity labels are explicit
The showcase page SHALL label each ecosystem item with one of `live`, `stable`, `planned`, or `archived`.

#### Scenario: Feature status is rendered
- **WHEN** a feature card or row is shown
- **THEN** it SHALL include a visible maturity label
- **AND** the label SHALL reflect the current implementation state rather than aspiration.

### Requirement: Core ecosystem sections are included
The showcase page SHALL include sections for foundation, Jira automation, reporting and analytics, GitLab review automation, browser/document support, shared tooling, and impact/ROI.

#### Scenario: User navigates the page
- **WHEN** a viewer moves through the page
- **THEN** they SHALL encounter the required ecosystem sections in a clear narrative order
- **AND** each section SHALL summarize the relevant repos, commands, or capabilities.

### Requirement: Presentation fits one viewport per slide
The presentation SHALL be slide-based and every slide SHALL fit within one viewport with no internal scrolling.

#### Scenario: Long content is shown
- **WHEN** a section contains more information than fits comfortably in one viewport
- **THEN** the content SHALL be split into additional slides rather than introducing internal scrollbars
- **AND** each slide SHALL remain fully readable at desktop and mobile sizes.

### Requirement: Presentation navigation is interactive
The page SHALL support keyboard, wheel, and touch navigation across slides.

#### Scenario: Viewer changes slides
- **WHEN** the user presses arrow keys, uses the mouse wheel, or swipes on touch devices
- **THEN** the page SHALL navigate between slides predictably
- **AND** the current slide index or progress indicator SHALL update accordingly.

### Requirement: Motion is progressive and accessible
The page SHALL use purposeful reveal animations while respecting reduced-motion preferences.

#### Scenario: Motion-sensitive user opens the page
- **WHEN** the browser reports `prefers-reduced-motion: reduce`
- **THEN** animations and transitions SHALL be minimized or disabled
- **AND** the page SHALL remain usable with a static layout.

### Requirement: Responsive layouts are supported
The page SHALL remain legible and structurally correct on desktop, tablet, and phone widths.

#### Scenario: Mobile viewport is used
- **WHEN** the page is opened on a narrow viewport
- **THEN** the layout SHALL reflow without overflow clipping
- **AND** typography and spacing SHALL remain readable.

### Requirement: Webpage content reflects ecosystem feature taxonomy
The page SHALL organize ecosystem content into a consistent feature taxonomy.

#### Scenario: Feature taxonomy is rendered
- **WHEN** the viewer inspects the page
- **THEN** the ecosystem SHALL be grouped into at least the following buckets: foundation, automation, reporting, review, tooling, status, and impact
- **AND** each bucket SHALL use concise feature cards or tables instead of long bullet walls.

### Requirement: Spec/code/docs consistency is validated
The change SHALL define a consistency check workflow that verifies spec, code, docs, and skills stay aligned.

#### Scenario: Alignment is reviewed
- **WHEN** the page or supporting docs are updated
- **THEN** the maintainer SHALL verify that the feature list matches current repo READMEs, skill docs, and OpenSpec reports
- **AND** any mismatched or stale claim SHALL be corrected before release.

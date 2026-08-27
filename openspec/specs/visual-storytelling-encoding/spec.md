# visual-storytelling-encoding Specification

## Purpose
TBD - created by archiving change enhance-ntu-keynote-visual-storytelling. Update Purpose after archive.

## Requirements

### Requirement: Meaningful visuals SHALL be inline SVG with accessible semantics

Every chart, diagram, or symbolic visual that carries audience-required meaning SHALL be implemented as inline SVG with `role="img"`, a unique `<title>`, a unique `<desc>`, and `aria-labelledby` referencing both IDs. The title and description SHALL be in Vietnamese and SHALL preserve units, populations, qualifiers, and source identity.

#### Scenario: Chart SVG is inspected for accessibility

- **WHEN** any meaningful SVG element is examined in the DOM
- **THEN** it SHALL have `role="img"`
- **AND** it SHALL contain exactly one `<title>` child with a unique ID
- **AND** it SHALL contain exactly one `<desc>` child with a unique ID
- **AND** `aria-labelledby` SHALL reference both IDs
- **AND** the title and description text SHALL be Vietnamese

#### Scenario: Decorative visual has no required meaning

- **WHEN** a visual is classified as decorative
- **THEN** it SHALL carry `aria-hidden="true"` or `role="presentation"`
- **AND** removing it SHALL NOT remove any audience-required information

### Requirement: Data visuals SHALL preserve factual qualifiers and population separation

Every data visualization SHALL display its registered qualifier, population label, unit, and forecast/observed status as visible text within or adjacent to the visual. The 95% organization claim and 5% integrated-pilot claim SHALL remain in separate visual groups with no shared-denominator geometry.

#### Scenario: 95/5 separation is enforced

- **WHEN** slide 7's visual encoding is inspected
- **THEN** the 95% bar and 5% bar SHALL be in separate visual groups
- **AND** no stacked bar, pie, donut, track, connector, or proportional geometry SHALL imply a common denominator
- **AND** each bar SHALL label its distinct population ("tổ chức" vs "thử nghiệm AI tích hợp")
- **AND** the USD 30–40B investment figure SHALL be in a separate visual band

#### Scenario: Forecast is not encoded as observation

- **WHEN** any visual encodes a forecast or modeled estimate
- **THEN** the visual SHALL include a visible qualifier label (e.g., "dự báo", "ước tính mô hình hóa")
- **AND** the visual SHALL NOT use encoding conventions reserved for observed measurements (e.g., solid fill without qualifier, axis labeled as actual)

### Requirement: Visuals SHALL meet legibility and safe-area constraints

Every meaningful visual SHALL be legible at 1366×768 viewport and within the 1280×720 authored stage safe area. SVG text elements SHALL compute to at least 18px at the authored stage before transform. Any visual that fails this constraint SHALL be dropped from scope rather than shrunk.

#### Scenario: Visual passes legibility check

- **WHEN** a slide visual is rendered at 1366×768 viewport
- **THEN** all text within the SVG SHALL compute to ≥ 18px at the 1280×720 authored stage
- **AND** the visual SHALL NOT overflow the slide safe area
- **AND** the visual SHALL NOT overlap required text content

#### Scenario: Visual fails legibility and is dropped

- **WHEN** a proposed visual cannot meet the 18px floor or safe-area bound
- **THEN** it SHALL be excluded from the implementation
- **AND** the exclusion SHALL be recorded in the implementation evidence
- **AND** the slide SHALL retain its existing text-based encoding

### Requirement: All visuals SHALL be offline-safe with no external dependencies

No visual SHALL require network access, CDN resources, JavaScript libraries, Canvas elements, external font files, or stock photography. All visuals SHALL render correctly from a local `file://` URL with no network connectivity.

#### Scenario: Offline rendering is verified

- **WHEN** the presentation is opened via `file://` with network disabled
- **THEN** all visuals SHALL render completely
- **AND** no console errors SHALL reference network requests
- **AND** no `<canvas>`, `<script src>`, or external `<link>` elements SHALL be present

### Requirement: Visual changes SHALL trigger Tier 1 evidence refresh

Any change to public-package bytes for visual enhancement SHALL invalidate the current package digest and require full Tier 1 evidence regeneration: PDF, browser qualification, accessibility, copied-folder observation, checksums, manifest, and a new Drive version folder.

#### Scenario: New candidate produces new digest

- **WHEN** visual enhancements are committed to `index.html`
- **THEN** the seven-file package digest SHALL change
- **AND** a new Drive version folder SHALL be created (not overwriting the prior version)
- **AND** all evidence artifacts SHALL reference the new candidate commit and digest

#### Scenario: Predecessor records are preserved

- **WHEN** the new candidate is published
- **THEN** predecessor acceptance artifacts SHALL NOT be mutated
- **AND** the new acceptance bundle SHALL live under this change's own directory
- **AND** predecessor open gates SHALL remain open and unaffected

### Requirement: Visual budget SHALL limit scope to legible enhancements

A maximum of 8 slides SHALL receive visual enhancement in a single pass. The implementation SHALL record which visuals passed legibility and which were dropped. No visual SHALL be added if it overcrowds the slide or reduces comprehension of the dominant message.

#### Scenario: Visual budget is enforced

- **WHEN** the implementation is complete
- **THEN** at most 8 slides SHALL have new meaningful visuals
- **AND** each enhanced slide SHALL retain its dominant narrative message as the primary reading element
- **AND** the implementation evidence SHALL list passed and dropped visuals with reasons

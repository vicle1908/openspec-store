## Purpose

This delta spec defines requirements for embedding the Nanyang Business School (NBS) logo alongside the NTU corporate logo in the keynote presentation brand lockup.

## ADDED Requirements

### Requirement: NBS logo asset SHALL be an officially sourced file with recorded provenance

The NBS logo asset SHALL be sourced from an authoritative origin and its provenance SHALL be recorded with source URL, retrieval date, file format, dimensions, alpha/transparency, and SHA-256 hash. The provenance classification SHALL be one of `official-page-asset`, `brand-portal-download`, or `user-provided`. If no authoritative NBS logo source can be verified, the presentation SHALL remain NTU-only with no NBS mark and the change SHALL NOT proceed to implementation.

#### Scenario: NBS logo is sourced from an authoritative origin

- **WHEN** the NBS logo file is added to `assets/`
- **THEN** the source URL, retrieval date, file format, dimensions, alpha/transparency, and SHA-256 hash SHALL be recorded in `evidence/source-inspection.json` or a dedicated asset-provenance record
- **AND** the provenance classification SHALL be one of `official-page-asset`, `brand-portal-download`, or `user-provided` (not `unknown` or `third-party-repo`)

#### Scenario: NBS logo fails provenance review

- **WHEN** no authoritative NBS logo source can be verified
- **THEN** the presentation SHALL remain in NTU-only branding (no NBS mark)
- **AND** the change SHALL NOT proceed to implementation

### Requirement: Brand lockup SHALL contain exactly one NTU logo and one NBS logo

The `.brand-layer` container SHALL contain exactly two `<img>` elements with `data-brand-asset` values of `ntu-logo` and `nbs-logo`, separated by a single divider element. The container SHALL carry `role="group"` and a Vietnamese `aria-label` identifying both marks. No additional `<img>` elements SHALL exist inside `.brand-layer`.

#### Scenario: Dual-lockup HTML structure

- **WHEN** the `.brand-layer` container is inspected
- **THEN** it SHALL contain exactly two `<img>` elements with `data-brand-asset` values of `ntu-logo` and `nbs-logo`
- **AND** exactly one `.brand-divider` element (or equivalent separator) between them
- **AND** the container SHALL carry `role="group"` and Vietnamese `aria-label` identifying both marks

#### Scenario: No hidden or duplicate logos

- **WHEN** the full HTML is searched for `data-brand-asset`
- **THEN** there SHALL be exactly two matches: one `ntu-logo` and one `nbs-logo`
- **AND** no additional `<img>` elements SHALL exist inside `.brand-layer`

### Requirement: Both logos SHALL be local assets with no external dependencies

Both logo `src` attributes SHALL reference local files under `assets/` with no protocol prefixes. The brand lockup SHALL produce zero HTTP/HTTPS network requests when loaded via `file://`.

#### Scenario: Offline launch

- **WHEN** the keynote is opened via `file://` with no network
- **THEN** both logos SHALL render from local `assets/` paths
- **AND** `src` attributes SHALL NOT contain `http://`, `https://`, or protocol-relative URLs

#### Scenario: Zero outbound requests from brand lockup

- **WHEN** Playwright captures network requests during slide 1 load
- **THEN** the brand lockup SHALL produce zero HTTP/HTTPS requests

### Requirement: Lockup SHALL fit within the authored safe area at all required viewports

The brand lockup bounding box SHALL be entirely within the safe area at every required viewport. The container bottom SHALL NOT exceed y=144px at 1280×720 to avoid overlapping slide titles. All four required viewport checks (1920×1080, 1440×900, 1366×768, 1024×768) SHALL report `overflow: false`.

#### Scenario: Safe-area bounds at 1280×720

- **WHEN** the lockup is measured at 1280×720 (authored stage)
- **THEN** the container bounding box SHALL be entirely within x∈[64, 1216] and y∈[36, 684]
- **AND** the container bottom SHALL NOT exceed y=144 (to avoid overlapping any slide title)

#### Scenario: Safe-area bounds at 1024×768

- **WHEN** the lockup is measured at 1024×768 (smallest required viewport)
- **THEN** the container bounding box SHALL be entirely within the safe area
- **AND** no overflow SHALL occur

#### Scenario: Overflow at any viewport

- **WHEN** Chrome viewport checks at 1920×1080, 1440×900, 1366×768, and 1024×768 all report `overflow: false` for `.brand-layer`
- **THEN** the geometry check SHALL pass

### Requirement: Lockup SHALL NOT alter slide content, timing, or navigation

The addition of the NBS logo SHALL NOT change any slide text, slide order, per-slide timing values, notes content, navigation routes, or SVG visuals. All existing slide-level invariants SHALL be preserved.

#### Scenario: Slide count and route invariants

- **WHEN** the presentation is tested
- **THEN** there SHALL be exactly 17 slides in the same order
- **AND** full route SHALL be slides 1–17
- **AND** short route SHALL skip only slides 4 and 8
- **AND** per-slide timing SHALL match the existing `data-full-seconds` and `data-short-seconds` values

#### Scenario: Slide 1 content preserved

- **WHEN** slide 1 visible text is compared before and after the change
- **THEN** all existing Vietnamese text, title, eyebrow, and layout SHALL be unchanged

### Requirement: NTU logo SHALL retain its current visual prominence

The NTU logo rendered width SHALL be greater than or equal to the NBS logo rendered width. The NTU logo SHALL remain leftmost in the lockup arrangement.

#### Scenario: NTU logo is not smaller than NBS logo

- **WHEN** both logos are rendered in the lockup
- **THEN** the NTU logo rendered width SHALL be ≥ the NBS logo rendered width
- **AND** the NTU logo SHALL remain leftmost in the lockup

### Requirement: Lockup SHALL render correctly in print / PDF fallback

The PDF fallback SHALL show both NTU and NBS logos in the brand lockup on page 1. The lockup SHALL NOT be clipped or overlap any slide content in the PDF rendering.

#### Scenario: PDF contains the lockup

- **WHEN** `keynote-fallback.pdf` is generated and inspected
- **THEN** both NTU and NBS logos SHALL be visible in the page-1 rendering
- **AND** the lockup SHALL NOT be clipped or overlapping any slide content

### Requirement: Package evidence SHALL be updated to reflect the new asset

The seven-file package SHALL become an eight-file package with the NBS asset added. The package digest SHALL differ from the predecessor (`8a96ed4f...`). All evidence surfaces SHALL be rebound to the new candidate.

#### Scenario: Package digest changes

- **WHEN** the public package is recomputed
- **THEN** the digest SHALL differ from the predecessor (`8a96ed4f...`)
- **AND** `checksums.sha256` SHALL include the new NBS asset entry
- **AND** `evidence/assets.json` SHALL record the NBS file with format, dimensions, and SHA-256

#### Scenario: Manifest is rebound

- **WHEN** `evidence/release-manifest.json` is updated
- **THEN** `public_venue_package.files` SHALL include the NBS asset path
- **AND** `public_venue_package.file_sha256` SHALL include the NBS hash
- **AND** `status` SHALL remain `blocked-automated`
- **AND** human gates SHALL remain open

### Requirement: Existing claim copy, qualifiers, and notes SHALL NOT change

All Vietnamese audience copy, notes copy, qualifiers, and source references from `evidence/sources.json` SHALL remain unchanged. The qualifier-fidelity check from `scripts/verify_static.py` SHALL continue to pass.

#### Scenario: Vietnamese copy preservation

- **WHEN** all claim `audience_copy_vi` values from `evidence/sources.json` are checked against visible slide text
- **THEN** every claim SHALL still match its slide
- **AND** all `notes_copy_vi` values SHALL still match the notes contract

#### Scenario: Qualifier fidelity

- **WHEN** `scripts/verify_static.py` qualifier-fidelity check runs
- **THEN** it SHALL still pass (all required qualifier tokens present in their slides)

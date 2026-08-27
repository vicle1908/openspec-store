# Visual Attention Enhancement

## ADDED Requirements

### Requirement: Slide 3 SHALL encode the modeled potential as a single qualified magnitude visual

Slide 3 SHALL display the $15.7T modeled estimate as a single magnitude visual with a visible modeled-estimate qualifier on the visual itself. The visual SHALL NOT compare the modeled estimate against realized or observed values, and SHALL NOT introduce new animation.

#### Scenario: Magnitude visual is inspected

- **WHEN** the slide-3 visual is examined in the DOM
- **THEN** it SHALL be a single inline SVG with `data-visual-id="visual-s3-magnitude"`
- **AND** it SHALL contain exactly one bar or magnitude shape labeled with the value "15,7 nghìn tỷ USD"
- **AND** it SHALL contain visible qualifier text stating this is a modeled estimate for 2030 ("ước tính mô hình hóa")
- **AND** it SHALL NOT contain a second comparison bar, realized-value axis, or observed-data geometry
- **AND** the existing `pwc-counter` animation final value SHALL remain "15,7 nghìn tỷ USD"

#### Scenario: Magnitude visual fails legibility and is dropped

- **WHEN** the slide-3 visual cannot meet the 18px authored-stage text floor or the safe-area bound at 1366×768
- **THEN** the SVG SHALL be excluded from the implementation
- **AND** the exclusion SHALL be recorded in this change's acceptance evidence
- **AND** the slide SHALL retain its existing text-based encoding and counter animation

### Requirement: Slide 5 SHALL present ITVIEC-2025 survey findings as three base-labeled stat blocks

Slide 5 SHALL present the three ITVIEC-2025 survey figures — 73% adoption breadth (base: surveyed companies), 13.8% scaled/fully adoption stage (a stage within the 73% adopter breakdown), and 5.4% very-high-trust-with-minimal-human-oversight (base: companies that have adopted AI) — as three separate, equal-weight stat blocks, each carrying a visible base/denominator label. The figures SHALL NOT be encoded as a funnel, stacked bar, shared track, or arrow-connected progression implying a sequential filter, and no geometry SHALL imply one common denominator across all three figures. The real subset relationships (13.8% within the 73% breakdown; 5.4% based on adopters) SHALL be stated in the base labels, not denied.

#### Scenario: Three stat blocks are inspected for geometry and base labels

- **WHEN** the slide-5 survey encoding is examined in the DOM
- **THEN** the three figures SHALL appear in three separate equal-weight containers
- **AND** the 73% block SHALL carry a base label identifying surveyed companies
- **AND** the 13.8% block SHALL carry a base label identifying it as a stage within the 73% adopter breakdown
- **AND** the 5.4% block SHALL carry a base label identifying companies that have adopted AI
- **AND** no SVG path, connector, shared axis, stacked geometry, nested shape, or arrow SHALL link the three figures as a sequential filter
- **AND** card placement, sizing, and color SHALL NOT imply a single funnel or progression
- **AND** a visible methodology note SHALL state the two independent Q2-2025 surveys (IT professionals; HR leaders and business decision-makers) per the report methodology page

#### Scenario: Survey wording and respondent-count attribution are preserved

- **WHEN** the slide-5 audience copy and notes are inspected
- **THEN** the figures SHALL be framed as survey findings ("khảo sát")
- **AND** no copy SHALL present the figures as audited company-level measurements
- **AND** the combined 846-respondent count, if present at all, SHALL be attributed to the publisher blog and SHALL NOT be presented as the denominator of any of the three figures
- **AND** the notes contract for slide 5 SHALL include a source reminder covering the denominator caution

#### Scenario: Existing slide-5 claims are preserved

- **WHEN** the revised slide 5 is compared with the baseline
- **THEN** the NQ57-2024 and GOOGLE-AP-2024 card copy SHALL remain verbatim
- **AND** the slide's existing mandatory anchors SHALL remain present
- **AND** the source line SHALL additionally reference [ITVIEC-2025]

#### Scenario: Slide-5 encoding overflows and falls back to text

- **WHEN** the three-block strip cannot fit at ≥18px within the safe area at 1366×768
- **THEN** the implementation SHALL fall back to text-only encoding with three separate sentences and base labels
- **AND** the fallback SHALL be an accepted implementation path, not a defect
- **AND** the claims SHALL remain registered in the source register regardless of visual path
- **AND** the chosen path SHALL be recorded in this change's acceptance evidence

### Requirement: The source register SHALL carry ITVIEC-2025 as a primary source with inspected PDF artifact identity

The evidence source register SHALL add source `ITVIEC-2025` using the existing `primary` source_type value (no new enum value is introduced), with the publisher blog URL as access URL and the official mini-report PDF recorded as the inspected primary artifact with its SHA-256, page count, and creation date. The register SHALL record the two-survey Q2-2025 methodology stated in the PDF and SHALL note that the combined 846-respondent count appears only on the publisher blog.

#### Scenario: Source record is inspected

- **WHEN** `evidence/sources.json` is examined
- **THEN** it SHALL contain source id `ITVIEC-2025` with source_type `primary`
- **AND** the record SHALL reference the official mini-report PDF with SHA-256 `552a2d5e39b6896ed542f59bf12f76499f3458b9b8a352cc7b087131d0f17802`, 54 pages, created 2025-08-21
- **AND** the record SHALL state the two independent Q2-2025 surveys methodology from the PDF
- **AND** the record SHALL note that the combined 846-respondent count is attributed to the publisher blog only
- **AND** three claims SHALL reference this source with distinct base labels: adoption breadth 73% (surveyed companies), scaled/fully stage 13.8% (within the 73% adopter breakdown), very-high-trust-with-minimal-human-oversight 5.4% (companies that have adopted AI)

#### Scenario: Canonical ID consistency is verified

- **WHEN** all change artifacts and the implementation are searched for the source identifier
- **THEN** only `ITVIEC-2025` SHALL appear (no variants such as `ITVIC-2025`)
- **AND** `evidence/slide-contract.json` slide-5 `source_ids` SHALL include `ITVIEC-2025`

### Requirement: Slide 6 SHALL render a visible waterline separating tip from submerged mass

Slide 6 SHALL render the iceberg metaphor with a visible waterline: the visible-tip content above the waterline and the submerged value-creation content below it, with the submerged region visually dominant. All existing slide-6 copy SHALL remain unchanged in DOM text and reading order.

#### Scenario: Waterline layout is inspected

- **WHEN** slide 6 is rendered in full and short mode
- **THEN** a visible waterline divider SHALL separate tip content from submerged content
- **AND** the submerged region SHALL occupy visibly greater area than the tip
- **AND** the tip content and the three submerged layer items SHALL appear in the existing reading order with unchanged text
- **AND** any decorative waterline shape SVG SHALL carry `aria-hidden="true"`

#### Scenario: Waterline layout fails and falls back

- **WHEN** the vertical waterline layout cannot meet the safe-area bound at 1366×768
- **THEN** the implementation SHALL retain the existing two-column grid and add only a decorative waterline motif
- **AND** the chosen path SHALL be recorded in this change's acceptance evidence

### Requirement: New visuals SHALL satisfy the inherited accessibility, legibility, and offline contracts

All new meaningful visuals SHALL comply with the main `visual-storytelling-encoding` requirements without restatement: inline SVG with `role="img"`, unique Vietnamese `<title>` and `<desc>`, `aria-labelledby` referencing both, ≥18px authored-stage text, safe-area bounds, and offline safety. No new binary assets, external URLs, fonts, scripts, or network dependencies SHALL be introduced.

#### Scenario: New meaningful SVGs are inspected for accessibility

- **WHEN** any new meaningful SVG is examined in the DOM
- **THEN** it SHALL have `role="img"`
- **AND** it SHALL contain exactly one `<title>` child with a unique ID and Vietnamese text
- **AND** it SHALL contain exactly one `<desc>` child with a unique ID and Vietnamese text
- **AND** `aria-labelledby` SHALL reference both IDs

#### Scenario: Public package boundary is preserved

- **WHEN** the revised candidate is built against `evidence/venue-package-allowlist.json`
- **THEN** the package SHALL contain exactly the existing seven public files
- **AND** `index.html` SHALL contain no new external URL references
- **AND** no new binary asset SHALL be added under `assets/`
- **AND** research artifacts (including the inspected ITviec PDF) SHALL NOT enter the package, `assets/`, or the package digest

### Requirement: Deck contract invariants SHALL remain unchanged

The enhancement SHALL NOT change the slide count, slide order, route definitions, per-slide timing values, fragment routing, or slide-7 geometry. Notes-contract updates SHALL be limited to slides 3, 5, and 6.

#### Scenario: Contract invariants are verified against baseline

- **WHEN** the revised `index.html` is compared with the baseline candidate
- **THEN** exactly 17 slide IDs in the same order SHALL remain
- **AND** the full and short route arrays and all `data-full-seconds`/`data-short-seconds` values SHALL remain unchanged
- **AND** the slide-7 visual groups, 95%/5% separation geometry, and investment band SHALL be byte-equivalent in structure
- **AND** notes-contract entries for slides other than 3, 5, and 6 SHALL remain unchanged

### Requirement: Tier 1 evidence SHALL be refreshed against the new candidate with human gates remaining open

Because `index.html` and `keynote-fallback.pdf` are public package files, the implementation SHALL produce a new immutable candidate identity and SHALL refresh all affected evidence. The release manifest SHALL remain blocked on the open human gates and SHALL NOT be marked approved by this change.

#### Scenario: New candidate evidence is produced

- **WHEN** the implementation is integrated
- **THEN** the seven-file package digest SHALL differ from `795d4f53c3172f382f0ec4a9965cdf88e75dcffaeca29fcb802bb6c11de53254`
- **AND** per-file SHA-256 values and `checksums.sha256` SHALL be recomputed and pass verification
- **AND** `keynote-fallback.pdf` SHALL be regenerated from the new candidate with 17 pages
- **AND** browser qualification, screenshots, and copied-folder evidence SHALL identify the new candidate commit

#### Scenario: Drive publication creates a new version without touching the prior one

- **WHEN** the new package is synced to Drive
- **THEN** a new version folder SHALL be created whose path differs from `a7f24085935a-795d4f53c317`
- **AND** read-back SHALL confirm 7 files with matching sizes
- **AND** the prior version folder SHALL remain intact

#### Scenario: Human gates remain open

- **WHEN** the release manifest is inspected after integration
- **THEN** the Vietnamese editorial review gate SHALL remain open for the new slide-5 copy
- **AND** the Safari re-qualification, physical venue rehearsal, and release decision gates SHALL remain open
- **AND** no tag, remote, or archive action SHALL have been taken on either repository

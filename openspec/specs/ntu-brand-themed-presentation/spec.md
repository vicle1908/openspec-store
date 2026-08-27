# ntu-brand-themed-presentation Specification

## Purpose
Define a conservative, evidence-bound visual enhancement that makes the NTU keynote visibly compatible with the researched NTU blue/red/golden-yellow identity family while preserving the existing offline presentation contract, readability, neutral copy, and human approval boundary.

## Requirements

### Requirement: NTU brand-family palette roles SHALL be explicit and navy-dominant

The presentation SHALL define explicit CSS color roles for a navy-dominant stage, structural crimson, readable light crimson, golden yellow, and white. The implementation SHALL identify reference values as design references rather than claiming official NTU HEX or Pantone compliance when the official general presentation guide is unavailable.

#### Scenario: Palette roles are inspectable in the committed HTML

- **WHEN** the committed `index.html` CSS tokens are inspected
- **THEN** the named roles SHALL include stage navy, structural crimson, readable crimson, gold, and white
- **AND** the stage background SHALL remain navy-dominant
- **AND** the implementation SHALL contain no claim that the reference HEX values are official NTU tokens

#### Scenario: Official logo asset remains unchanged

- **WHEN** the implementation diff is reviewed
- **THEN** `assets/ntu-logo.png` SHALL be byte-identical to the prior candidate
- **AND** no new crest, logo, SVG, or third-party asset SHALL be added

### Requirement: Brand accents SHALL be restrained and non-semantic

The presentation SHALL use crimson and gold for restrained identity decoration and existing attention points without changing slide content, DOM reading order, route behavior, or semantic meaning.

#### Scenario: Slides receive a non-interactive identity rule

- **WHEN** a slide is rendered in full or short mode
- **THEN** a 4px solid crimson identity rule with a thin gold bottom edge SHALL appear at the top edge
- **AND** the rule SHALL not consume authored safe-area space, alter content flow, or create a focusable element

#### Scenario: Eyebrow and key metrics use the researched accent family

- **WHEN** visible eyebrow labels and existing metric attention points are rendered
- **THEN** eyebrow text SHALL use the readable crimson role
- **AND** existing metric attention points SHALL use the gold role sparingly
- **AND** ordinary body labels SHALL remain white/readable rather than becoming decorative color noise

#### Scenario: Content and route contracts remain unchanged

- **WHEN** the revised HTML is compared with the prior candidate at the semantic/content level
- **THEN** exactly 17 slide IDs, slide order, Vietnamese copy, notes contract, full/short timing, fragment routing, and local-storage behavior SHALL remain unchanged

### Requirement: Accent contrast SHALL satisfy the presentation accessibility contract

The implementation SHALL use only contrast-safe text roles on the dark stage: normal text SHALL meet at least 4.5:1, large text SHALL meet at least 3:1, and structural crimson SHALL NOT be used as normal-size body text when its contrast is insufficient.

#### Scenario: Text and focus colors meet contrast thresholds

- **WHEN** contrast is calculated from the committed role values against `--ntu-blue-stage`
- **THEN** readable crimson, gold, and white SHALL meet the applicable WCAG thresholds
- **AND** the structural crimson role SHALL be classified as decoration-only if it fails normal-text contrast

#### Scenario: Reduced motion and print preserve the final visual state

- **WHEN** reduced-motion or print-final CSS states are applied
- **THEN** the red/gold decorations SHALL remain static and visible where appropriate
- **AND** no new animation SHALL be introduced

### Requirement: Public-package evidence SHALL be refreshed after theme changes

Because `index.html` is an allowlisted public package file, any implementation of this change SHALL produce a new immutable candidate identity and SHALL refresh all affected PDF, screenshot, evidence, checksum, and central acceptance references.

#### Scenario: Changed public bytes invalidate prior candidate evidence

- **WHEN** the revised `index.html` differs from the prior candidate
- **THEN** the prior public-package digest SHALL NOT be presented as current
- **AND** the revised candidate SHALL have a recomputed seven-file digest and per-file hashes
- **AND** the central acceptance artifact SHALL bind to the revised commit

#### Scenario: Evidence is refreshed against the revised candidate

- **WHEN** PDF or browser evidence is regenerated for the changed public bytes
- **THEN** the regenerated evidence SHALL identify the revised candidate commit and environment
- **AND** stale prior screenshots SHALL NOT be relabeled as fresh evidence

#### Scenario: Evidence generation is honestly blocked

- **WHEN** a required renderer or browser is unavailable
- **THEN** the exact blocker SHALL be recorded in the acceptance artifact
- **AND** stale prior screenshots SHALL NOT be relabeled as fresh evidence

### Requirement: Brand alignment SHALL preserve offline and public-private boundaries

The enhancement SHALL remain a single offline `file://` presentation using only the existing seven public files and SHALL NOT introduce network, external font, private-evidence, or local-planning dependencies.

#### Scenario: Public package remains exactly seven files

- **WHEN** the allowlisted venue package is built
- **THEN** it SHALL contain exactly the existing seven public files
- **AND** no `evidence/`, `tests/`, `scripts/`, `openspec/`, `.git*`, or worktree data SHALL be copied

#### Scenario: Offline launch remains self-contained

- **WHEN** `index.html` is opened from `file://` without network access
- **THEN** the revised colors and decorations SHALL render using local assets only
- **AND** all existing navigation, notes, fullscreen, reduced-motion, and PDF fallback behavior SHALL remain available

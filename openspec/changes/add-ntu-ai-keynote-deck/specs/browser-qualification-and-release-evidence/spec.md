## Purpose

Define browser, computed-style, PDF, package-isolation, rehearsal, evidence-freshness, and release acceptance required to prove one exact keynote candidate without central mutation of the external implementation root.

## ADDED Requirements

### Requirement: Safari and Chrome SHALL qualify the same exact candidate

Current installed Safari and Chrome SHALL each open the same hash-bound `file://` candidate and qualify launch, 17-slide exposure, keyboard and pointer navigation, route boundaries, full and short modes, fragment reload and invalid state, notes, local assets, font fallback, both attention animations, reduced motion, qualified viewports, fullscreen behavior where available, and print behavior.

#### Scenario: Browser matrices pass
- **WHEN** Safari and Chrome evidence is collected for one candidate
- **THEN** both records SHALL identify browser and OS versions, timestamp, evidence-base commit, tested public hashes, requirement IDs, results, and referenced artifacts with no unresolved failure

#### Scenario: Browser evidence targets different bytes
- **WHEN** Safari and Chrome records name different `index.html` or public-package hashes
- **THEN** the evidence set MUST fail release acceptance even if each browser passed independently

### Requirement: Browser evidence SHALL own computed-style acceptance

Facts that depend on the browser cascade or rendered state—including computed font size, effective foreground and background colors, display, visibility, opacity, transforms, focus outline, active/inactive exposure, overflow, clipping, reduced-motion state, and print final state—SHALL be proven by browser-derived computed-style or rendered-layout evidence. Static source inspection MAY prove declarations and structure, but MUST NOT substitute for computed-style acceptance.

#### Scenario: Scoped 18px floor is verified
- **WHEN** required audience text and meaningful visual labels are checked for the 18px floor
- **THEN** both Safari and Chrome evidence SHALL enumerate each included element, capture its computed font size at the authored 1280×720 stage before the stage transform, and classify excluded auxiliary text separately

#### Scenario: Contrast is verified
- **WHEN** a contrast result is accepted
- **THEN** the foreground and effective background inputs SHALL come from the rendered browser state rather than from an unverified source-code color token alone

#### Scenario: Static CSS appears compliant but computed style differs
- **WHEN** cascade, inheritance, transform state, media query, or runtime class changes the rendered value
- **THEN** the computed browser result SHALL control acceptance and the static declaration MUST NOT override it

### Requirement: Viewport and interaction evidence SHALL expose observable behavior

Browser qualification SHALL retain representative screenshots and machine-readable results for 1920×1080, 1440×900, 1366×768, and 1024×768, plus scripted or directly observed results for route sequences, single-step repeat protection, notes interaction suppression, fragment recovery, storage denial, animation entry and revisit, and reduced motion.

#### Scenario: Qualified viewport evidence is inspected
- **WHEN** a viewport record and screenshot are reviewed
- **THEN** they SHALL show the complete centered stage, safe-area containment, intended dominant visual, required text, and absence of clipping or overlap for the same candidate hash

#### Scenario: Interaction result lacks state evidence
- **WHEN** a navigation or recovery check reports only a generic pass without initial state, action, and resulting state
- **THEN** that result MUST NOT satisfy the corresponding acceptance scenario

### Requirement: PDF fallback SHALL be generated and verified from the accepted candidate

The fallback PDF SHALL contain exactly 17 pages in slide order, preserve dark backgrounds, Vietnamese glyphs, accessible reading order, and complete final animation values, and exclude notes and controls. Its evidence SHALL bind the PDF hash to the exact `index.html`, source and approval selection, and evidence-base commit used for generation.

#### Scenario: PDF evidence matches the candidate
- **WHEN** the PDF page count, representative pages, reading order, and bound input hashes are verified
- **THEN** the PDF SHALL be accepted as the 30-second venue fallback for that candidate

#### Scenario: A bound PDF input changes
- **WHEN** selected public content or another declared PDF input no longer matches the generation record
- **THEN** the PDF and its dependent evidence MUST be regenerated before release

### Requirement: The public venue package SHALL contain exactly the allowlisted files

The released venue package SHALL contain only `index.html`, `README.md`, `keynote-fallback.pdf`, `assets/ntu-logo.png`, and `assets/fonts/be-vietnam-pro-{400,600,800}.woff2`. It MUST NOT contain OpenSpec artifacts, source or approval records, evidence, tests, scripts, screenshots, licenses, Git or worktree metadata, or unapproved company proposal text.

#### Scenario: Venue package is assembled
- **WHEN** the release package inventory and checksums are compared with the allowlist
- **THEN** exactly seven files SHALL be present and every checksum SHALL match the release manifest

#### Scenario: Private file is included
- **WHEN** a non-allowlisted planning, evidence, source, approval, license, script, test, or repository file appears in the public package
- **THEN** release acceptance MUST fail

### Requirement: Copied-folder and actual venue rehearsals SHALL gate release

A copy of the exact allowlisted package SHALL be rehearsed from a path containing spaces and Vietnamese characters with network access unavailable to the browser context. The same package digest SHALL later be rehearsed on the actual presenting laptop with projector or external display and real clicker, covering fullscreen, navigation, notes policy, reload recovery, full delivery, exact short route, display and sleep safeguards, and PDF fallback within 30 seconds.

#### Scenario: Copied-folder rehearsal passes
- **WHEN** the hash-bound package is launched from the alternate offline path
- **THEN** all 17 slides, both routes, local assets, font fallback, notes, reset, reload, and PDF opening SHALL pass without a required network request or private-file disclosure

#### Scenario: Venue rehearsal is missing or targets another digest
- **WHEN** no actual hardware rehearsal exists for the release package digest
- **THEN** the manifest MUST remain blocked and MUST NOT say `released`

### Requirement: Release evidence SHALL be complete, fresh, and traceable

The private evidence set SHALL record requirement IDs, environments, timestamps, tested hashes, pass or fail results, referenced screenshots or reports, approval-or-neutral selection, evidence-base commit, non-self checksums, public package digest, and intended annotated tag. Any applicable invalidation event MUST visibly mark affected evidence stale until refreshed.

#### Scenario: Final release gate is evaluated
- **WHEN** central acceptance reviews the release evidence set
- **THEN** every required contract SHALL have current hash-bound evidence, the approval-or-neutral gate SHALL be resolved, the venue rehearsal SHALL pass, and the manifest SHALL use the accurate release status

#### Scenario: Evidence is stale, missing, or internally inconsistent
- **WHEN** a required record has mismatched hashes, an expired dependency, an unresolved gate, or a result for another candidate
- **THEN** release acceptance MUST remain incomplete and SHALL identify the failing evidence relationship

### Requirement: Release evidence retention SHALL apply Tier 1 and Tier 2 dependency rules

Tier 1 SHALL apply to any public-package byte, selected audience or notes wording, visual meaning, runtime behavior, or PDF-input change and SHALL require fresh browser, accessibility, viewport, screenshot, PDF, package-checksum, manifest, and copied-folder evidence for the new candidate. Tier 2 SHALL apply only when every public hash and the selected meaning remain identical and MAY retain rendering or interaction evidence only when recorded dependency hashes still match; dependent private traceability, approval, freshness, manifest, and checksum assertions MUST be refreshed.

#### Scenario: Tier 1 evidence is reused
- **WHEN** a Tier 1 change occurs and content-dependent evidence still identifies the previous candidate
- **THEN** that evidence MUST remain stale and MUST NOT satisfy release acceptance

#### Scenario: Tier 2 evidence is retained
- **WHEN** a private-record-only change leaves every public hash and selected meaning identical
- **THEN** retained rendering or interaction evidence SHALL identify matching public hashes, while every affected private dependency assertion SHALL be refreshed before acceptance

### Requirement: Central acceptance SHALL be read-only toward external implementation evidence

Central tasks SHALL receive external implementation and evidence as immutable or hash-verifiable inputs, evaluate them against central requirement IDs, and record only central acceptance state inside the central allowed edit root. Central tasks MUST NOT modify, regenerate, stage, commit, tag, or delete any file in the external implementation repository and MUST NOT invoke or depend on any local OpenSpec lifecycle. External OpenSpec artifacts, if supplied, are read-only migration or evidence inputs and have no independent acceptance authority.

#### Scenario: External evidence satisfies a central requirement
- **WHEN** a submitted record proves a requirement with matching candidate hashes and fresh results
- **THEN** central acceptance MAY record that requirement as satisfied without mutating the evidence source

#### Scenario: External evidence fails acceptance
- **WHEN** a submitted record is absent, stale, mismatched, or failing
- **THEN** the central task SHALL remain incomplete and SHALL return the deficiency for separate externally authorized remediation

### Requirement: The fixed annotated ref SHALL identify the final release externally

The intended ref SHALL be exactly `refs/tags/ntu-ai-keynote-v1.0.0`. Before external release finalization, immutable evidence SHALL establish that the ref is available for this release. A conflicting existing ref MUST block release and MUST NOT be moved, deleted, reused, or repointed by a central task. After all gates pass and external release occurs, the exact ref SHALL resolve to an annotated tag object; acceptance SHALL derive the authoritative commit by peeling `refs/tags/ntu-ai-keynote-v1.0.0^{commit}`, and the manifest MUST NOT claim its own containing commit SHA.

#### Scenario: Fixed tag ref is available
- **WHEN** pre-finalization tag-availability evidence is reviewed
- **THEN** it SHALL identify the external repository, exact ref, timestamp, and immutable inspection result showing that no conflicting tag object occupies `refs/tags/ntu-ai-keynote-v1.0.0`

#### Scenario: Final annotated ref is inspected
- **WHEN** the exact release ref is resolved after external release
- **THEN** it SHALL be an annotated tag object whose peeled commit contains the accepted manifest and exact public package digest

#### Scenario: Release ref is invalid
- **WHEN** the ref is lightweight, dynamic, alternate, conflicting, unverifiable, or peels to a commit containing different public bytes
- **THEN** release acceptance MUST fail

## Purpose

Define semantic, keyboard, visual, motion, typography, contrast, fallback, and print accessibility requirements for the audience deck at qualified stage viewports.

## ADDED Requirements

### Requirement: Only the active slide SHALL be exposed as active content

The document SHALL identify the active slide as a named semantic region and SHALL remove inactive slides from the accessibility tree and sequential focus order. Slide changes SHALL announce `Trang X trên 17` without disrupting the presenter or repeatedly stealing focus.

#### Scenario: Accessibility tree is inspected
- **WHEN** slide 9 is active
- **THEN** slide 9 SHALL be the only audience slide exposed as active content and inactive-slide controls or links MUST NOT be focusable

#### Scenario: Slide changes
- **WHEN** keyboard or pointer navigation activates another slide
- **THEN** the slide counter announcement SHALL update once without trapping focus or moving it unexpectedly into hidden content

### Requirement: Every runtime action SHALL be keyboard-operable with visible focus

Next, previous, Home, End, direct access, full/short selection, notes toggle and close, and reset SHALL be operable without a pointer. Focus indicators SHALL remain visible, keyboard focus MUST NOT be trapped, and click-anywhere navigation MUST NOT override focused controls.

#### Scenario: Keyboard-only walkthrough is performed
- **WHEN** a presenter operates the complete deck without a pointer
- **THEN** every required control and route action SHALL be reachable, operable, and reversible with visible focus and no keyboard trap

#### Scenario: Focused control receives activation
- **WHEN** Enter or Space activates a focused control
- **THEN** only that control's declared action SHALL occur and the background slide SHALL NOT advance incidentally

### Requirement: The 18px floor SHALL apply only to required audience meaning

At the unscaled authored 1280×720 stage, required audience narrative copy, numeric values, roundtable prompts, and every meaningful visual label that carries required slide meaning—including SVG text, node labels, legends, source or scope badges, and relationship labels—SHALL have a browser-computed font size of at least 18 CSS pixels in both qualified Safari and Chrome. This 18px floor SHALL NOT apply to source-attribution or provenance lines, slide counter or progress metadata, or the speaker-notes overlay; those excluded surfaces SHALL still remain legible, non-overlapping, contrast-compliant for their role, and present at every qualified viewport where they are intended to appear.

#### Scenario: Required audience text is measured
- **WHEN** Safari and Chrome computed styles are captured at the authored 1280×720 stage before the stage transform for narrative copy, numeric values, prompts, and meaningful visual labels
- **THEN** each included text surface SHALL compute to at least 18px in both browsers and SHALL fit without clipping or overlap

#### Scenario: Excluded auxiliary text is measured
- **WHEN** a source line, slide counter, progress label, or notes-overlay string computes below 18px
- **THEN** it SHALL NOT fail the scoped 18px floor solely for that reason, but it MUST still pass its applicable legibility, contrast, visibility, and overflow checks

#### Scenario: Required meaning is disguised as decorative
- **WHEN** visible text or a text-like vector carries required audience meaning but is marked decorative, omitted from the measured set, or moved only into an accessible description
- **THEN** it SHALL remain subject to the visible 18px floor and accessible-equivalent requirements and MUST NOT bypass either contract

### Requirement: Contrast and non-color meaning SHALL remain sufficient

Normal text SHALL provide at least 4.5:1 contrast and large text SHALL provide at least 3:1 contrast against its effective background. Every essential color distinction SHALL also have a text, shape, position, pattern, or label counterpart.

#### Scenario: Computed contrast is evaluated
- **WHEN** audience text is rendered in its actual browser state over its effective background
- **THEN** the computed foreground and background colors SHALL meet the applicable contrast threshold

#### Scenario: Color is unavailable
- **WHEN** a viewer cannot distinguish the NTU Red accent from other colors
- **THEN** every statistic, warning, state, and comparison SHALL retain its meaning through a non-color cue

### Requirement: Meaningful visuals SHALL have an accessible reading order and equivalent

Every meaningful diagram, chart, illustration, and icon group SHALL expose a concise Vietnamese text equivalent in a logical reading order. Decorative vectors SHALL be hidden from assistive technology and MUST NOT contain the only representation of required information.

#### Scenario: Meaningful diagram is encountered
- **WHEN** assistive technology reaches a slide containing a diagram
- **THEN** the slide SHALL expose the diagram's purpose, labels, values, relationships, and qualifier in a concise Vietnamese order equivalent to the visible meaning

#### Scenario: Decorative vectors are exposed
- **WHEN** the accessibility tree is inspected
- **THEN** decorative shapes and paths SHALL be absent and SHALL contribute no redundant or misleading names

### Requirement: Motion preferences and revisit behavior SHALL preserve complete meaning

The deck SHALL honor reduced-motion preferences by exposing final animation states without timed motion. Ordinary motion SHALL not flash or prevent reading, and revisiting an attention slide SHALL not leave its value hidden or partially initialized.

#### Scenario: Reduced motion is enabled
- **WHEN** the deck starts or navigates with reduced motion enabled
- **THEN** every slide SHALL expose complete final values and text immediately

#### Scenario: Attention slide is revisited
- **WHEN** the PwC or MIT slide becomes active again
- **THEN** its content SHALL remain accessible throughout the reset and entry sequence and SHALL finish in the same complete state

### Requirement: Font fallback and qualified scaling SHALL preserve comprehension

Removing the local fonts or rendering at any qualified viewport SHALL NOT clip, overlap, hide, reorder, or change the meaning of required audience content. Vietnamese glyphs SHALL remain readable through the declared system-font fallback.

#### Scenario: Local fonts are unavailable
- **WHEN** the venue package is opened without the bundled font files
- **THEN** all Vietnamese audience copy, labels, prompts, controls, and notes SHALL remain readable without overflow or missing required glyphs

#### Scenario: Stage is letterboxed
- **WHEN** the deck renders at a qualified 16:10 or 4:3 viewport
- **THEN** scaling SHALL preserve complete content, safe-area containment, focus visibility, and semantic order

### Requirement: Printed fallback SHALL remain accessible and complete

Print output SHALL contain exactly one complete slide per page in the approved order, preserve backgrounds and final values, and exclude notes and interactive controls. Its reading order and text extraction SHALL preserve the slide's essential meaning.

#### Scenario: PDF accessibility checks are performed
- **WHEN** the pre-generated 17-page fallback is inspected
- **THEN** pages SHALL be ordered 1–17, essential text SHALL follow a meaningful reading order, and no required content SHALL be clipped, hidden, or replaced by animation state

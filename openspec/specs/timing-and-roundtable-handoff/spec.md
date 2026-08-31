## Purpose

Define the exact full and short timing routes, entry behavior for timed animations, synchronized notes, and the transition from keynote content into the roundtable.

Stable identity policy: every requirement and scenario SHALL carry the explicit capability-qualified ID shown immediately below its heading. Headings are display text only; IDs SHALL NOT be derived implicitly from headings. IDs MUST be unique across all six specs, renaming a heading MUST preserve its existing ID, and any collision MUST fail central validation.

## Requirements

### Requirement: The full route SHALL total exactly 765 seconds
**Requirement ID:** `REQ-trh-the-full-route-shall-total-exactly-765-seconds`

The full route SHALL visit slides 1–17 in order with per-slide seconds `30,60,45,45,45,45,45,45,40,40,50,50,50,50,50,45,30`. Notes timing windows MUST be contiguous, MUST begin at 0:00, and MUST end at 12:45.

#### Scenario: Full timing is calculated
**Scenario ID:** `SCN-trh-the-full-route-shall-total-exactly-765-seconds-full-timing-is-calculated`
- **WHEN** the full-route slide durations are summed and their cumulative windows are derived
- **THEN** all 17 slides SHALL be visited once, no gap or overlap SHALL exist, and the final boundary SHALL be exactly 12:45

#### Scenario: Full-route duration drifts
**Scenario ID:** `SCN-trh-the-full-route-shall-total-exactly-765-seconds-full-route-duration-drifts`
- **WHEN** any slide duration or cumulative boundary causes the total to differ from 765 seconds
- **THEN** the candidate MUST fail timing acceptance

### Requirement: The short route SHALL total exactly 600 seconds and skip only slides 4 and 8
**Requirement ID:** `REQ-trh-the-short-route-shall-total-exactly-600-seconds-and-skip-only-slides-4-and-8`

The short route SHALL visit `1,2,3,5,6,7,9,10,11,12,13,14,15,16,17` with per-visited-slide seconds `25,25,35,40,25,35,25,35,45,40,45,45,45,105,30`. It SHALL retain all three journey layers, SHALL skip rather than merge slides 4 and 8, and MUST total exactly 10:00.

#### Scenario: Short route is traversed sequentially
**Scenario ID:** `SCN-trh-the-short-route-shall-total-exactly-600-seconds-and-skip-only-slides-4-and-8-short-route-is-traversed-sequentially`
- **WHEN** the presenter selects short mode at the permitted startup state and advances to the end
- **THEN** exactly 15 slides SHALL be visited in the declared order, only slides 4 and 8 SHALL be skipped, and the cumulative end SHALL be exactly 10:00

#### Scenario: Direct access is used in short mode
**Scenario ID:** `SCN-trh-the-short-route-shall-total-exactly-600-seconds-and-skip-only-slides-4-and-8-direct-access-is-used-in-short-mode`
- **WHEN** the presenter directly opens another slide
- **THEN** direct access SHALL NOT mutate the canonical short-route membership or timing contract

### Requirement: Notes SHALL expose route-specific timing without contradiction
**Requirement ID:** `REQ-trh-notes-shall-expose-route-specific-timing-without-contradiction`

Each slide's notes SHALL identify its full-route cumulative window, its short-route window or explicit skipped state, and one delivery cue. Slide 16 notes SHALL contain the full moderator expansions while its audience surface retains only the concise prompts.

#### Scenario: Presenter changes route mode
**Scenario ID:** `SCN-trh-notes-shall-expose-route-specific-timing-without-contradiction-presenter-changes-route-mode`
- **WHEN** the same slide is viewed in full and short mode
- **THEN** its notes SHALL show the timing applicable to the active route and SHALL NOT contradict audience copy

#### Scenario: Skipped slide is inspected in short mode
**Scenario ID:** `SCN-trh-notes-shall-expose-route-specific-timing-without-contradiction-skipped-slide-is-inspected-in-short-mode`
- **WHEN** notes data for slide 4 or slide 8 is reviewed under the short contract
- **THEN** it SHALL state that the slide is skipped and MUST NOT describe its content as merged into another slide

### Requirement: Attention animations SHALL begin on target-slide entry
**Requirement ID:** `REQ-trh-attention-animations-shall-begin-on-target-slide-entry`

The PwC counter and MIT emphasis SHALL reset before their target slide becomes active and SHALL begin only when that target slide enters the active audience state. They MUST NOT begin on page initialization while another slide is active, on the preceding slide's exit, or merely because an inactive slide exists in the document.

#### Scenario: Presenter advances to an attention slide
**Scenario ID:** `SCN-trh-attention-animations-shall-begin-on-target-slide-entry-presenter-advances-to-an-attention-slide`
- **WHEN** the target slide changes from inactive to active through sequential navigation
- **THEN** its attention animation SHALL start once after the target slide is active and visible

#### Scenario: Target slide is initial fragment state
**Scenario ID:** `SCN-trh-attention-animations-shall-begin-on-target-slide-entry-target-slide-is-initial-fragment-state`
- **WHEN** a valid direct or reload fragment opens the deck on the PwC or MIT slide
- **THEN** the corresponding animation SHALL start from its entry state when that slide becomes the initial active slide

#### Scenario: Presenter revisits an attention slide
**Scenario ID:** `SCN-trh-attention-animations-shall-begin-on-target-slide-entry-presenter-revisits-an-attention-slide`
- **WHEN** the target slide becomes active after having previously been left
- **THEN** the effect SHALL reset and replay once for the new entry

#### Scenario: Reduced motion or print is active
**Scenario ID:** `SCN-trh-attention-animations-shall-begin-on-target-slide-entry-reduced-motion-or-print-is-active`
- **WHEN** reduced motion is requested or the deck is rendered for print
- **THEN** the final complete value and message SHALL be present without a timed entry effect

### Requirement: The roundtable transition SHALL preserve separate audience jobs
**Requirement ID:** `REQ-trh-the-roundtable-transition-shall-preserve-separate-audience-jobs`

Slide 16 SHALL solicit discussion through three concise prompts anchored respectively to the registered 95% organization context, 39% workforce-skills context, and **hơn 40%** Gartner forecast context; slide 17 SHALL perform the verbal handoff in 30 seconds. The 95% prompt MUST NOT imply that the distinct 5% integrated-pilot finding is its complementary remainder. The handoff SHALL acknowledge the roundtable and NTU alumni connection without restating the prompts.

#### Scenario: Keynote reaches the final two slides
**Scenario ID:** `SCN-trh-the-roundtable-transition-shall-preserve-separate-audience-jobs-keynote-reaches-the-final-two-slides`
- **WHEN** slides 16 and 17 are delivered in sequence
- **THEN** slide 16 SHALL perform the question-setting job, preserve **hơn 40%** in its Gartner anchor and the organization-versus-integrated-pilot distinction in any slide-7 reference, and slide 17 SHALL perform only the handoff job within its assigned timing

#### Scenario: Panelist details are unavailable
**Scenario ID:** `SCN-trh-the-roundtable-transition-shall-preserve-separate-audience-jobs-panelist-details-are-unavailable`
- **WHEN** final panelist names or roles have not been supplied
- **THEN** slide 17 MUST remain complete and neutral without conditional text, empty slots, or unresolved markers

## ADDED Requirements

### Requirement: Self-contained offline HTML deck

The presentation SHALL be delivered as a single HTML file that opens and renders
fully in any modern browser with no build step, no server, and no live network
access. Any slide framework or styling MUST be vendored inline or degrade
gracefully so the deck remains usable offline.

#### Scenario: Opening the deck offline

- **WHEN** the presenter opens the HTML file directly from disk (`file://`) with no internet connection
- **THEN** all slides, layout, fonts fallbacks, and navigation render correctly without missing content or broken styling

#### Scenario: No build step required

- **WHEN** a reviewer receives only the single HTML file
- **THEN** they can present it without installing dependencies, running a bundler, or starting a dev server

### Requirement: 20-minute, three-act narrative structure

The deck SHALL be sized for a ~20-minute delivery and organized into three acts:
(1) setup — hook, pitch/positions map, and the stat-bucket decoder; (2) styles by
pitch zone; (3) putting it together — chemistry, a sample XI, and recap. Total
slide count SHALL land between 15 and 20 content slides.

#### Scenario: Slide count within timing budget

- **WHEN** the deck is complete
- **THEN** it contains between 15 and 20 content slides so that average pacing stays near 60–75 seconds per slide for a 20-minute talk

#### Scenario: Act ordering is explicit

- **WHEN** the audience advances through the deck
- **THEN** setup slides appear before any per-style slide, and chemistry/sample-XI/recap slides appear after all per-style slides

### Requirement: Keyboard-navigable slides

The deck SHALL support sequential slide navigation via keyboard (next/previous)
and MUST visually present one slide at a time in presentation view.

#### Scenario: Advancing and reversing

- **WHEN** the presenter presses the next-slide key and then the previous-slide key
- **THEN** the deck advances to the following slide and then returns to the prior slide without losing state

### Requirement: Consistent per-style visual template

Every per-style slide SHALL use one shared visual template containing: the style
name, a position-activation badge, a one-line behavior description, a "stat dial"
showing the style's emphasis across the six stat buckets, and its famous-player
exemplars each accompanied by a player image (a rights-safe photo or its
deterministic fallback). The template MUST be visually consistent across all
style slides.

#### Scenario: Style slide renders all required elements

- **WHEN** any per-style slide is shown
- **THEN** it displays the style name, activatable position(s), a one-line description, a stat-dial visualization, and at least one exemplar player with an accompanying image

#### Scenario: Template consistency

- **WHEN** the audience moves between two different per-style slides
- **THEN** the same layout regions (name, badge, description, dial, exemplars with images) appear in the same positions

#### Scenario: Every exemplar has a visible image

- **WHEN** an exemplar player is shown on any style slide
- **THEN** it is accompanied by either an embedded rights-safe photo or a deterministic name-derived placeholder, never a blank or broken image

### Requirement: Speaker notes and recap

The deck SHALL include speaker-facing notes for pacing/talking points and a final
recap slide that restates the core takeaways (playstyle = weighting of shared
stats; position activation matters; exemplars aid recall).

#### Scenario: Recap present as final content

- **WHEN** the presenter reaches the end of the deck
- **THEN** a recap/takeaways slide summarizes the key messages of the talk

#### Scenario: Speaker notes available

- **WHEN** the presenter needs talking points for a slide
- **THEN** speaker notes are available for the setup and per-zone slides (via the framework's notes view or an inline notes region)

### Requirement: Interactive player peek overlay

The deck SHALL let the audience open an on-demand overlay for any exemplar that
displays a high-resolution portrait of the player alongside a detailed stat panel.
The overlay SHALL be openable by hovering the exemplar (on pointer devices) and by
tapping it (on touch devices). The high-resolution portrait MUST be embedded inline
so it renders offline with no network request.

#### Scenario: Opening the peek on a pointer device

- **WHEN** the presenter hovers the pointer over an exemplar's avatar
- **THEN** an overlay appears showing that player's high-resolution portrait and a detailed stat panel

#### Scenario: Opening the peek on a touch device

- **WHEN** a viewer taps an exemplar's avatar on a device without hover
- **THEN** the same overlay appears with the high-resolution portrait and stat panel

#### Scenario: Hi-res portrait is offline-safe

- **WHEN** the deck is opened with no network connection and a peek is triggered
- **THEN** the high-resolution portrait renders from embedded data with no outbound image request

### Requirement: Peek overlay must not trap presentation navigation

The peek overlay SHALL be non-modal: it MUST NOT trap keyboard focus or block
slide navigation. Advancing or reversing a slide SHALL dismiss any open peek, and
at most one peek SHALL be open at a time. The overlay MUST also be dismissable
directly (Esc key, pointer leaving the target, tapping the backdrop, or a close
control).

#### Scenario: Navigation dismisses an open peek

- **WHEN** a peek overlay is open and the presenter presses the next- or previous-slide key
- **THEN** the deck advances or reverses and the overlay closes, without the navigation being swallowed

#### Scenario: Explicit dismissal

- **WHEN** a peek overlay is open and the viewer presses Esc, moves the pointer away, taps the backdrop, or activates the close control
- **THEN** the overlay closes and the deck remains on the current slide

#### Scenario: One peek at a time

- **WHEN** a peek overlay is open and the viewer opens a peek for a different exemplar
- **THEN** the previously open overlay closes so only one is visible

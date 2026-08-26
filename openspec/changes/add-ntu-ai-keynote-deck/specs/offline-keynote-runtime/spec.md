## Purpose

Define the observable offline runtime contract that keeps the keynote navigable, recoverable, visually stable, and usable from the venue package without a server or network.

## ADDED Requirements

### Requirement: The keynote SHALL launch directly and remain network-independent

The venue package SHALL open through `file://` in an installed modern Safari or Chrome browser without a server, build step, CDN, live network, package manager, account, or production runtime dependency. Every runtime asset MUST resolve through a relative path inside the allowlisted venue package. Compliance SHALL be established by immutable, hash-bound external runtime evidence consumed read-only by the central change; local OpenSpec artifact or task status MUST NOT substitute for launch and interaction evidence.

#### Scenario: Offline direct launch succeeds
- **WHEN** the allowlisted venue package is copied to a new folder and `index.html` is opened while HTTP and HTTPS access are unavailable
- **THEN** all 17 slides, local fonts, the NTU logo, navigation, notes, visuals, and the PDF fallback SHALL remain available without a failed required asset

#### Scenario: External runtime reference is introduced
- **WHEN** a required runtime resource resolves to a live URL, protocol-relative URL, package import, server endpoint, or file outside the venue package
- **THEN** the candidate MUST fail offline-runtime acceptance

### Requirement: The stage SHALL preserve its authored geometry within qualified viewports

The keynote SHALL use a fixed 1280×720 authored stage, a 5% content-safe area, and centered non-distorting letterbox scaling. Required content MUST remain within the safe area at qualified 16:9, 16:10, and 4:3 viewports; acceptance SHALL NOT claim pixel-identical rendering across browsers, operating systems, projectors, scaling settings, or overscan conditions.

#### Scenario: Qualified viewport scales the stage
- **WHEN** the deck is rendered at 1920×1080, 1440×900, 1366×768, or 1024×768
- **THEN** the complete stage SHALL remain centered with preserved aspect ratio, visible letterboxing where needed, and no required content outside the safe area

#### Scenario: Viewport aspect ratio differs from 16:9
- **WHEN** the available viewport is 16:10 or 4:3
- **THEN** the stage MUST letterbox rather than stretch, crop, or reflow its authored geometry

### Requirement: Navigation SHALL implement deterministic full and short routes

The runtime SHALL support next, previous, Home, End, direct slide access, standard keyboard/clicker input, and pointer navigation without allowing one input event or key repeat to advance more than one route position. It SHALL expose the current slide, progress, and active full/short route mode.

#### Scenario: Sequential navigation follows the active route
- **WHEN** the presenter advances from the first slide to the route boundary
- **THEN** each accepted input SHALL move exactly one position through the selected full or short route and SHALL stop safely at the boundary

#### Scenario: Interactive surface receives a click
- **WHEN** the presenter clicks a control, notes surface, or other interactive element
- **THEN** background click-to-advance behavior MUST NOT change the slide

### Requirement: Fragment state SHALL recover safely under `file://`

The current route mode and slide SHALL be represented by canonical URL-fragment state compatible with Safari `file://`. Reload SHALL restore a valid state, invalid or unsupported state SHALL fall back safely, and reset SHALL return to full mode slide 1 without depending on `localStorage`.

#### Scenario: Valid state is reloaded
- **WHEN** the deck is reloaded on slide 9 in either route mode
- **THEN** the runtime SHALL restore slide 9 in the same route mode

#### Scenario: Fragment state is absent or invalid
- **WHEN** the URL fragment is missing, malformed, or names an unavailable route position
- **THEN** the runtime MUST start in a safe canonical state and MUST NOT expose an empty or broken stage

#### Scenario: Browser storage is denied
- **WHEN** persistent browser storage is unavailable or rejected
- **THEN** navigation, fragment recovery, and reset SHALL retain their required behavior

### Requirement: Speaker notes SHALL remain synchronized and controlled

Every slide SHALL provide Vietnamese notes with timing and delivery cues. The notes surface SHALL be off by default, synchronize with the active slide, close with Escape, warn that it is audience-visible on mirrored displays, suppress background navigation from notes interactions, and remain absent from print output.

#### Scenario: Notes follow navigation
- **WHEN** notes are open and the presenter changes slides
- **THEN** the notes surface SHALL show only the newly active slide's notes and timing cues

#### Scenario: Notes are closed or printed
- **WHEN** notes are closed or the deck is rendered for print
- **THEN** notes content and controls MUST NOT be exposed as audience slide content

### Requirement: Motion SHALL be limited and state-safe

The keynote SHALL provide only the PwC counter, the MIT emphasis, and a restrained base slide transition as motion effects. Each attention effect SHALL expose its complete final meaning under print and reduced-motion preferences and SHALL replay correctly on a later re-entry to its slide.

#### Scenario: Reduced motion is requested
- **WHEN** the browser reports `prefers-reduced-motion: reduce`
- **THEN** every animated value and statement SHALL appear immediately in its complete final state without loss of meaning

#### Scenario: An attention slide is revisited
- **WHEN** the presenter leaves and later re-enters the PwC or MIT slide
- **THEN** the corresponding effect SHALL begin from its defined entry state and replay once for that entry

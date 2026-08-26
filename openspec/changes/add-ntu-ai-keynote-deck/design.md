## Context

The deliverable is a stage presentation with one chance to work: venue equipment,
possibly a borrowed laptop, no guaranteed internet. See proposal.md for motivation
and scope. Existing assets from exploration: `~/Developer/ntu-keynote/assets/ntu-logo.png`
(1304×512 transparent PNG, palette verified against official NTU hex values) and
verified brand colors extracted from NTU's Quick Brand Guide PDF
(NTU Blue `#181C62`, NTU Red `#D71440`).

## Goals / Non-Goals

**Goals:**
- Zero-failure presentation runtime: opens by double-click from USB, no network,
  no build, no accounts.
- 17 slides in a fixed 3-act timing budget (10–15 min) with speaker-visible timing
  cues.
- Correct Vietnamese rendering everywhere (all diacritics) without CDN fonts.
- Identical appearance on any projector resolution (16:9 letterboxed scaling).

**Non-Goals:**
- No authoring tooling, no slide CMS, no edit-time UI — content is edited directly
  in the HTML source.
- No touch/swipe gestures, no presenter-remote protocol beyond standard arrow keys.
- No dark/light toggle — dark stage theme only.

## Decisions

### D1: Single self-contained HTML file + sibling `assets/` folder
One `index.html` with inline `<style>` and `<script>`; logo and font woff2 files
referenced by relative path from `assets/`.
- **Why**: the whole folder copies to a USB stick and runs anywhere a browser
  exists. No bundler, no node_modules, no version drift.
- **Alternatives**: (a) fully inline everything as base64 data URIs — rejected:
  bloats the HTML ~70KB and makes copy editing painful; relative assets keep the
  file readable. (b) Reveal.js vendored — rejected: ~2MB of machinery and its own
  CSS opinions for 17 static slides; the only features needed (keyboard nav,
  transitions, notes) are ~100 lines of vanilla JS. (c) Slidev — rejected: Node
  build step is a stage-failure mode.

### D2: Fixed 16:9 stage with CSS transform scaling + safe margins
Slides are authored at a fixed 1280×720 coordinate space; a JS resize handler
computes `scale = min(vw/1280, vh/720)` and applies `transform: scale()` to the
stage container, centered with letterboxing. All content sits inside a 5% safe
margin (projector overscan protection). Claim scope: layout is centered and
letterboxed within tested bounds (16:9, 16:10, 4:3 viewports) — NOT
"pixel-identical on any display"; browser chrome, OS scaling, and overscan are
handled by letterboxing + safe margins, and the operator checklist (task 8.2)
documents fullscreen entry.
- **Why**: stable layout on any projector/window size; text sizes are authored
  once and never reflow; safe margins survive real projector overscan.
- **Alternative**: responsive `vw`/`vh` typography — rejected: layout shifts
  between rehearsal laptop and venue projector are exactly what must not happen.

### D3: Navigation model — arrow keys + click-anywhere + Home/End
`ArrowRight`/`Space`/`PageDown`/click = next; `ArrowLeft`/`PageUp` = previous;
`Home`/`End` = first/last. Click handlers ignore clicks while the notes overlay
is open.
- **Why**: standard presentation clickers emit arrow keys or PageDown — this
  covers all common hardware with no pairing/driver concerns.

### D4: Speaker notes as hidden overlay with timing cues, toggled by `S`
Each slide carries a `data-notes` attribute (single representation — no
`<aside>` alternative, to avoid implementation churn) containing timing cues ("~3:00 — pivot to tảng băng") and delivery reminders. `S` toggles a
semi-transparent overlay panel; it never appears in print output.
- **Why**: for a 10–15 minute talk, pacing cues matter more than script notes;
  a keypress toggle keeps the audience view clean.
- **Alternative**: separate presenter window (Reveal-style) — rejected: requires
  popup windows, which venue machines often block.

### D5: NTU brand palette adapted for projection
Background: NTU Blue darkened to `#0D1038` (pure brand blue is too bright for a
full-bleed stage background and projectors wash out mid-blues). Accent: NTU Red
`#D71440` for headline statistics. Body text: white at ≥90% opacity; secondary
text at 60%.
- **Why**: brand recognition (alumni event) + stage contrast rules (dark bg,
  high-contrast accent). Red doubles as the "alarm" color for the failure stats —
  brand and narrative need the same color.

### D6: Be Vietnam Pro, bundled locally, vietnamese subset
Download woff2 files (weights 400/600/800) via google-webfonts-helper with the
`vietnamese` subset; declare via local `@font-face` with `font-display: block`.
- **Why**: full diacritic coverage is non-negotiable; `font-display: block`
  prevents a flash of fallback glyphs on slide entry.
- **Alternative**: system font stack — rejected: no cross-platform guarantee of
  Vietnamese glyph quality.

### D7: Two animations only, both CSS-driven
(1) Counter on the $15.7T slide: JS increments a number over ~1.2s when the slide
activates. (2) Slam-in on the 95% slide: CSS `transform: scale()` + opacity keyframe
triggered by the slide's `.active` class. All other transitions: a single 300ms
fade.
- **Why**: animation budget discipline — every extra effect dilutes the two
  emotional peaks. CSS-class-triggered animations replay correctly when revisiting
  a slide.

### D8: Print stylesheet for PDF fallback
`@media print`: one slide per page (`page-break-after`), notes overlay hidden,
animations frozen at final state, background forced dark with
`print-color-adjust: exact`.
- **Why**: if the venue machine cannot run the HTML, a PRE-GENERATED
  `keynote-fallback.pdf` ships with the deck (task 7.2). Venue-time Cmd+P is a
  last resort only — print settings (backgrounds, orientation) are
  browser-dependent and must not be the primary fallback.

### D9: State recovery via localStorage
Current slide number persists to localStorage on every navigation and is
restored on page load (default slide 1 if absent/corrupt); `R` clears it.
- **Why**: an accidental reload mid-talk must not reset the deck to slide 1 in
  front of the audience. localStorage survives reloads without any server.
- **Alternative**: URL hash routing (`#slide-9`) — acceptable but exposes
  position in the address bar and invites accidental link-shares; localStorage
  is simpler and invisible.

## Risks / Trade-offs

- [Venue browser is ancient (IE/old Edge)] → Mitigation: the JS uses only
  `classList`, `addEventListener`, `transform` — no ES2020+ syntax; test in Safari
  (macOS default) which is the most likely venue browser. PDF fallback covers the
  worst case.
- [Projector resolution/aspect differs from 16:9] → Mitigation: D2 letterboxes
  rather than stretches; content never distorts.
- [Clicker emits unexpected keycodes] → Mitigation: click-anywhere navigation as
  universal fallback; Space/PageDown also bound.
- [Font files fail to load (corrupt USB copy)] → Mitigation: `font-display: block`
  then fallback to system sans — deck remains legible, just less polished.
- [Speaker notes visible to audience by accident] → Mitigation: overlay is
  off by default and only toggles on explicit `S`; add a visible "notes ON" badge
  so the speaker notices.
- [Statistic challenged by audience] → Mitigation: every stat slide carries a
  small source line (PwC/MIT/Gartner/WEF/Google); sources list also in notes.
- [Accidental reload mid-talk resets position] → Mitigation: D9 localStorage
  restore + reload-recovery step in the venue rehearsal (task 8.3).
- [Projector overscan clips edge content] → Mitigation: 5% safe margin (D2);
  nothing meaningful is authored outside it.
- [Notes overlay accidentally shown to audience on mirrored display] →
  Mitigation: overlay is off by default, carries a visible "notes ON" badge,
  and the README cue sheet (task 8.2) is the private alternative.
- [Laptop sleeps/display blanks during talk] → Mitigation: operator checklist
  (task 8.2): disable sleep + display blanking, AC power.

## Migration Plan

Not applicable (new standalone deliverable). Delivery: copy the entire
`~/Developer/ntu-keynote/` folder to USB; open `index.html`; rehearse once with
the notes overlay to confirm timing cues.

## Open Questions

Both original open questions are resolved by task contract rather than left open:
- First-party call-center metrics for slide 11: task 4.5 requires either a real
  metric or the qualitative framing with NO audience-visible placeholder marker —
  the deck ships clean either way.
- Event-specific logo beside the NTU mark: task 3.1 reserves the slot; if no
  logo arrives, the typographic "NTU Alumni" treatment is the shipped state.

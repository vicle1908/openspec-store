## Context

This change captures a standalone deliverable: a ~20-minute HTML slide deck that
teaches football **playing styles** and their **key stats**, using **eFootball
2026** as the concrete reference model. It is not application code — it touches no
Python sub-repo, no `tdt_core` client, and no service. The design exists mainly to
lock a few decisions before authoring so the deck stays consistent, offline-safe,
and honest about sourcing.

Current state: no presentation exists. Source material for the canonical style
list and attribute model was gathered from public eFootball 2026 documentation
(FIFPlay attribute/style listings, community activation guides). The styles and
their position activations are treated as the authoritative taxonomy; player
exemplars are illustrative.

Constraints:
- Single presenter, runs from a laptop browser, possibly with no internet.
- Must be shareable as one file (email/USB/repo) with zero setup.
- 20-minute wall-clock budget → 15–20 content slides.

## Goals / Non-Goals

**Goals:**
- Produce one self-contained HTML file that presents offline with keyboard nav.
- Teach a reusable mental model: playstyle = a weighting over six shared stat buckets.
- Cover all ~21 eFootball 2026 styles grouped by pitch zone, ~3 per slide.
- Give every style a position badge, one-line behavior, stat dial, and famous exemplars (modern + historical).
- Close with chemistry guidance and a sample XI built from styles.

**Non-Goals:**
- No live data, squad builder, or scraper.
- No exhaustive numeric per-player cards (numbers illustrative unless sourced).
- No dependence on a specific in-game patch beyond the published 2026 style list.
- Not a general real-world tactics course; eFootball is the framing device.

## Decisions

### Decision: Single-file HTML with reveal.js vendored inline (fallback to plain CSS)
Use reveal.js for slide navigation/notes, but vendor the minimal CSS/JS inline (or
CDN-with-inline-fallback) so the file opens from `file://` offline. Rationale:
reveal.js gives keyboard nav, a speaker-notes view, and fragments for near-zero
cost. Alternative considered: plain CSS scroll-snap slides (simpler, but weaker
speaker notes and no fragment reveals). If vendoring bloats the file
unacceptably, fall back to a hand-rolled CSS `:target`/scroll-snap deck that still
satisfies the offline + keyboard requirements.

### Decision: "Stat dial" as pure CSS horizontal bars
Represent each style's six-bucket emphasis as labeled horizontal bars (0–100%
width) rather than a JS chart library. Rationale: keeps the file dependency-free,
renders offline, and reads instantly on a projector. Alternative considered: radar
/hexagon charts (visually appealing, on-brand for football games, but need canvas
/SVG scripting and are harder to read at a glance from the back of a room).

### Decision: Six-bucket taxonomy as the spine
Map eFootball attributes into Attacking, Technique, Passing, Defending, Physical,
Aerial. Every style slide reuses these six labels in the same order. Rationale: a
fixed decoder ring lets the audience "read" any style slide after learning it
once; consistency is the teaching device.

### Decision: 3-act structure, ~3 styles per zone slide
Act 1 setup (title/hook, pitch+positions, stat-bucket decoder), Act 2 styles by
zone, Act 3 chemistry + sample XI + recap. Grouping ~3 styles per slide keeps the
count in the 15–20 band and pace near 60–75s/slide.

### Decision: Exemplars mix modern and historical, labeled illustrative
Each style names 1–3 well-known players spanning eras (e.g., Goal Poacher →
Inzaghi + Haaland). Any numeric stat shown is marked illustrative unless a source
is cited. Rationale: recall aid without over-claiming in-game accuracy.

### Decision: File location
Place the deck at `tdt-meta/presentations/efootball-playstyles.html`. Rationale:
keeps the artifact with other meta content, out of `docs/` (which is
mirror/reference material), and it is not tied to any code repo.

### Decision: Visual theme — eFootball "player card" aesthetic
Adopt a sporty player-card look: dark/high-contrast background, position badges,
and the CSS stat dials styled like in-game rating bars. Rationale: on-theme for
the subject, makes the per-style template visually memorable, and the stat dials
double as the card's rating strip. Alternatives considered: clean/minimal
(rejected — less engaging for this topic) and neubrutalism (rejected — visual
noise competes with the dials).

### Decision: Real key attributes in the peek panel, paired with the illustrative dial (supersedes "illustrative only")
The slide surface stays illustrative — the always-visible stat dial is a 0–5
teaching abstraction across the six buckets, and no raw numbers are printed on the
slide itself. But the interactive peek overlay (see below) shows **real eFootball
2026 key attributes** for the exemplar, deliberately reversing the earlier
"no real in-game numeric values" stance.

Rationale: pairing our 0–5 dial with the real attributes in the same panel turns a
potential contradiction into the deck's sharpest teaching beat — "our dial is a
simplification; here are the real numbers it summarizes." The thesis (playstyle =
a weighting of shared stats) becomes literally visible.

To keep the numbers honest and patch-safe:
- **Representative attribute per bucket** (not the full ~30-attribute card): ATK →
  Finishing, TEC → Dribbling, PAS → Low Pass, DEF → Defensive Awareness, PHY →
  Speed, AER → Heading. GK styles show GK Reflexes / Reach / Catching / Awareness.
  Six values read cleanly on a projector and map 1:1 to the six buckets.
- **Pinned, dated snapshot**: each player's attributes are captured once at
  authoring time and stamped with a **fetch date** ("stats as of Jul 2026"), not a
  live feed. A snapshot cannot silently rot; the date makes staleness visible.
- **Card version**: modern players use their **base/current** card; retired legends
  exist only as special cards, so they use the **Epic (peak)** card, labelled as
  such on the panel so a peak rating is never mistaken for a neutral base rating.
- **Source + attribution**: values are read from the community database pesdb.net
  and attributed on-panel ("stats: pesdb, base card"). These are facts about the
  game presented as dated reference.

This supersedes both the "marquee real numbers" option and the prior
"illustrative only" decision.

### Decision: Real player photos, rights-safe and embedded (supersedes CSS-only visuals)
Each exemplar is illustrated with a real player photo. This supersedes the earlier
"visuals are CSS-only / images optional" stance in the original Impact section.
Constraints that shape the approach:
- **Rights:** only Wikimedia Commons images under CC-BY, CC-BY-SA, CC0, or public
  domain are eligible. Copyrighted agency/press photos (Getty, AP, Reuters, etc.)
  are never embedded. License is read programmatically from the Commons
  `imageinfo.extmetadata` field and filtered against an allowlist.
- **Offline (hard requirement preserved):** photos are fetched from Commons at
  *authoring* time, downscaled, and embedded inline as base64 data URIs. The
  shipped file makes zero network requests — the offline requirement is preserved
  temporally (fetch now, embed, present offline), not weakened.
- **Attribution:** CC-BY / CC-BY-SA require visible credit, satisfied by an in-deck
  credits slide listing author + license per photo.
Alternatives considered: hotlinking Commons URLs (rejected — breaks offline); a
separate assets folder (rejected — breaks single-file); generic clip-art
(rejected — defeats the "real player" goal).

### Decision: Deterministic SVG avatar fallback for missing photos
Commons coverage is incomplete — some exemplars (especially historical players)
have no rights-safe photo. For those, generate a deterministic, name-seeded SVG
avatar (initials on a hue derived from a hash of the name) inline. Rationale:
guarantees no blank or broken-image slot, stays offline (pure inline SVG, no
library, no network), and is stable across renders. Alternative considered:
pulling a third-party avatar library (rejected — adds a dependency for something a
~20-line pure function does; keeps the file dependency-free per the deck's spine).

### Decision: Interactive player peek — non-modal overlay on hover + tap
Hovering an exemplar chip (desktop) or tapping it (touch) opens an overlay showing
the hi-res portrait and the real-attribute stat panel. The overlay is **non-modal
and auto-dismissing**: it never traps focus, and advancing/reversing a slide (or
pressing Esc, or moving the pointer away / tapping the backdrop) closes it. Only
one peek is open at a time.

Rationale: the deck is driven by keyboard/clicker navigation from the front of a
room. A modal that captured focus would strand a presenter mid-talk. Making the
peek a "reward" layer that yields immediately to navigation keeps presentation flow
intact while still enabling the interaction during live delivery and self-guided
reading. Alternatives considered: a modal dialog (rejected — traps clicker nav); a
separate detail slide per player (rejected — would blow the 15–20 slide budget by
44 slides); inline expansion within the card (rejected — reflows the shared
template and breaks visual consistency).

### Decision: Touch support — tap-to-open, tap-away / close-button to dismiss
On devices without hover, a tap on the exemplar avatar opens the peek; tapping the
backdrop, a close control, or navigating dismisses it. Rationale: `:hover` does not
exist on touch, so the same information must be reachable by tap for the deck to be
usable when shared as a file on a tablet/phone. The open/close logic is shared with
the desktop hover path so behaviour stays consistent.

### Decision: Two-tier images — small thumb for the chip, hi-res for the peek
Keep the existing ~220px thumbnail as the always-visible circular chip (fast first
paint), and fetch a **larger portrait (~480–600px)** for the peek overlay, stored
in a separate hi-res manifest. Rationale: enlarging the 220px thumb looks soft;
a dedicated hi-res tier is sharp on the overlay while the chip render path stays
lean. Same Commons source files and licenses as the thumbnails, so no new rights
review is needed — only a larger `iiurlwidth`. Trade-off: ~3.5–4.5 MB added to the
single file (≈5–6 MB total), which still opens instantly offline; accepted because
the single-file offline invariant is preserved. Alternative considered: upscaling
the existing thumbnail via CSS (rejected — visibly blurry); one shared large image
for both chip and peek (rejected — bloats first paint for 44 always-visible chips).

### Decision: Photo pipeline is a repeatable build script, output committed
A small Node/shell script queries Commons, filters by license, downscales, base64-
encodes, and writes an image manifest (name → data URI + source URL + license +
author). The manifest is embedded into the deck's data model. Rationale: makes the
sourcing auditable and regenerable, and records the provenance the spec requires in
`data-reference.md`. The script itself is authoring-time tooling, not shipped runtime.

### Decision: Language — English
Author the deck in English per workspace default.

## Risks / Trade-offs

- **[Style list drifts with patches]** → Treat the eFootball 2026 published list as the baseline; note in a source slide that minor activation tweaks may occur.
- **[Exemplar accuracy debated]** → Choose broadly agreed archetypes and label player numbers illustrative; avoid contentious edge cases.
- **[reveal.js CDN unavailable offline]** → Vendor inline or provide CSS fallback; verify by opening with network disabled.
- **[Too many styles for 20 min]** → Enforce ~3-per-slide zone grouping; chemistry/XI act absorbs synthesis instead of more per-style slides.
- **[Overlong single file from embedded photos]** → Downscale each photo (small thumbnail width, e.g. ~160–200px) and compress before base64 embedding; budget total added size and prefer the deterministic SVG fallback over large images where coverage is thin.
- **[Incomplete rights-safe photo coverage]** → Deterministic name-seeded SVG avatar guarantees every slot is filled; historical players most likely to fall back.
- **[Attribution obligation for CC-BY/CC-BY-SA]** → Dedicated credits slide lists author + license per embedded photo; provenance also recorded in `data-reference.md`.
- **[Wrong-person / mislabeled Commons image]** → Fetch via the player's Wikipedia lead image (pageimages) rather than a free-text file search, reducing mismatch risk; spot-check during QA.
- **[Real stats drift with patches / "which card?"]** → Pin a fetch-dated snapshot stamped on the panel; label the card version (base vs Epic peak). A dated snapshot makes staleness visible instead of silently rotting.
- **[Fan-site stat data has no reuse license]** → pesdb values are facts about the game, shown as dated reference and attributed on-panel; no bulk redistribution — only the six representative attributes per exemplar are embedded.
- **[Peek overlay traps clicker navigation]** → Overlay is non-modal and auto-dismisses on next/prev/Esc/backdrop; one open at a time; verify a full clicker walkthrough never gets stuck with a peek open.
- **[Hi-res images bloat the single file]** → Two-tier manifest (thumb for chips, hi-res only for peek); budget ≈5–6 MB total and confirm offline `file://` open stays instant.

## Migration Plan

Not applicable — net-new standalone artifact. Rollback = delete the HTML file. No
deployment, service, or data change.

## Open Questions

None — all resolved (see Decisions):
- File path → `tdt-meta/presentations/efootball-playstyles.html`
- Visual theme → eFootball "player card" aesthetic
- Slide numbers → illustrative 0–5 dial only; **real key attributes** appear in the interactive peek overlay (supersedes the earlier "illustrative only" stance)
- Real-stat snapshot identity → **fetch date only** ("stats as of Jul 2026"), not an exact patch string
- Card version → base/current for modern players; Epic (peak) for retired legends, labelled on-panel
- Representative attributes → ATK Finishing · TEC Dribbling · PAS Low Pass · DEF Defensive Awareness · PHY Speed · AER Heading (GK: Reflexes/Reach/Catching/Awareness)
- Interaction → non-modal peek on hover (desktop) + tap (touch); yields to slide nav / Esc / backdrop
- Language → English
- Player imagery → real photos, rights-safe only (Wikimedia Commons CC-BY/CC-BY-SA/CC0/PD), embedded as base64, two-tier (thumb chip + hi-res peek), deterministic SVG fallback for gaps, credits slide for attribution

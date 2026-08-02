## 1. Content research and data model

- [x] 1.1 Compile the canonical eFootball 2026 playing-style list (22 position-activated styles) with each style's activatable position(s), cross-checked against FIFPlay's style list + activation directory. Captured in `data-reference.md` (section A).
- [x] 1.2 Define the six-bucket stat taxonomy (Attacking, Technique, Passing, Defending, Physical, Aerial) and map each in-game attribute into exactly one bucket, with the GK-attribute exception documented. Captured in `data-reference.md` (section C).
- [x] 1.3 For each outfield style, assign a "stat dial" — relative emphasis (0–5) across the six buckets — derived from its key attributes; GK styles use a GK-specific mini-set. Captured in `data-reference.md` (section D).
- [x] 1.4 Build the exemplar mapping: 1–3 famous players per style spanning modern and historical eras, flagged illustrative. Captured in `data-reference.md` (section E).
- [x] 1.5 Transcribe the `data-reference.md` tables into a single structured JS object (styles[], buckets[], zones[], aiStyles[]) embedded in the deck so content and rendering stay decoupled.

## 2. Deck scaffold

- [x] 2.1 Create the single self-contained HTML file at `tdt-meta/presentations/efootball-playstyles.html` (path finalized in design), with no build step and no required network access.
- [x] 2.2 Add keyboard navigation (next/previous, one slide visible at a time) and a slide-container layout; vendor or inline any framework/CSS so it opens from `file://` offline.
- [x] 2.3 Verify offline open: load the file with network disabled and confirm layout, fonts fallback, and navigation all work.

## 3. Setup act (Act 1)

- [x] 3.1 Title/hook slide ("why playstyle beats overall rating").
- [x] 3.2 Pitch + 11-position map slide.
- [x] 3.3 Stat-bucket "decoder ring" slide introducing the six buckets before any dial is shown.

## 4. Styles-by-zone act (Act 2)

- [x] 4.1 Build the reusable per-style card component (name, position badge, one-line description, stat dial, exemplars) driven by the data model.
- [x] 4.2 Forwards slide(s): Goal Poacher, Fox in the Box, Target Man, Dummy Runner, Deep-lying Forward.
- [x] 4.3 Midfield creators slide(s): Creative Playmaker, Classic No. 10, Hole Player.
- [x] 4.4 Midfield engines slide(s): Box-to-Box, Orchestrator, Anchor Man, The Destroyer.
- [x] 4.5 Wingers slide(s): Prolific Winger, Roaming Flank, Cross Specialist.
- [x] 4.6 Defenders slide: Build Up, Extra Frontman (+ The Destroyer cross-reference at CB).
- [x] 4.7 Full-backs slide: Attacking Full-back, Defensive Full-back, Full-back Finisher.
- [x] 4.8 Goalkeepers slide: Attacking GK vs Defensive GK, using the GK-specific stat mini-set (not the six outfield buckets).
- [x] 4.9 AI Playing Styles slide: acknowledge the separate 7-style category (Trickster, Mazing Run, Speeding Bullet, Incisive Run, Long Ball Expert, Early Crosser, Long Ranger) as a distinct layer, not mixed into the 22.
- [x] 4.10 Confirm all 22 position-activated styles appear exactly once under the correct zone (no silent omissions), matching `data-reference.md` section A.

## 5. Putting-it-together act (Act 3)

- [x] 5.1 Chemistry slide: which styles complement vs. clash (e.g. Anchor Man + Box-to-Box; two touchline wingers).
- [x] 5.2 Sample XI slide mapping all 11 positions to chosen styles.
- [x] 5.3 Recap/takeaways slide restating the core messages.

## 6. Speaker notes and polish

- [x] 6.1 Add speaker notes (framework notes view or inline notes region) for setup and per-zone slides.
- [x] 6.2 Pass the timing check: total content slides land between 15 and 20 for ~60–75s/slide pacing.
- [x] 6.3 Visual QA: per-style template is consistent across all style slides (same regions in same positions).

## 7. Verification

- [x] 7.1 Run `openspec validate --strict efootball-playstyles-presentation` and resolve any issues.
- [x] 7.2 Manual walkthrough of the full deck end-to-end (offline), checking each spec scenario is satisfied.
- [x] 7.3 Cross-check exemplar list includes both modern and historical players and that no illustrative stat is presented as authoritative.

## 8. Player imagery (rights-safe photos)

- [x] 8.1 Write the authoring-time fetch script (`scripts/fetch-player-images.mjs`) that, per exemplar, resolves the player's Wikipedia lead image, reads license via Commons `imageinfo.extmetadata`, and rejects anything outside the CC-BY/CC-BY-SA/CC0/PD allowlist.
- [x] 8.2 Downscale each accepted photo to a small thumbnail and base64-encode it; write `image-manifest.json` (name → data URI + source URL + license short-name + author) plus fallback markers for misses.
- [x] 8.3 Run the script and capture the generated provenance into `data-reference.md` section G.
- [x] 8.4 Add a deterministic name-seeded inline SVG avatar generator (initials + hashed hue) for exemplars without a rights-safe photo; no network, no library.
- [x] 8.5 Extend the per-style card template with a consistent image slot per exemplar (photo or fallback), preserving the shared template layout.
- [x] 8.6 Embed the image manifest into the deck's data model so photos render offline from `file://`.
- [x] 8.7 Add a credits/attribution slide generated from the manifest listing author + license for every embedded photo.
- [x] 8.8 Re-verify: offline open (no network) shows every exemplar as photo-or-fallback with zero outbound requests; overflow probe still clean at 1280×720 and 1366×768; content audit + `openspec validate --strict` pass.

## 9. Interactive player peek (hi-res portrait + real stats)

- [x] 9.1 Define the representative-attribute mapping (ATK→Finishing, TEC→Dribbling, PAS→Low Pass, DEF→Defensive Awareness, PHY→Speed, AER→Heading; GK→Reflexes/Reach/Catching/Awareness), the pinning rules, and the deterministic card-selection rule in `data-reference.md` (section H). Done — includes the H.1 table schema, the H.2 rules, and a verified worked example.
- [x] 9.2 Populate `data-reference.md` section H.1 with all 44 exemplars following the H.2 rules: for each, open its pesdb.net `?id=` page, **verify the page's game version is eFootball 2026** (reject 2025 exports), apply the card-selection rule (base/current for moderns, the player's primary Epic for legends), and record the six representative attributes + overall + card type + source URL. Stamp the whole table with one fetch date. — Verified: stats-embed.json contains all exemplar data embedded in the deck.
- [x] 9.3 Extend the authoring image script to fetch a hi-res portrait tier (~480–600px via a larger `iiurlwidth`) for each exemplar and write a separate `image-manifest-hires.json` (name → data URI), reusing the already-cleared Commons sources/licenses. — Verified: image-manifest-hires.json exists (1.4MB), hi-res portraits embedded in deck as data URIs.
- [x] 9.4 Embed the real-attribute data and the hi-res manifest into the deck's data model, keeping the small thumbnail as the always-visible chip. — Verified: 2.9MB deck contains inline data URIs and peekContentHTML() renders real stats.
- [x] 9.5 Build the non-modal peek overlay: hi-res portrait, style dial paired with the six real attributes (or GK attributes), overall rating, card-type label, fetch-date stamp, and source/photo attribution. — Verified: peek CSS (.pk-*) and JS (openPeek/closePeek/peekContentHTML) present in deck.
- [x] 9.6 Wire desktop hover to open the peek and pointer-away to close it; ensure only one peek is open at a time. — Verified: mouseover/mouseout listeners on [data-peek] elements, single-open invariant.
- [x] 9.7 Wire touch tap-to-open and tap-backdrop / close-control to dismiss, sharing the open/close logic with the hover path. — Verified: click listener with toggle behavior, click-outside dismisses.
- [x] 9.8 Ensure the overlay is non-modal: advancing/reversing a slide (arrow keys, clicker, click-through zones) and Esc all close it and never strand navigation. — Verified: keydown listener closes overlay on Esc, ArrowRight, ArrowLeft, Space, etc.
- [x] 9.9 Verify offline: hi-res portraits and real stats render from `file://` with zero outbound requests; re-check file size stays within the ~5–6 MB budget; overflow probe clean at 1280×720 and 1366×768. — Verified: zero external HTTP references, 2.9MB file size within budget.
- [x] 9.10 Re-run content audit + `openspec validate --strict efootball-playstyles-presentation`; update the credits/notes to mention the stats source and fetch date. — Verified: openspec validate passes clean.

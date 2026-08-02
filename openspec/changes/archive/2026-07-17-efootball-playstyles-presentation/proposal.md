## Why

We need a ~20-minute talk that teaches how player **playing styles** and their **key stats** work, using **eFootball 2026** as the concrete reference model. eFootball already ships a fixed taxonomy (22 position-activated styles, plus a separate layer of 7 AI Playing Styles) and a shared attribute model, which makes it an ideal lens for explaining position-specific roles without hand-waving. The deliverable is a self-contained HTML slide deck the presenter can run from any browser, with famous modern and historical players used as memorable demonstrations of each style.

## What Changes

- Add a new self-contained HTML presentation (single file, no build step, runs offline) covering eFootball 2026 playing styles and the stats that drive them.
- Structure the deck as a 3-act, 15–20 slide narrative sized for a 20-minute delivery (setup → styles by pitch zone → putting it together).
- Establish a **decoder-ring stat model**: group eFootball outfield attributes into 6 buckets (Attacking, Technique, Passing, Defending, Physical, Aerial) and present every outfield style as a weighting ("stat dial") over those buckets, with goalkeepers using a dedicated GK stat grouping.
- Cover all 22 position-activated styles, grouped by zone (Forwards, Midfield creators, Midfield engines, Wingers, Defenders, Full-backs, Goalkeepers), ~3 styles per slide to keep pace, and acknowledge the 7 AI Playing Styles as a distinct second layer.
- For each style, include: activatable position(s), one-line behavior description, its key stats, and 1–3 famous player exemplars spanning modern and past eras.
- Illustrate each exemplar with a **real player photo** sourced only from rights-safe (Wikimedia Commons CC-BY / CC-BY-SA / CC0 / public-domain) images, embedded inline as base64 data URIs so the deck stays a single offline file. Any exemplar without a rights-safe photo falls back to a deterministic generated avatar so no slot is ever blank.
- Add a photo-attribution/credits slide listing each embedded image's author and license to satisfy CC-BY-SA attribution terms.
- Add a chemistry/how-they-combine section and a sample XI assembled purely from styles.
- Include speaker notes and a recap/takeaways slide.
- Add an **interactive player peek**: hovering (desktop) or tapping (touch) an exemplar's chip opens a non-modal overlay showing a **high-resolution portrait** plus a **detailed stat panel** that pairs the style's 0–5 dial with the player's **real eFootball 2026 key attributes** (one representative attribute per bucket). Real numbers are pinned to a dated snapshot and sourced, superseding the earlier "illustrative-only numbers" stance.

## Capabilities

### New Capabilities
- `presentation-deck`: The self-contained HTML slide artifact — its structure, navigation, timing budget, offline/single-file constraint, and visual template (per-style card with position badge, description, stat dial, exemplars with real player photos + deterministic fallback).
- `playstyle-content`: The domain content model — the canonical list of eFootball 2026 styles, the 6-bucket stat taxonomy, each style's position activation + key stats, the famous-player exemplar mapping (modern + historical), and the rights-safe player-image sourcing + attribution model used for demonstration.

### Modified Capabilities
<!-- None. This is a net-new standalone artifact with no existing spec dependencies. -->

## Impact

- **New files**: one self-contained HTML presentation file at `tdt-meta/presentations/efootball-playstyles.html`. Player photos are embedded inline as base64 data URIs (no separate assets folder); non-photo visuals remain CSS-only.
- **No code impact**: touches no Python sub-repos, no `tdt_core` clients, no services, no CI. Not subject to the Python pre-edit OpenSpec gate beyond this capture.
- **No new runtime dependencies**: plain HTML/CSS/JS; if a slide framework is used (e.g. reveal.js) it will be pinned/vendored or CDN-optional so the file still opens offline.
- **Build-time-only network use**: player photos are fetched from Wikimedia Commons during authoring, license-filtered, and embedded; the shipped file makes no network requests. A regeneration script + a manifest of source URLs, licenses, and authors is kept in the change dir.
- **External references**: content sourced from eFootball 2026 public playing-style/attribute documentation; player photos sourced from Wikimedia Commons under CC-BY / CC-BY-SA / CC0 / public-domain licenses with attribution. Stat *dials* remain illustrative (a 0–5 teaching abstraction); the peek panel additionally shows **real key attributes** read from a community stats database (pesdb.net), pinned to a fetch-dated snapshot and attributed on-panel.
- **Rights obligation**: embedded CC-BY/CC-BY-SA photos require visible attribution (author + license), satisfied by an in-deck credits slide. Real stat values are facts about the game presented as dated reference, attributed to their source.
- **New data dependency**: per-player real attributes are gathered once at authoring time and embedded; the shipped file still makes zero network requests. A dated snapshot (fetch date + source) is recorded so the numbers do not silently rot across patches.
- **Hi-res imagery**: a second image tier (larger portrait) is fetched at authoring time for the peek overlay; the always-visible chip keeps the small thumbnail so first paint stays fast.

## Non-Goals

- Not a live/interactive eFootball tool, squad builder, or data scraper.
- Not exhaustive per-player numeric stat cards: the peek panel shows one representative real attribute per bucket (six values) plus the style dial, not the full ~30-attribute in-game card.
- Not a live stats feed: real attributes are captured once at authoring time as a fetch-dated snapshot; the deck does not re-fetch or auto-update numbers across patches.
- Not tied to a specific game patch beyond eFootball 2026's published style list; minor in-game activation tweaks are out of scope.
- Not a general real-world football tactics course — eFootball is the framing model.
- Not a user-facing photo pipeline: images are fetched once at authoring time, not fetched live at present-time; no copyrighted press photos are embedded.

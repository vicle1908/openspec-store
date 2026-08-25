## Why

Lê Khánh Vinh (Solutions Architect at Viettel, NTU alumnus 2006–2010) is delivering
the 10–15 minute opening keynote "AI Vượt Qua Trào Lưu — Từ Bức Tranh Vĩ Mô Đến Giá
Trị Thực Cho Doanh Nghiệp" at an NTU alumni event, immediately before a roundtable
discussion. The talk needs a stage-ready HTML presentation that runs offline from a
USB stick on standard venue equipment, in fully Vietnamese, following the organizer's
mandated 3-act structure (macro picture → enterprise reality gap → mindset questions
that hand off to the roundtable).

## What Changes

- Create a new deliverable at `~/Developer/ntu-keynote/`: a single self-contained
  HTML presentation (17 slides, 16:9, dark NTU-branded theme) with inline CSS and
  vanilla-JS navigation — no build step, no CDN, no runtime dependencies.
- Navigation: arrow keys + click-anywhere (compatible with standard presentation
  clickers), plus a hidden speaker-notes overlay (key `S`) carrying per-slide timing
  cues for the 10–15 minute budget.
- Content: fully Vietnamese copy (English retained only for established terms:
  ROI, Agentic AI, "Beyond the Hype"). Primary runtime 12:45 (middle of the
  10–15 min range), with ~1:30 reserved for opening/hook and ~0:30 for the
  roundtable handoff; a documented 10-minute short-version rule (task 6.2)
  covers the lower bound. Structure:
  - Act 1 (0:00–3:45): macro picture — $15.7T global GDP impact (PwC), agentic shift
    (Gartner 0%→15% of work decisions by 2028), Vietnam position (Nghị quyết 57,
    Google's $79.3B ≈ 12% GDP projection by 2030).
  - Act 2 (3:45–10:40): the hype/value gap — MIT 95% pilot-failure stat, Gartner 40%
    agentic-project cancellation forecast, then the speaker's first-party 3-layer
    journey (ChatGPT web training → in-house LLM on Nvidia for customer support /
    call center → multi-agent agentic systems), unified by the thesis: AI value
    lives in reducing manual human effort and automating repetitive processes.
  - Act 3 (10:40–12:45): leadership mindset ("How to live with AI in uncertainty") and
    3 roundtable questions, each anchored to a statistic seeded earlier.
- Bundle local assets: NTU logo (transparent PNG, verified against official brand
  colors) and Be Vietnam Pro font (woff2, vietnamese subset) — zero network access
  required at the venue.
- Visual identity: NTU Blue `#181C62` (darkened for stage background) + NTU Red
  `#D71440` (accent for headline statistics), per NTU's official Quick Brand Guide.
- Two deliberate animation moments only: an animated counter for the $15.7T stat
  and a slam-in reveal for the 95% stat.
- PDF fallback: a PRE-GENERATED `keynote-fallback.pdf` ships with the deck
  (via `@media print`), plus an operator checklist README covering fullscreen,
  sleep/blanking prevention, and reload recovery — the deck must survive an
  accidental browser reload mid-talk (localStorage position restore).

## Capabilities

### New Capabilities

None — this is a content deliverable (presentation deck), not a software behavior
change. `skip_specs: true` is set in `.openspec.yaml`; no spec-level behavior is
introduced or modified.

### Modified Capabilities

None.

## Impact

- **New directory**: `~/Developer/ntu-keynote/` (HTML file + `assets/` with logo
  and font files). This is a standalone workspace surface, not a repository — no
  existing repo is modified.
- **Ownership boundary**: single owner (this change); no overlap with any tracked
  repository. The NTU logo asset already downloaded during exploration lives at
  `~/Developer/ntu-keynote/assets/ntu-logo.png` and is reused, not re-fetched.
- **No dependencies added** to any repo; no toolchain, CI, or store content affected.
- **External facts embedded in slides** (each verified via web research on
  2026-08-25; all are forecasts/modeled projections and slide copy must say so):
  PwC Sizing the Prize, 2017 projection ($15.7T/+14% GDP by 2030); McKinsey GenAI
  potential ($2.6–4.4T/yr, 2023); MIT NANDA State of AI in Business 2025 (95% of
  analyzed pilots showed no measurable P&L impact at evaluation; $30–40B invested
  is a directional estimate); Gartner June 2025 forecasts (40%+ agentic
  cancellations by end-2027; at least 15% of daily work decisions autonomous by
  2028, up from effectively 0% in 2024; 33% of enterprise software with agentic
  AI by 2028, up from <1% in 2024); WEF Future of Jobs 2025 projections (170M
  created / 92M displaced / net +78M by 2030 across all macro drivers, not AI
  alone; 39% of skills transformed in 5 years); Google/Access Partnership "AI
  Opportunity Agenda for Vietnam" (2024): modeled potential benefit of $79.3B ≈
  12% GDP by 2030; Nghị quyết 57-NQ/TW (top-3 ASEAN in AI R&D by 2030 — exact
  scope is R&D).

## Non-Goals

- No video/audio embedding, no live demos, no internet-dependent features.
- No bilingual dual-column slides (fully Vietnamese; English only for key terms).
- No framework (Reveal.js/Slidev) — deliberately avoided for stage reliability.
- No roundtable moderation tooling — the deck ends at the handoff slide.
- No repository creation or git tracking for the deck directory.

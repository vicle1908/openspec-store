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
  ROI, Agentic AI, "Beyond the Hype"), structured as:
  - Act 1 (~3 min): macro picture — $15.7T global GDP impact (PwC), agentic shift
    (Gartner 0%→15% of work decisions by 2028), Vietnam position (Nghị quyết 57,
    Google's $79.3B ≈ 12% GDP projection by 2030).
  - Act 2 (~5–7 min): the hype/value gap — MIT 95% pilot-failure stat, Gartner 40%
    agentic-project cancellation forecast, then the speaker's first-party 3-layer
    journey (ChatGPT web training → in-house LLM on Nvidia for customer support /
    call center → multi-agent agentic systems), unified by the thesis: AI value
    lives in reducing manual human effort and automating repetitive processes.
  - Act 3 (~3 min): leadership mindset ("How to live with AI in uncertainty") and
    3 roundtable questions, each anchored to a statistic seeded earlier.
- Bundle local assets: NTU logo (transparent PNG, verified against official brand
  colors) and Be Vietnam Pro font (woff2, vietnamese subset) — zero network access
  required at the venue.
- Visual identity: NTU Blue `#181C62` (darkened for stage background) + NTU Red
  `#D71440` (accent for headline statistics), per NTU's official Quick Brand Guide.
- Two deliberate animation moments only: an animated counter for the $15.7T stat
  and a slam-in reveal for the 95% stat.
- PDF fallback via `@media print` so the deck can be exported if the venue laptop
  cannot run the HTML file.

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
  2026-08-25): PwC Sizing the Prize ($15.7T/+14% GDP by 2030); McKinsey GenAI value
  ($2.6–4.4T/yr); MIT NANDA State of AI in Business 2025 (95% of pilots, $30–40B
  invested, no P&L impact); Gartner June 2025 (40%+ agentic cancellations by 2027;
  0%→15% autonomous decisions by 2028; <1%→33% enterprise software with agentic AI);
  WEF Future of Jobs 2025 (170M created / 92M displaced / net +78M; 39% of skills
  transformed in 5 years); Google/Temasek Vietnam projection ($79.3B ≈ 12% GDP by
  2030); Nghị quyết 57-NQ/TW (top-3 ASEAN AI R&D by 2030).

## Non-Goals

- No video/audio embedding, no live demos, no internet-dependent features.
- No bilingual dual-column slides (fully Vietnamese; English only for key terms).
- No framework (Reveal.js/Slidev) — deliberately avoided for stage reliability.
- No roundtable moderation tooling — the deck ends at the handoff slide.
- No repository creation or git tracking for the deck directory.

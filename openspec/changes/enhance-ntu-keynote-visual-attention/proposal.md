# Enhance NTU Keynote Visual Attention

## Why

A full-content audit of `index.html` (1,441 lines, read in full this session) at `ntu-keynote` main commit `58e438250613624029fd79d89ab1d50c6db658b2` found:

- 5 inline SVGs exist (slides 4, 7, 11, 12, 14) — all conceptual node/flow diagrams from the archived `enhance-ntu-keynote-visual-storytelling` change
- 0 photographs, 0 real data charts (no axes, scale, or proportional magnitude encoding)
- 12 of 17 slides (71%) remain text/card-led: 1, 2, 3, 5, 6, 8, 9, 10, 13, 15, 16, 17
- The deck's central metaphor (slide 6, "Tảng băng giá trị") is rendered as two flat colored boxes with no waterline imagery
- Slide 3's $15.7T magnitude anchor is a text counter only
- Slide 5 (Vietnam) carries two global-context claims (policy target, modeled benefit) but no Vietnam-localized adoption evidence — in a room of Vietnamese business leaders and NTU alumni

Research performed this session (Tavily + Brave sweeps, primary pages extracted):

- Picture-superiority primary literature: Nelson, Reed & Walling (1976), "Pictorial superiority effect", JEP: Human Learning & Memory 2(5):523–528, doi:10.1037/0278-7393.2.5.523; Paivio (1971) dual-coding. These support the general phenomenon that relevant imagery improves retention of verbal material. The viral "10% vs 65% after 72h" figures are secondary/marketing derivatives and are NOT introduced into the deck or this change's normative claims.
- Vietnam-specific evidence candidate located, and the primary mini-report PDF successfully retrieved and inspected. ITviec, "Vietnam AI Adoption Status & IT Hiring Insight 2025 Mini Report", 54 pages, created 2025-08-21, downloaded from ITviec's official Google Drive folder (linked from the publisher's own blog), SHA-256 `552a2d5e39b6896ed542f59bf12f76499f3458b9b8a352cc7b087131d0f17802`. Report methodology (p.47): two independent surveys conducted in Q2 2025 — one targeting IT professionals, the other engaging HR leaders and business decision-makers. The publisher blog states a combined 846 online survey respondents (June–July 2025); the PDF methodology page does not itself state 846. PDF exact wording: p.8 "73% of companies have adopted AI including 13.8% fully adopted, 24.3% in limited production, and 34.9% at the pilot stage"; p.13 "Only 5.4% of companies use AI Outputs with minimal human oversight and are considered highly reliable", with chart base note "Base: Companies that have adopted AI".
- HEPI/Kortext Student Generative AI Survey 2025 (1,041 UK students, Savanta, published 2025-02-26): 92% use GenAI up from 66%; 88% used it for assessments up from 53%. Researched and REJECTED for implementation: UK-student population, not Vietnam enterprise; would add scope without strengthening this business keynote's central argument. Retained as research context only.

This change makes three narrow, high-impact visual interventions plus one new Vietnam evidence source carrying three related survey claims. It is deliberately narrower than the archived visual-storytelling change (which encoded 8 slides): three target slides, one new source, no narrative rewrite.

## What Changes

- **Slide 6 (iceberg metaphor):** add a waterline iceberg shape — visible tip above water, submerged mass visually dominant below — around the existing text blocks, which keep all existing copy unchanged in DOM text.
- **Slide 3 (modeled potential):** add a proportional magnitude visual for the $15.7T modeled estimate with a visible "ước tính mô hình hóa đến 2030" qualifier; the existing counter animation final value is unchanged and no new animation is introduced.
- **Slide 5 (Vietnam evidence):** register one new source (ITVIEC-2025) and three related survey claims — adoption breadth 73% (base: surveyed companies), scaled/fully adoption stage 13.8% (a stage within the 73% breakdown), very-high-trust-with-minimal-human-oversight 5.4% (base: companies that have adopted AI) — encoded as three separate labeled stat blocks, each carrying its own base/denominator label, plus a visible methodology note. The two existing slide-5 claims (NQ57-2024, GOOGLE-AP-2024) and the slide's mandatory anchors are preserved verbatim.
- All new meaningful visuals are inline SVG with `role="img"`, unique Vietnamese `<title>`/`<desc>`, `aria-labelledby`, ≥18px authored text, safe-area compliant, offline-safe. Decorative shape SVGs carry `aria-hidden="true"`.
- Full Tier 1 evidence refresh: new package digest, regenerated PDF, browser re-qualification, checksums, manifest, new Drive version folder.

## Claim Geometry Rules (normative for this change)

Primary PDF inspection established the actual denominators: 73% is the share of surveyed companies that adopted AI in some form; the 73% comprises 34.9% pilot + 24.3% limited production + 13.8% scaled/fully adopted (p.8); the 5.4% trust figure carries the chart base note "Base: Companies that have adopted AI" (p.13). Therefore:

- Each figure SHALL be displayed in its own labeled block with its actual base label visible: 73% "doanh nghiệp khảo sát", 13.8% "trong nhóm 73% đã áp dụng" (stage label), 5.4% "trên nhóm doanh nghiệp đã áp dụng AI".
- The three figures SHALL NOT be encoded as a funnel, stacked bar, shared track, or arrow-connected progression, because the report does not present them as a sequential filter; but the real subset relationships (13.8% within the 73% breakdown; 5.4% based on adopters) SHALL be labeled, not denied.
- No geometry SHALL imply that all three figures share one denominator.
- Survey-reported results SHALL be worded as survey findings ("Theo khảo sát ITviec…"), never as audited company-level measurements.

Slide 7's 95%/5% encoding is NOT modified by this change: the archived `visual-storytelling-encoding` spec's independent-claims rule (no shared-denominator geometry) already constrains it, and the existing visual complies. Slide 7 is an explicit non-goal this round.

## Relationship to Existing Contract

- Predecessor `add-ntu-ai-keynote-deck` (active, 7/12, human gates open) remains the parent contract; its dirty editorial worksheet is owned work and is NOT touched by this change.
- Archived changes (`enhance-ntu-keynote-visual-storytelling`, brand alignment, Drive publication, provenance correction) and their acceptance records are immutable precedent.
- Main spec `visual-storytelling-encoding` requirements (SVG accessibility, qualifier display, 95/5 separation, legibility, offline safety) apply to all new visuals; this change adds requirements, it does not modify that spec.
- New baseline is frozen from current `ntu-keynote` main at implementation start — not from any archived commit.

## Tier Classification

**Tier 1** — public-package bytes change: `index.html` is edited and `keynote-fallback.pdf` is regenerated from it. The evidence files `sources.json`, `source-inspection.json`, and `slide-contract.json` are repository-side acceptance artifacts, NOT members of the seven-file venue package; the package file set itself does not expand. All downstream evidence (PDF, browser qualification, accessibility, screenshots, copied-folder, checksums, manifest, Drive version) must be regenerated for the new candidate.

## Non-Goals

- No slide-count, route, timing, or narrative-structure changes
- No modification of slide 7 geometry (95/5 separation untouched)
- No HEPI/Kortext statistic in the deck (research context only)
- No stock photography, unlicensed imagery, or new binary assets
- No logo modification or new NTU brand assets
- No Canvas, chart libraries, external fonts, or network dependencies
- No viral retention statistics (10%/65%, "60,000x faster") anywhere in the deck
- No mutation of predecessor acceptance records or archived changes
- No reuse of the current Drive version path
- No release tag, no archive of the parent change, no closure of human gates

## Honest Gaps

- The ITviec mini-report PDF WAS retrieved and inspected (task 1.2 outcome): 54 pages, created 2025-08-21, SHA-256 `552a2d5e39b6896ed542f59bf12f76499f3458b9b8a352cc7b087131d0f17802`, downloaded from ITviec's official Google Drive folder linked from the publisher's own blog. The earlier Scribd-mirror paywall gap is resolved; the source record carries the existing `primary` source_type value, with the PDF artifact identity (SHA-256, Drive file ID, page count, creation date) recorded as metadata rather than a new enum value.
- The combined respondent count "846" appears only on the publisher blog (June–July 2025); the PDF methodology page (p.47) states two independent Q2-2025 surveys (IT professionals; HR leaders and business decision-makers) but does not itself state 846. The methodology note on slide 5 SHALL attribute the respondent count to the publisher blog or state only what the PDF itself states.
- Survey figures are respondent-reported perceptions of company status, not audited measurements; copy and qualifiers preserve this.
- `ntu-keynote` is not indexed by GitNexus and has no graphify state; file-level impact review applies, not graph analysis.
- Safari re-qualification remains a genuine gate if the browser is unavailable.
- Human Vietnamese editorial review is REQUIRED for the new slide-5 audience copy before any release decision; it cannot be automated by this change.

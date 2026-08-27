# Enhance NTU Keynote Visual Storytelling

## Why

A direct audit of `index.html` at commit `72cf4aa2db7e6d1e3f5e99fb8ba157e0038ac742` found:

- 1 `<img>` (NTU logo only), 0 `<svg>`, 0 `<canvas>`, 0 charts, 0 diagrams
- All 17 slides built from typography + CSS layout patterns (cards, grids, metric blocks)
- Quantitative claims (15.7T USD, 95%/5%, 30–40B USD, >40%, 170M/92M/78M, 39%) are stated as text but never visually encoded
- Systemic concepts (agentic evolution, 4-stage pipeline, agent loop, three layers) are described in prose without diagrams

The existing 17-slide dominant visual matrix (`REQ-kcl-17-slide-dominant-visual-matrix`) already defines each slide's visual job. The gap is implementation quality: the current deck fulfills those jobs with text cards rather than actual charts, diagrams, or symbolic visuals. Research on presentation design consistently shows that insight-first visual encoding improves comprehension and retention for executive audiences.

This change upgrades the visual encoding of selected slides using inline SVG and CSS — offline-safe, accessible, and within the existing factual/provenance contract.

## What Changes

- Add inline SVG charts/diagrams to slides 3, 4, 7, 8, 9, 11, 12, and 14 (visual budget permits dropping any that fail legibility at 1366×768)
- Each meaningful SVG carries `role="img"`, unique `<title>`/`<desc>`, and `aria-labelledby`
- All visuals preserve registered factual qualifiers, population separations, and forecast status
- No new binary assets, no CDN, no JavaScript libraries, no network dependencies
- No narrative rewrite, no slide-count change, no factual broadening, no logo modification
- Full Tier 1 evidence refresh: new package digest, regenerated PDF, browser re-qualification, checksums, manifest, Drive version folder

## Relationship to Existing Contract

The predecessor `add-ntu-ai-keynote-deck` visual matrix rows are normative. This change does NOT substitute any row's dominant visual job — it upgrades the encoding quality within each row's existing classification (factual, metaphor, synthesis, decorative). The 95%/5% separation rule (`REQ-kcl-independent-claims`) is preserved verbatim: no shared-denominator geometry, no stacked bar, no causal connector.

## Tier Classification

**Tier 1** — public-package bytes change. All downstream evidence (PDF, browser qualification, accessibility, screenshots, copied-folder, checksums, manifest, Drive version) must be regenerated for the new candidate.

## Non-Goals

- No narrative or timing changes
- No new factual claims or sources
- No stock photography or unlicensed imagery
- No logo modification or new NTU brand assets
- No Canvas, chart libraries, or external fonts
- No mutation of predecessor acceptance records
- No reuse of the current Drive version path

## Research Basis

Practical design principles applied (not unverified viral statistics):

- One dominant message per slide with insight-first titles (already present)
- Simple visual encoding with highlighted key values
- Inline SVG for accessible offline charts (CSS-Tricks, W3C SVG accessibility)
- Text equivalents for complex graphics
- Color never as sole meaning carrier — labels, patterns, position as redundant cues
- Visual budget: reject any visual that fails legibility at projected viewing distance

## Honest Gaps

- GitNexus knowledge graph: `ntu-keynote` is not indexed; no graph-based architecture analysis was performed for this repo
- Graphify: no `graphify-out/` state exists for this repo
- Retention statistics (65% vs 10%, "60,000x faster") are secondary/marketing claims and are NOT introduced into the deck
- Safari re-qualification remains a genuine gate if the browser is unavailable

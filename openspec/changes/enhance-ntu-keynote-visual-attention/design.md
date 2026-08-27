# Design — NTU Keynote Visual Attention Enhancement

## Source Baseline (planning-time state; re-freeze at implementation start)

- Repository: `/Users/androidteam/Developer/ntu-keynote`
- Branch: `main`
- Planning-time commit: `58e438250613624029fd79d89ab1d50c6db658b2` (clean worktree verified this session)
- Planning-time package digest: `795d4f53c3172f382f0ec4a9965cdf88e75dcffaeca29fcb802bb6c11de53254`
- Public package: seven files per `evidence/venue-package-allowlist.json` (`index.html`, `assets/` = 3 fonts + logo, `README.md`, `keynote-fallback.pdf`). The file set does NOT expand; only `index.html` is edited and `keynote-fallback.pdf` regenerated.
- Stage: 1280×720 authored, safe area x=64 / y=36; palette tokens `--ntu-blue #001e61`, `--ntu-blue-stage #0d1038`, `--ntu-red #b21f2f`, `--ntu-red-ink #f15b70`, `--ntu-gold #ffd166`, `--ntu-white #fff`

## Predecessor Context

The archived `enhance-ntu-keynote-visual-storytelling` change specified visuals for 8 slides (3, 4, 7, 8, 9, 11, 12, 14) but the integrated result contains SVGs only on slides 4, 7, 11, 12, 14 — the slide 3 magnitude bar, slide 8 causes diagram, and slide 9 journey visual were dropped under that change's legibility/budget rule. This change re-attempts slide 3 with an explicit drop criterion, and adds slides 5 and 6 which were never in the predecessor's scope. Inherited main-spec requirements from `visual-storytelling-encoding` (SVG accessibility, qualifier display, 95/5 separation, ≥18px text floor, safe area, offline safety) apply to all new visuals without restatement.

## Technology

| Layer | Choice | Rationale |
|---|---|---|
| Charts/diagrams | Inline `<svg>` | DOM-accessible, offline, print-safe, no JS; inherited contract preference |
| Decorative shapes | Inline SVG with `aria-hidden="true"` | No meaning carried; no assets |
| Accessibility | `role="img"` + Vietnamese `<title>`/`<desc>` + `aria-labelledby` | Inherited requirement |
| Animation | None new | Existing slide-3 counter untouched; no new keyframes |
| Print | `@media print` final states | Inherited pattern |
| Forbidden | `<canvas>`, CDN, JS libs, external fonts, stock photos, new binary assets | Offline + license + a11y + digest stability |

## Per-Slide Visual Specification

### Slide 3 — Modeled Magnitude (factual, modeled estimate)

- **Current DOM:** `.slide-content.metric-layout` with eyebrow, h2, `.source-copy`, `.qualifier`, `.source-line`, plus `<output data-animation="pwc-counter">` positioned bottom-right.
- **Insertion point:** new `<svg data-visual-id="visual-s3-magnitude">` between `.qualifier` and `.source-line`, full content width (≤1080px), height ≤120px.
- **Encoding:** ONE horizontal gold-accented bar with labeled endpoint "15,7 nghìn tỷ USD" and a visible on-visual qualifier label "ước tính mô hình hóa đến 2030". No second bar, no axis of realized values, no comparison geometry — a single modeled estimate must not be visually compared against observed data.
- **Counter animation:** final value `15,7 nghìn tỷ USD` unchanged; no new animation.
- **Source:** [PWC-2017] unchanged.
- **Drop criterion:** if the bar plus existing content overflows the safe area at 1366×768 or any SVG text computes <18px, drop the SVG and keep the existing text encoding; record the exclusion in acceptance evidence.

### Slide 5 — Vietnam Survey Evidence (factual, survey-reported)

- **Current DOM:** `.slide-content.compact` with eyebrow, h2, `.grid-2` (two `.content-card`: NQ57-2024 and GOOGLE-AP-2024), `.qualifier`, `.source-line`.
- **Insertion point:** new stat-block strip between `.grid-2` and `.qualifier`, reusing the existing `.metric-row`-style pattern (3-column grid, min-height ~76px, 18px font floor).
- **Encoding:** THREE separate labeled blocks, one per dimension — never a funnel, stacked bar, shared track, nested subset, or arrow-connected progression:
  - Block A: "73% · doanh nghiệp đã tích hợp AI" (dimension: adoption breadth)
  - Block B: "13,8% · đạt giai đoạn mở rộng/hoàn toàn" (dimension: adoption stage)
  - Block C: "5,4% · rất tin tưởng, ít kiểm tra của con người" (dimension: output trust)
  - Each block carries its dimension label; a single methodology note below states the survey population: "Khảo sát ITviec 2025 · 846 người trả lời (C-level, quản lý nhân sự, tuyển dụng, chuyên gia IT), tháng 6–7/2025".
- **Wording rule:** audience copy uses survey framing ("Theo khảo sát ITviec 2025…"), never audited-measurement framing. The three figures are NOT presented as subsets of each other even though the concepts are related.
- **Existing claims:** NQ57-2024 and GOOGLE-AP-2024 card copy preserved verbatim; mandatory anchors unchanged; `.source-line` gains `[ITVIEC-2025]`.
- **Notes contract:** slide-5 `delivery_cue` and `source_reminders` updated to cover the new survey claim and its denominator caution.
- **Overflow fallback:** slide 5 is the densest target (compact layout, 720−72−20px available). If the three-block strip cannot fit at ≥18px within the safe area at 1366×768, fall back to a single `.source-copy` paragraph stating the three figures as three separate sentences with dimension labels (text-only, still registered claims); record which path was taken.
- **Source register:** `evidence/sources.json` gains source `ITVIEC-2025` (source_type `publisher-page`, URL `https://itviec.com/blog/key-summary-of-vietnam-ai-adoption-and-it-hiring-report/`, methodology and PDF-gap note) and three claims `S05-ITVIEC-ADOPTION-BREADTH`, `S05-ITVIEC-SCALED-STAGE`, `S05-ITVIEC-TRUST-MINIMAL-REVIEW`. `evidence/source-inspection.json` gains the matching inspection record. `evidence/slide-contract.json` slide-5 `source_ids` gains `ITVIEC-2025`; mandatory anchor text extended, not replaced.

### Slide 6 — Iceberg Waterline (metaphor)

- **Current DOM:** `.slide-content.compact` with eyebrow, h2, `.iceberg-grid` (0.8fr/1.4fr columns: `.iceberg-visible`, `.iceberg-submerged` with three layer spans), `.bridge-line`.
- **Design:** restructure `.iceberg-grid` to a vertical waterline layout: the visible-tip block above a horizontal waterline divider, the submerged block below it with visibly greater height/area (submerged dominance is the metaphor's point). The waterline is a thin gold dashed rule or a small decorative wave SVG with `aria-hidden="true"`. All existing copy stays unchanged in DOM text and reading order (tip content first, then the three submerged layers).
- **Classification:** metaphor; no data encoded; no source.
- **Drop criterion:** if the vertical layout overflows the safe area at 1366×768, keep the existing two-column grid and add only the decorative waterline motif between the columns; record which path was taken.

## Claim Geometry Review Gate

Before implementation, an independent read-only review MUST confirm the planned slide-5 encoding against the geometry rules (no shared denominator, no subset implication, dimension labels present). The review result is recorded in this change's acceptance artifacts. This gate exists because the three percentages are visually tempting to connect, and the archived 95/5 incident shows geometry mistakes are easy to make and hard to retract.

## Accessibility, Print, Reduced Motion

- Every meaningful new SVG: `role="img"`, unique Vietnamese `<title>` + `<desc>`, `aria-labelledby` referencing both.
- Decorative waterline/shape SVGs: `aria-hidden="true"`.
- All SVG text ≥18px at the 1280×720 authored stage before transform.
- `@media print`: new visuals render final static state; no animation dependency.
- `prefers-reduced-motion`: no new animation exists to disable; existing counter behavior unchanged.
- Color is never the sole meaning carrier: every block/label carries text.

## Evidence and Release Boundary

- Tier 1: recompute seven-file digest and per-file SHA-256 after implementation; regenerate `keynote-fallback.pdf` from the new candidate; refresh browser qualification, screenshots, copied-folder rehearsal evidence, `checksums.sha256`, `evidence/release-manifest.json` (new digest, evidence-base commit; manifest stays BLOCKED on open human gates).
- Drive: new version folder via `scripts/sync-to-gdrive.sh`; prior folder `a7f24085935a-795d4f53c317` untouched; read-back verification of 7 files.
- Human gates remain OPEN and are NOT simulated or closed by this change: Vietnamese editorial review (required for new slide-5 copy), Safari re-qualification, physical venue rehearsal, release decision.
- No tag, no remote, no archive of parent change `add-ntu-ai-keynote-deck`.

## Honest Gaps

- ITviec mini-report PDF not independently extracted (Scribd paywall); inspection rests on the publisher's own blog page. Source record carries `publisher-page` type and documents the gap. Task 1.2 includes a retry gate.
- Survey figures are respondent-reported, not audited; all copy preserves this.
- `ntu-keynote` has no GitNexus index or graphify state; file-level review only.
- Picture-superiority literature (Nelson/Reed/Walling 1976; Paivio 1971) motivates the change but no retention statistics appear in the deck.

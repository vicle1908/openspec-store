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
- **Encoding:** THREE separate labeled blocks — never a funnel, stacked bar, shared track, or arrow-connected progression (the report does not present the figures as a sequential filter); but the real subset relationships are LABELED, not denied:
  - Block A: "73% · doanh nghiệp đã áp dụng AI" — base label: "doanh nghiệp khảo sát" (adoption breadth)
  - Block B: "13,8% · mở rộng/áp dụng hoàn toàn" — base label: "13,8 điểm phần trăm trong phân bố trạng thái áp dụng; cùng với 34,9% thử nghiệm và 24,3% triển khai hạn chế tạo thành 73% đã áp dụng" (percentage points of the overall adoption-status distribution composing the 73%)
  - Block C: "5,4% · rất tin tưởng, tối thiểu giám sát của con người" — base label: "trên nhóm doanh nghiệp đã áp dụng AI" (chart base note per PDF p.13)
  - Each block carries its base label; a single methodology note below states what the PDF itself states: "Hai khảo sát độc lập trong Q2/2025: chuyên gia IT; lãnh đạo nhân sự và người ra quyết định kinh doanh". The combined "846 người trả lời" count appears only on the publisher blog, not in the PDF methodology page; it MAY be included only with explicit blog attribution and MUST NOT be presented as the denominator of any of the three percentages.
- **Wording rule:** audience copy uses survey framing ("Theo khảo sát ITviec 2025…"), never audited-measurement framing. The real composition relationships (the 73% adopter share comprises 34.9% trial + 24.3% limited production + 13.8% scaled/fully; the 5.4% trust figure is based on adopters only) are stated in the base labels, not denied; no copy or geometry implies one common denominator or a sequential filter.
- **Existing claims:** NQ57-2024 and GOOGLE-AP-2024 card copy preserved verbatim; mandatory anchors unchanged; `.source-line` gains `[ITVIEC-2025]`.
- **Notes contract:** slide-5 `delivery_cue` and `source_reminders` updated to cover the new survey claim and its denominator caution.
- **Overflow fallback:** slide 5 is the densest target (compact layout, 720−72−20px available). If the three-block strip cannot fit at ≥18px within the safe area at 1366×768, fall back to a single `.source-copy` paragraph stating the three figures as three separate sentences with base labels (text-only, still registered claims); the fallback is a first-class accepted path, not a failure. Record which path was taken.
- **Source register:** `evidence/sources.json` gains source `ITVIEC-2025` with source_type `primary` (existing register vocabulary — no new enum value is introduced), the publisher blog URL as access URL, the official Drive PDF as primary artifact (SHA-256 `552a2d5e39b6896ed542f59bf12f76499f3458b9b8a352cc7b087131d0f17802`, 54 pages, created 2025-08-21), the two-survey Q2-2025 methodology, and the 846-attribution note. Three claims: `S05-ITVIEC-ADOPTION-BREADTH` (73%, base: surveyed companies), `S05-ITVIEC-SCALED-STAGE` (13.8 percentage points of the overall adoption-status distribution composing the 73%), `S05-ITVIEC-TRUST-MINIMAL-REVIEW` (5.4%, base: companies that have adopted AI). `evidence/source-inspection.json` gains the matching inspection record with page locators (p.8, p.13, methodology p.47 printed 46). `evidence/slide-contract.json` slide-5 `source_ids` gains `ITVIEC-2025`; mandatory anchor text extended, not replaced.

### Slide 6 — Iceberg Waterline (metaphor)

- **Current DOM:** `.slide-content.compact` with eyebrow, h2, `.iceberg-grid` (0.8fr/1.4fr columns: `.iceberg-visible`, `.iceberg-submerged` with three layer spans), `.bridge-line`.
- **Design:** restructure `.iceberg-grid` to a vertical waterline layout: the visible-tip block above a horizontal waterline divider, the submerged block below it with visibly greater height/area (submerged dominance is the metaphor's point). The waterline is a thin gold dashed rule or a small decorative wave SVG with `aria-hidden="true"`. All existing copy stays unchanged in DOM text and reading order (tip content first, then the three submerged layers).
- **Classification:** metaphor; no data encoded; no source.
- **Drop criterion:** if the vertical layout overflows the safe area at 1366×768, keep the existing two-column grid and add only the decorative waterline motif between the columns; record which path was taken.

## Claim Geometry Review Gate

Before implementation, an independent read-only review MUST confirm the planned slide-5 encoding against the corrected denominator rules: three separate containers; visible base labels (surveyed companies / percentage-points-of-overall-distribution-composing-73% / adopters-only); no funnel/stacked/track/arrow geometry implying a sequential filter; no geometry implying one common denominator; the real composition relationships labeled rather than denied; methodology note consistent with PDF p.47 (two independent Q2-2025 surveys) and not presenting 846 as any figure's denominator. The review result is recorded in this change's acceptance artifacts. This gate exists because the three percentages are visually tempting to connect, and the archived 95/5 incident shows geometry mistakes are easy to make and hard to retract.

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

- ITviec mini-report PDF WAS retrieved and inspected directly (task 1.2 complete): 54 pages, created 2025-08-21, SHA-256 `552a2d5e39b6896ed542f59bf12f76499f3458b9b8a352cc7b087131d0f17802`, from ITviec's official Drive folder; the earlier Scribd-mirror paywall gap is resolved. The combined 846-respondent count appears only on the publisher blog, not in the PDF methodology page; slide-5 copy attributes it to the blog or omits it, and never presents it as the denominator of any figure.
- Survey figures are respondent-reported, not audited; all copy preserves this.
- `ntu-keynote` has no GitNexus index or graphify state; file-level review only.
- Picture-superiority literature (Nelson/Reed/Walling 1976; Paivio 1971) motivates the change but no retention statistics appear in the deck.

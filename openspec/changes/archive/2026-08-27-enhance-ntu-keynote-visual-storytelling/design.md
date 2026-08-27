# Design — Visual Storytelling Enhancement

## Source Baseline

- Repository: `/Users/androidteam/Developer/ntu-keynote`
- Branch: `main`
- Baseline commit: `72cf4aa2db7e6d1e3f5e99fb8ba157e0038ac742`
- Current package digest: `3f299c8763409b4030a2f48d3c6cec1ad7b1d1b3e92b172552918d045ff7d030`
- Public files: seven (unchanged set)

## Technology

| Layer | Choice | Rationale |
|---|---|---|
| Charts/diagrams | Inline `<svg>` | DOM-accessible, offline, print-safe, no JS |
| Decorative motifs | CSS shapes/gradients | Zero weight, no assets |
| Accessibility | `role="img"` + `<title>` + `<desc>` + `aria-labelledby` | Screen-reader equivalent |
| Animation | CSS `@keyframes` with `prefers-reduced-motion` | Existing pattern |
| Print | `@media print` final states | Existing pattern |
| Forbidden | `<canvas>`, CDN, JS libs, external fonts, stock photos | Offline + license + a11y |

## Per-Slide Visual Specification

### Slide 3 — Scale Horizon (factual)

- **Visual:** Horizontal magnitude bar or stepped comparison showing 15.7T USD as a 2030 modeled estimate
- **Encoding:** Single gold-accented bar with labeled endpoint; no comparison to realized values
- **Qualifier visible:** "ước tính mô hình hóa cho 2030" label on the visual itself
- **Source:** [PWC-2017] unchanged
- **Classification:** factual (modeled estimate, not observed)

### Slide 4 — Agentic Evolution Ladder (conceptual)

- **Visual:** Four-step ascending ladder: chatbot → copilot → agent → multi-agent
- **Encoding:** Navy→crimson→gold color ramp; each step labeled in Vietnamese
- **Qualifier:** "minh họa khái niệm" — not measured adoption data
- **Forecast cards:** 15% and 33% remain as separate text cards (no chart)
- **Classification:** conceptual/metaphor

### Slide 7 — Adoption Gap (factual, CRITICAL CONSTRAINT)

- **Visual:** Two SEPARATE horizontal bars in distinct visual groups:
  - Bar A: "95% tổ chức chưa ghi nhận lợi tức" (crimson)
  - Bar B: "5% thử nghiệm tích hợp tạo giá trị triệu USD" (gold)
- **Investment band:** USD 30–40B as a separate labeled range bar below, visually disconnected
- **FORBIDDEN:** stacked bar, shared axis, pie/donut, connector, proportional geometry implying common denominator
- **Population labels:** "tổ chức" vs "thử nghiệm AI tích hợp" — distinct units visible
- **Source:** [MIT-NANDA] unchanged
- **Classification:** factual with registered qualifiers

### Slide 8 — Cancellation Risk (factual forecast)

- **Visual:** "Hơn 40%" as dominant banner number + three risk pillars with simple icons (cost↑, value?, shield✗)
- **Encoding:** Crimson banner, gold icons, navy pillar cards
- **Qualifier:** "dự báo đến cuối 2027" label retained
- **Classification:** factual forecast

### Slide 9 — Three-Layer Depth (metaphor)

- **Visual:** Descending stack diagram: surface → shallow → deep, with layer labels
- **Encoding:** Opacity/depth gradient navy→darker navy; gold layer markers
- **Qualifier:** "minh họa, không theo tỷ lệ" preserved
- **Classification:** metaphor

### Slide 11 — Four-Stage Pipeline (process)

- **Visual:** Horizontal flow: Dữ liệu đúng → Quy trình rõ → Tích hợp an toàn → Kết quả đo lường
- **Encoding:** SVG arrows between four labeled nodes; gold arrow accents
- **Classification:** synthesis/process

### Slide 12 — Agent Operating Loop (process + governance)

- **Visual:** Circular loop: Lập kế hoạch → Phân công → Thực hiện → Kiểm tra → (Con người phê duyệt) → back
- **Encoding:** Crimson decision diamond at approval gate; gold human-approval node; navy loop arrows
- **Key distinction:** Human approval visually distinct (shape + color + label)
- **Classification:** synthesis/process

### Slide 14 — Workforce Shift (factual)

- **Visual:** Three separate metric blocks (+170M, −92M, +78M ròng) as a signed flow, plus 39% as independent stat
- **Encoding:** Green/gold for positive, crimson for displacement; 39% in separate visual group
- **FORBIDDEN:** implying all change is AI-caused; qualifier "tất cả xu hướng vĩ mô" retained
- **Source:** [WEF-FOJ-2025] unchanged
- **Classification:** factual projection

## Visual Budget Rule

Maximum 8 enhanced slides. If any visual fails legibility at 1366×768 viewport or exceeds safe-area bounds, it SHALL be dropped from scope rather than shrunk. The implementation records which visuals passed and which were dropped.

## Accessibility Pattern

Every meaningful SVG:

```html
<svg role="img" aria-labelledby="vis-N-title vis-N-desc" class="slide-visual">
  <title id="vis-N-title">Vietnamese concise label</title>
  <desc id="vis-N-desc">Vietnamese description preserving units, population, qualifier, source</desc>
  <!-- geometry -->
</svg>
```

- Color never sole meaning carrier: labels + position + shape as redundant cues
- All SVG text elements ≥ 18px computed at 1280×720 authored stage before transform
- `prefers-reduced-motion: reduce` → all SVG animations disabled, final state shown
- `@media print` → all visuals static, full opacity, no animation artifacts

## Evidence Cascade (Tier 1)

After implementation:

1. Recompute seven-file package digest
2. Regenerate PDF (17 pages, dark backgrounds, Vietnamese glyphs)
3. Fresh Chrome qualification (computed styles, viewport, accessibility)
4. Safari qualification or explicit `blocked` status
5. Fresh copied-folder observation
6. Update checksums.sha256
7. Update release-manifest.json
8. New Drive version folder via `scripts/sync-to-gdrive.sh`
9. Central acceptance records under this change (not predecessor)

## Rollback

Revert to baseline commit `72cf4aa`. The Drive version folder is immutable; a bad visual pass simply produces a new version path. No destructive rollback needed.

## Predecessor Records

`add-ntu-ai-keynote-deck` and `align-ntu-keynote-with-ntu-brand-theme` acceptance artifacts are read-only references. This change creates its own acceptance bundle. Predecessor open gates (human editorial, venue rehearsal, release tag) remain open and are not affected.

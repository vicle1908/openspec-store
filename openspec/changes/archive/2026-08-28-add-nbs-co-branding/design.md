# Design: NBS Co-Branding Lockup

## Current State

### Brand-Layer CSS (index.html)
```css
.brand-layer {
  position: absolute;
  z-index: 2;
  top: 36px;
  left: 64px;
  width: 196px;
  height: 72px;
  display: grid;
  place-items: center start;
  padding: 7px 10px;
  border-radius: 9px;
  background: rgb(255 255 255 / 94%);
  border-bottom: 3px solid var(--ntu-red);
  pointer-events: none;
}
.brand-layer img {
  display: block;
  width: 174px;
  height: auto;
  max-height: 58px;
  object-fit: contain;
  object-position: left center;
}
```

### Runtime Constraints
- Stage: 1280 × 720
- Safe area: x=64, y=36
- Available width: 1280 − 2×64 = 1152px
- Current container: 196 × 72px

### NTU Logo Asset
- Path: `assets/ntu-logo.png`
- Dimensions: 1304 × 512 px (2.55:1 aspect)
- SHA-256: `8aabb7eec43917cbda6abe265df09f4159b14b81f250209b8b2e7be788edbafc`
- Rendered: 174 × ~57px inside the container

### NBS Wordmark Asset (extracted, user-directed)
- Source: mbatube.com school page `og:image` (409×195 JPEG, SHA-256 `04221ae19b1df1085c62176fd6204b1187ef31cea86f9cfa48d3aff3e52060bc`)
- Crop box: (6, 152, 398, 195) — bottom dense band rows 158–188 + 6px margin
- Raw crop output: 392 × 43 px PNG, white background, 9.1:1 aspect, SHA-256 `8082ad89d419a5c8f89797b2043fc073cd72e7b69830dc9eae705feaf4bb33b3` (provenance artifact)
- Normalization: raw crop background was 48.3% near-white JPEG noise (637 distinct values); glyph-safe flattening (near-white pixels with no content neighbor in 8-neighborhood → #fff, antialiased halos preserved) produced the production candidate, SHA-256 `e7a6df4f6e4fc3a5d80f43cf1582953258f9e6478ccd5274ee2e4297d96913a0`, same 392 × 43 geometry
- OCR: "Nanyang Business School" (exact, before and after normalization)
- Provenance: `third-party-derived-pending-user-approval` (NOT official; transitions to `user-approved-third-party-derived` only on explicit user approval); transparent derivative rejected (glyph damage)
- Durable storage: candidate `acceptance/candidates/nbs-wordmark-candidate.png` (SHA-256 e7a6df4f6e4fc3a5d80f43cf1582953258f9e6478ccd5274ee2e4297d96913a0), raw crop `acceptance/candidates/nbs-wordmark-raw-crop.png` (SHA-256 8082ad89d419a5c8f89797b2043fc073cd72e7b69830dc9eae705feaf4bb33b3), source composite `acceptance/candidates/mbatube-source-composite.jpg` (SHA-256 04221ae19b1df1085c62176fd6204b1187ef31cea86f9cfa48d3aff3e52060bc)
- Corroboration: user attachment = official NTU-hosted Gaia photo `picture2.jpg` (dHash 255/256) showing the same NTU+NBS lockup composition

## Proposed Design

### Layout: Horizontal Lockup

```
┌──────────────────────────────────────────────────────────┐
│  ┌────────────┐  │  ┌──────────────────────────────┐    │
│  │ NTU logo   │  │  │ Nanyang Business School      │    │
│  └────────────┘  │  └──────────────────────────────┘    │
└──────────────────────────────────────────────────────────┘
```

- NTU logo: left-aligned (position unchanged, width reduced)
- Neutral divider: 1px solid `rgb(0 30 97 / 20%)`, ~36px tall, centered vertically
- NBS wordmark: right of divider, white-background crop (no alpha keying)
- Container: flexbox (row), `align-items: center`

### Container Geometry

| Property | Current | Proposed |
|----------|---------|----------|
| width | 196px | auto, max ~390px |
| height | 72px | 72px (unchanged, verify no title overlap) |
| display | grid | flex (row) |
| padding | 7px 10px | 8px 12px |
| NTU img | 174px wide | ~122px wide (≈48px tall at 2.55:1) |
| NBS img | n/a | ~20–24px tall → ≈182–219px wide (9.1:1) |
| divider | none | 1px × 36px |

Expected total width: 122 + 12 + 1 + 12 + ~200 + 24 (padding) ≈ 370px.

### Height Budget

- Container: 72px; padding 8+8 → 56px available
- NTU rendered: ~48px tall
- NBS rendered: 20–24px tall (≥18px spec floor)
- Both vertically centered via `align-items: center`

### Safe-Area Verification

At 1280×720: left edge 64px ✓; right edge ≈64+390=454px ≪ 1216px ✓; top 36px ✓; bottom 36+72=108px ≤ 144px ✓.
At 1024×768: available width 896px ≫ 390px ✓.
Must also verify against every slide's title block, not only global stage bounds.

### Background and Border (theme adjustment)

- Background: CHANGED from `rgb(255 255 255 / 94%)` to opaque `#fff`. Rationale: the extracted wordmark crop has a baked 100%-white background; against a 94%-opaque pill on dark slides the crop would appear as a visibly brighter rectangle inside the pill. An opaque white pill removes the seam entirely. This is the ONLY theme adjustment in this change and must be verified on dark and light slides at qualification (task 3.1 seam check).
- Border-bottom: `3px solid var(--ntu-red)` (unchanged)
- Border-radius: 9px (unchanged)
- No gold accent (gold is reserved for data emphasis in slide content)

### Divider Styling

```css
.brand-divider {
  width: 1px;
  height: 36px;
  background: rgb(0 30 97 / 20%);
  flex-shrink: 0;
  margin: 0 6px;
}
```

### HTML Structure

```html
<div class="brand-layer" role="group" aria-label="Biểu trưng NTU và NBS">
  <img data-brand-asset="ntu-logo" src="assets/ntu-logo.png"
       alt="Biểu trưng Đại học Công nghệ Nanyang (NTU)">
  <span class="brand-divider" aria-hidden="true"></span>
  <img data-brand-asset="nbs-logo" src="assets/nbs-logo.png"
       alt="Biểu trưng Nanyang Business School (NBS)">
</div>
```

### Print / PDF

- `@media print` already preserves the brand-layer.
- White pill background ensures legibility on printed white paper.

### Rollback

If the NBS wordmark fails brand review or legibility:
- Remove the NBS `<img>` and divider `<span>`.
- Restore `.brand-layer` to `display: grid` and original width.
- Asset swap is isolated: one file + hash rebind if an officially issued NBS mark is obtained later.

## Risks

| Risk | Mitigation |
|------|-----------|
| Third-party-derived asset carries brand risk | Provenance recorded honestly (`third-party-derived-pending-user-approval` until explicit approval); human brand gate stays open; release stays `blocked-automated` |
| 43px source height limits crispness | Render at 20–24px height only (downscale, never upscale); swappable later for official asset |
| White background baked in (no alpha) | Pill changed to opaque `#fff` (theme adjustment) so the crop cannot seam; seam check on dark+light slides at qualification; proper anti-aliased matting is the fallback if opaque pill is rejected |
| Source resolution limit (43px native height) | Render at 20–24px only (downscale, never upscale above 43px); no CSS transforms that resample repeatedly; original composite + crop params retained in research record for reproducibility |
| Container too wide for some slide titles | Measure against every slide title at qualification; max-width cap ~390px |
| NBS wordmark illegible at 1024×768 | Spec floor: ≥18px rendered height + legibility scenario at 1024×768 |

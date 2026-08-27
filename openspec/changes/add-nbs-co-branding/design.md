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
- Mode: palette-indexed RGBA
- SHA-256: `8aabb7eec43917cbda6abe265df09f4159b14b81f250209b8b2e7be788edbafc`
- Rendered: 174 × ~57px inside the container

## Proposed Design

### Layout: Horizontal Lockup

```
┌─────────────────────────────────────────────────────┐
│  ┌──────────────┐  │  ┌──────────────┐             │
│  │  NTU logo    │  │  │  NBS logo    │             │
│  └──────────────┘  │  └──────────────┘             │
└─────────────────────────────────────────────────────┘
```

- NTU logo: left-aligned (unchanged from current)
- Neutral divider: 1px solid `rgb(0 30 97 / 20%)`, height ~40px, centered vertically
- NBS logo: right-aligned within the container, same max-height constraint
- Container: flexbox (row), centered items, gap controlled by padding

### Container Geometry

| Property | Current | Proposed |
|----------|---------|----------|
| width | 196px | ~310px (auto, max 340px) |
| height | 72px | 72px (unchanged) |
| display | grid | flex (row) |
| padding | 7px 10px | 8px 12px |
| NTU img width | 174px | 140px (slightly reduced) |
| NBS img width | n/a | auto (max-height: 48px) |
| divider | none | 1px × 36px |

### Height Budget

- Container: 72px
- Padding: 8px top + 8px bottom = 16px
- Available logo height: 56px
- NTU rendered: ~50px (140 × 512/1304 ≈ 54.7, clamped by max-height)
- NBS rendered: ≤48px (explicit max-height)
- Both logos vertically centered via `align-items: center`

### Safe-Area Verification

At 1280×720:
- Container left edge: 64px ✓ (matches safe_x)
- Container right edge: 64 + 340 = 404px ≪ 1216px (available width) ✓
- Container top edge: 36px ✓ (matches safe_y)
- Container bottom edge: 36 + 72 = 108px — well above any slide title area

At 1024×768 (smallest):
- Available width: 1024 − 2×64 = 896px
- Container 340px ≪ 896px ✓

### Background and Border

- Background: `rgb(255 255 255 / 94%)` (unchanged)
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
  margin: 0 4px;
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
- White background ensures legibility on printed white paper.
- The lockup prints at the same size as screen rendering.

### Rollback

If NBS logo fails provenance review or legibility:
- Remove the NBS `<img>` and divider `<span>`.
- Restore `.brand-layer` to `display: grid` and original width.
- No other files need reverting (asset files can be untracked).

## Risks

| Risk | Mitigation |
|------|-----------|
| NBS logo too small at 48px height | Test at 1024×768; fallback to text "NBS" if illegible |
| NBS logo has no transparent background | Add explicit white backing or request transparent PNG from brand owner |
| Container too wide for some content layouts | Constrain with `max-width: 340px`; measure against every slide |
| Brand owner objects to lockup arrangement | Human gate remains open; no release without approval |
| NBS logo unavailable in time | Ship NTU-only as default; NBS added when asset is approved |

# Design — NTU Brand Theme Alignment

## Current visual diagnosis

The candidate uses a dark navy stage and local NTU logo card. The primary visible eyebrow color is `#ff708f`; `--ntu-red` exists but is mainly used for structural borders and the lower-right rail; `#ffd166` is primarily a focus outline. This makes the deck read as a generic indigo/pink interface rather than a restrained NTU-family presentation.

The design will preserve the current visual hierarchy and use color as identity, not as new information encoding.

## Role-based palette

| Role | Value | Use | Contrast/guardrail |
|---|---|---|---|
| `--ntu-blue` | `#001E61` | reference navy for brand-aligned structural accents | not used as normal body text on dark stage |
| `--ntu-blue-stage` | `#0d1038` | dominant slide stage background | preserve current readability |
| `--ntu-red` | `#B21F2F` | structural crimson: top rule, rails, borders, blocks | decoration only on dark background; not normal text |
| `--ntu-red-ink` | `#F15B70` | readable crimson for eyebrow text | contrast against `#0d1038` is at least 4.5:1 |
| `--ntu-gold` | `#FFD166` | restrained metric/attention accent and focus ring | contrast against `#0d1038` is at least 4.5:1 |
| `--ntu-white` | `#FFFFFF` | primary text and logo-card background | preserve current white text |

The crimson and navy reference values are treated as visual references, not official NTU tokens, because the retrieved official pages did not publish a general NTU presentation palette. The gold value remains a screen-safe accessible accent rather than a claim about official Pantone equivalence.

## CSS implementation

1. Add `--ntu-blue-reference`, `--ntu-red-ink`, `--ntu-gold`, and `--ntu-white` alongside existing tokens. Retain `--ntu-blue-stage` and stage dimensions.
2. Set the existing visible `.eyebrow` text to `var(--ntu-red-ink)`.
3. Add `.slide-shell::before` as a non-interactive 4px top identity rule: crimson leading segment, short gold separator, transparent remainder. It must not change content flow, safe-area geometry, DOM order, or accessibility tree.
4. Add `.eyebrow::after` as a 32px × 3px gold marker with `aria-hidden`-equivalent decorative CSS only; it must not introduce text or controls. If pseudo-element rendering changes line wrapping at any supported viewport, remove this marker and retain only the top rule.
5. Set the existing metric outputs (`slide 3` and `slide 7`) and the two semantically meaningful metric-row endpoints (`slide 14` first and last cells) to `var(--ntu-gold)`; leave ordinary labels white.
6. Use `var(--ntu-red)` for existing structural red treatments and change the iceberg visible treatment from pink to a low-opacity crimson tint.
7. Add a thin crimson bottom edge to the existing white logo card only if it remains within the authored safe area; otherwise leave the card geometry unchanged.
8. Do not use `filter`, SVG recoloring, image editing, external CSS, external fonts, or JavaScript changes.

## Accessibility and layout

- Normal text must meet WCAG AA contrast of 4.5:1; large text must meet 3:1.
- `--ntu-red` is never used for normal-size text on the dark stage because its contrast is insufficient.
- The top rule and marker are decorative and cannot be the only indication of state or meaning.
- The logo card, content bounds, 1280×720 stage, 64px/36px safe inset, and all existing focus outlines remain within current geometry.
- Reduced-motion and print-final states must retain the final colors and decorations without animation.

## Evidence and candidate identity

Because `index.html` is a public package file, this is a Tier-1 public-content change:

1. Implement in the external repository worktree.
2. Regenerate `keynote-fallback.pdf` from the revised HTML if the presentation renderer is available; otherwise record the exact blocker and do not claim a refreshed PDF.
3. Capture or regenerate candidate-bound browser/accessibility/screenshot evidence for representative slides and rerun the full automated suite.
4. Recompute the seven-file package digest, all per-file checksums, release-manifest private hashes, and central intake/verification records.
5. Never reuse prior screenshot/PDF evidence solely because the old evidence passed; public bytes changed.

## Rollback and failure handling

If color contrast fails, a viewport overflows, or the PDF cannot be regenerated consistently, revert the implementation worktree before central acceptance. Do not weaken the contrast test or silently keep stale evidence. The previous candidate remains the rollback point.

## Rejected alternatives

- Full red background: rejected because it harms readability and overwhelms the logo relationship.
- Exact official Pantone claim: rejected because no public general NTU token table was retrieved.
- Adding the NTU crest or a new logo variant: rejected due to trademark/permission boundary.
- New imagery or external decorative assets: rejected because the deck is offline and the existing public allowlist is fixed.
- Changing slide content to insert branding language: rejected because this is a visual-only enhancement.

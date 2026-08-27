# Add NBS Co-Branding to NTU Keynote

## Why

The NTU alumni keynote currently carries only the NTU corporate logo in the top-left brand lockup (`.brand-layer`, 196×72px grid, single `<img data-brand-asset="ntu-logo">`). This talk is hosted under the Nanyang Business School (NBS) umbrella, so both the NTU and NBS identity marks should appear together; omitting the NBS mark leaves the audience without clear school affiliation.

Baseline at intake (ntu-keynote main): HEAD `97a0236`, public package digest `8a96ed4f...`, worktree clean.

Research performed this session (web sweeps of ntu.edu.sg and candidate asset sources):

- `ntu.edu.sg/about-us/nbs-brand` and `ntu.edu.sg/brandportal` return 404 — no downloadable NBS brand asset located on the official site.
- The only candidate image found (a `62234f...png` on a maglr.com CDN) is a 100×100 placeholder thumbnail, not an official mark, and fails provenance review.
- Conclusion: the NBS logo asset is an unresolved provenance gap. Task 1.1 is blocked until the user provides the approved NBS logo file or confirms an official source. Until then, the deck stays NTU-only.

## What Changes

- Add a second logo asset (NBS) alongside the existing NTU logo in one shared top-left brand lockup: NTU left, thin neutral vertical divider, NBS right.
- Expand `.brand-layer` (flex row, width auto capped at ~340px, height unchanged at 72px) to accommodate both marks with independent clear space.
- Record the new asset in `evidence/assets.json`, the venue-package allowlist, `checksums.sha256`, and the release manifest; rebind the package digest.
- Regenerate `keynote-fallback.pdf`, rebind `evidence/pdf-binding.json`, re-run browser qualification, and publish a new Drive version folder after all acceptance gates pass.

## Non-Goals

- This change does **not** modify any slide content, claim copy, qualifiers, timing, navigation, notes, or SVG visuals.
- This change does **not** alter the NTU logo file, the palette, or any existing brand color.
- This change does **not** introduce new fonts, external resources, animations, or JavaScript.

## Constraints

1. **Offline-first**: both logos must be local PNG/SVG assets inside `assets/`. No hotlinks, no external URLs, no CDN dependencies.
2. **Safe area**: the expanded lockup must fit within the authored safe area at 1280×720 (safe_x=64, safe_y=36) and all required smaller viewports (1024×768, 1366×768, 1440×900, 1920×1080); container bottom must not exceed y=144 at the authored stage.
3. **Independent clear space**: NTU and NBS marks remain visually independent — not merged, not overlapped, no shared bounding box implying a combined identity.
4. **Legibility (not WCAG text contrast)**: WCAG 4.5:1 is a text-contrast criterion and is NOT applied verbatim to logo images. Instead, both marks must pass a rendered-size legibility check against the white 94%-opaque pill at 1024×768. If the NBS mark contains white or very light elements that vanish against the pill, use the mark's dark/colored variant or an opaque backing.
5. **Print**: the lockup must appear in the PDF fallback with correct sizing, not clipped.
6. **Accessibility**: both `<img>` elements carry Vietnamese `alt` text; the container carries `role="group"` with a Vietnamese `aria-label`; the lockup remains inside a `pointer-events: none` layer.
7. **No content claim change**: no existing Vietnamese copy, qualifier, source reference, or notes text is modified.

## Approach

A horizontal lockup in the top-left corner: NTU logo on the left (existing position, width reduced 174→140px), a 1px neutral divider (`rgb(0 30 97 / 20%)`, 36px tall), NBS logo on the right (max-height 48px). White translucent background and red bottom border retained. The container grows in width only; height stays within the current 72px ceiling so no slide title is overlapped. Full geometry, HTML structure, and rollback plan are in `design.md`.

## Open Questions

1. **NBS logo provenance (blocking)**: no authoritative downloadable NBS logo asset has been found on `ntu.edu.sg`. The user must provide the approved NBS logo file or confirm an official source before task 1.1 can complete.
2. **Logo variant**: should NBS use its wordmark, icon, or full lockup with "Nanyang Business School" text?
3. **Dark-background slides**: is the white-translucent pill sufficient for all slides, or does the NBS mark need a light variant anywhere?

## Success Criteria

- Both logos visible in the brand lockup on every slide, legible at 1024×768.
- Package digest differs from predecessor (`8a96ed4f...`).
- Full test suite green, static verifier 11/11, `shasum -c checksums.sha256` passes.
- PDF regenerated with correct lockup; pdf-binding rebound.
- New Drive version folder created; prior version untouched.
- Release remains `blocked-automated` with human brand/editorial gates open; no tag, no archive.

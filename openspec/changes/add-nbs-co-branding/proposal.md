# Add NBS Co-Branding to NTU Keynote

## Why

The NTU alumni keynote currently carries only the NTU corporate logo in the top-left brand lockup (`.brand-layer`, 196×72px grid, single `<img data-brand-asset="ntu-logo">`). This talk is hosted under the Nanyang Business School (NBS) umbrella, so both the NTU and NBS identity marks should appear together; omitting the NBS mark leaves the audience without clear school affiliation.

Baseline at intake (ntu-keynote main): HEAD `97a0236`, public package digest `8a96ed4f...`, worktree clean (frozen in `acceptance/nbs-baseline.json`, validated 12/12 against live state).

Research performed this session (web sweeps, user-provided assets, user-directed extraction — full record in `research/nbs-logo-provenance.json`):

- Official NTU site dead ends: `/about-us/nbs-brand` 404, `/brandportal` 404, `/nbs` 404, `nbs.ntu.edu.sg` NXDOMAIN, Wikimedia Commons empty.
- User attachment (`img_58f72e2dec49.jpg`, 755×582 JPEG, SHA-256 `a0734180...`): photographed NTU/NBS signage lockup on a textured tan background. Corroborated as the official NTU-hosted Gaia article photo `picture2.jpg` (dHash agreement 255/256) — but photographic/textured, not production-ready.
- User-directed extraction from `https://mbatube.com/school/nanyang-business-school`: the page's `og:image` (409×195 JPEG, SHA-256 `04221ae1...`) is a clean white-background composite lockup — NTU crest + university name stacked above the "Nanyang Business School" wordmark. Deterministic crop of the wordmark band (rows 158–188, +6px margin) yields a 392×43 PNG (raw SHA-256 `8082ad89...`) whose OCR reads exactly "Nanyang Business School"; because the raw crop background was 48.3% near-white JPEG noise, a glyph-safe normalization (near-white pixels with no content neighbor flattened to #fff, antialiased halos preserved) produced the production candidate (SHA-256 `e7a6df4f...`, same geometry, OCR still exact). A transparent-background derivative was REJECTED (hard-threshold flood fill damaged glyphs). The whole composite is NOT usable because it duplicates NTU identity already carried by the deck's NTU logo.
- Provenance classification: `third-party-derived-pending-user-approval` — the user directed the extraction, which authorizes research and candidate preparation only, NOT embedding in the deck. The asset is NOT officially issued by NTU. On explicit user approval (task 1.1b) it transitions to `user-approved-third-party-derived`. The human brand-approval gate remains OPEN and release stays `blocked-automated`. The candidate and its source composite are preserved durably under `acceptance/candidates/`.

## What Changes

- Add the extracted, normalized NBS wordmark asset (`assets/nbs-logo.png`, white-background 392×43 PNG) alongside the existing NTU logo in one shared top-left brand lockup: NTU left, thin neutral vertical divider, NBS wordmark right.
- Expand `.brand-layer` (flex row, width ~350–390px, height unchanged at 72px) to accommodate both marks with independent clear space.
- Record the new asset in `evidence/assets.json`, `checksums.sha256`, and the release manifest; rebind the package digest. (The venue-package allowlist already includes `assets/` — no allowlist edit needed, verify only.)
- Regenerate `keynote-fallback.pdf`, rebind `evidence/pdf-binding.json`, re-run browser qualification, and publish a new Drive version folder after all acceptance gates pass.

## Non-Goals

- This change does **not** modify any slide content, claim copy, qualifiers, timing, navigation, notes, or SVG visuals.
- This change does **not** alter the NTU logo file, the palette, or any existing brand color.
- This change does **not** introduce new fonts, external resources, animations, or JavaScript.

## Constraints

1. **Offline-first**: both logos must be local assets inside `assets/`. No hotlinks, no external URLs, no CDN dependencies.
2. **Safe area**: the expanded lockup must fit within the authored safe area at 1280×720 (safe_x=64, safe_y=36) and all required viewports (1024×768, 1366×768, 1440×900, 1920×1080); container bottom must not exceed y=144 at the authored stage and must not overlap any slide title.
3. **Independent clear space**: NTU and NBS marks remain visually independent — not merged, not overlapped, no shared bounding box implying a combined identity.
4. **Legibility (not WCAG text contrast)**: WCAG 4.5:1 is a text-contrast criterion and is NOT applied verbatim to logo images. The NBS wordmark rendered height must be ≥18px at the authored stage and the full phrase must be legible at 1024×768. The white-background crop relies on the deck's white 94%-opaque pill; no alpha keying.
5. **Print**: the lockup must appear in the PDF fallback with correct sizing, not clipped.
6. **Accessibility**: both `<img>` elements carry Vietnamese `alt` text; the container carries `role="group"` with a Vietnamese `aria-label`; the lockup remains inside a `pointer-events: none` layer.
7. **No content claim change**: no existing Vietnamese copy, qualifier, source reference, or notes text is modified.
8. **Provenance honesty**: the asset is recorded as `third-party-derived-pending-user-approval` until explicit user approval (then `user-approved-third-party-derived`), never as `official-page-asset`.

## Approach

A horizontal lockup in the top-left corner: NTU logo on the left (existing position, width reduced 174→~122px at ~48px height), a 1px neutral divider (`rgb(0 30 97 / 20%)`, ~36px tall), NBS wordmark on the right at ~20–24px rendered height (≈182–219px wide given the 9.1:1 aspect). White translucent background and red bottom border retained. Expected container width ≈350–390px; height stays 72px if browser measurement confirms no title overlap. Full geometry, HTML structure, and rollback plan are in `design.md`.

## Open Questions

1. **NBS logo provenance** — extraction COMPLETE, embedding approval PENDING (task 1.1b): user-directed extraction from mbatube.com produced a clean wordmark candidate, classified `third-party-derived-pending-user-approval`, corroborated against official Gaia imagery. Extraction authorization is not embedding approval; the user must explicitly choose before implementation. The candidate is eligible for implementation preview only and SHALL NOT close the human brand gate or be represented as officially issued.
2. ~~Logo variant~~ — RESOLVED: wordmark only ("Nanyang Business School"), because the deck already carries NTU crest + university name.
3. **Dark-background slides**: contact sheet (`acceptance/nbs-contact-sheet.png`) shows the white-bg wordmark on white, navy, and checker backgrounds; confirm at qualification that the white pill keeps it legible on every slide.

## Success Criteria

- Both logos visible in the brand lockup on every slide; NBS wordmark ≥18px rendered height, legible at 1024×768.
- Package digest differs from predecessor (`8a96ed4f...`).
- Full test suite green, static verifier 11/11, `shasum -c checksums.sha256` passes.
- PDF regenerated with correct lockup; pdf-binding rebound.
- Drive upload deferred until human brand approval (no third-party-derived asset syncs before approval); prior version untouched.
- Release remains `blocked-automated` with human brand/editorial gates open; no tag, no archive.

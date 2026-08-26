# Research context — NTU keynote brand-theme alignment

Date: 2026-08-26 (Asia/Ho_Chi_Minh)

## Sources consulted

1. Official NTU Singapore About Us: https://www.ntu.edu.sg/about-us
   - Confirms NTU Singapore positioning as a technological university and its stated AI-enabled future.
   - No public color-token table was exposed on the retrieved page.

2. Official NTU National Institute of Education Corporate Identity page: https://www.ntu.edu.sg/nie/about-us/corporate-identity
   - States that the vibrant primary colours blue, red and golden yellow reflect the red and gold of the NTU logo and project dynamism, progressiveness and confidence.
   - States that the shield/lion relationship connects the identity to NTU.
   - This is an NTU-owned identity page, but it is the NIE identity page rather than a general NTU presentation manual.

3. NTU Terms of Use: https://www.ntu.edu.sg/legal/terms-of-use
   - Search result states that NTU name, logo and crest are trademarks and may not be used without prior written consent.
   - This change therefore does not add, redraw, or modify the NTU logo/crest.

4. Reference-only third-party logo catalog: https://logotyp.us/logo/ntu-sg/
   - Reports reference values around navy `#001E61` and red `#B21F2F` for an NTU SG logo asset.
   - These values are not treated as official NTU design tokens; they are used only as a conservative visual reference.

5. Direct candidate inspection: `~/Developer/ntu-keynote/index.html`
   - Dominant stage colors are dark navy (`#07091f`, `#0d1038`, `#181c62`).
   - Visible eyebrow accent is pink (`#ff708f`), while red is mostly structural and gold is used primarily for focus rings.

## Decision

Use a navy-dominant, white-readable theme with restrained crimson-red and golden-yellow accents. Retain the existing dark stage background and local logo asset. Replace the visible pink accent with an accessible light-crimson role, use the reference crimson for structural decoration, and promote gold to a limited metric/identity accent. Do not claim official hex-code compliance, do not add third-party assets, and do not change slide copy or factual claims.

## Confidence and limits

- High confidence: blue/red/golden-yellow are part of the NTU-family identity language because the official NTU NIE page states this directly.
- Medium confidence: the exact reference hex values because they come from a third-party catalog, not a retrieved official NTU brand manual.
- Unknown: whether the keynote organizer has a separate event-specific NTU lockup or current presentation template. A final institutional-brand approval remains a human gate.

## Public-byte consequence

`index.html` is one of the seven public package files. Any CSS update changes its SHA-256 and therefore requires a new implementation candidate, regenerated PDF/screenshots where applicable, refreshed checksums, and a new central acceptance rebind. No existing release tag or archive may be reused as proof for the revised candidate.

## Rollback

Revert the implementation commit and its evidence refresh commit together. The prior candidate remains available by commit history; no database, external service, or logo asset mutation is involved.

## Research gaps

The two guessed general NTU brand-guideline URLs returned Page Not Found. This plan must not state that the proposed hex values are official or that the result is institutionally approved.

## Review traceability

The authoritative implementation/spec lifecycle is the central OpenSpec change `align-ntu-keynote-with-ntu-brand-theme` in `~/Developer/openspec-store`. The implementation owner is `~/Developer/ntu-keynote` on `main`.

## Required post-change evidence

- CSS-token and decoration assertions
- contrast calculation for text and focus roles
- 17-slide structural/static verification
- full test suite
- regenerated 17-page PDF if the existing PDF is changed
- refreshed seven-file digest and checksums
- visual inspection evidence for representative slides; existing screenshots cannot be reused merely because the public bytes changed
- explicit human institutional/editorial approval remains separate from automated checks

# Align NTU Keynote With NTU Brand Theme

## Why

The current keynote is structurally strong and uses a dark navy stage, but its visible accent system is dominated by a pink highlight while the NTU-family identity research points to a blue, red and golden-yellow palette. The NTU-owned NIE Corporate Identity page explicitly describes blue, red and golden yellow as the vibrant primary colours reflecting the NTU logo; the retrieved NTU pages do not expose a general-purpose public presentation token sheet. The keynote should therefore become visibly NTU-aligned without falsely claiming official brand-guide compliance.

This is a visual-system enhancement, not a content rewrite. The deck must preserve the neutral copy, all factual qualifiers, the 17-slide narrative, the offline runtime, the seven-file public package boundary, and existing accessibility constraints.

## What Changes

- Add explicit visual role tokens for navy, reference crimson, readable light crimson, golden yellow, and white in the inline CSS.
- Keep deep navy as the dominant stage color and white as the primary reading color.
- Replace the visible pink eyebrow accent with an accessible light-crimson role that maintains normal-text contrast.
- Add a restrained crimson/gold top identity rule and a small gold marker to section eyebrows without changing DOM order or slide copy.
- Use gold sparingly for the existing attention metrics and the existing keyboard-focus role; do not turn every metric into decorative emphasis.
- Align existing red structural accents and the iceberg treatment with the reference crimson role.
- Do not add a new logo, crest, external asset, web font, network dependency, animation, or presenter interaction.
- Regenerate candidate-bound PDF/evidence/checksums and re-register the implementation candidate centrally because `index.html` is a public package byte.
- Add automated tests for palette roles, decoration bounds, contrast, logo-preservation, public/private boundary, and unchanged slide/content contracts.

## Scope and Ownership

- Implementation owner: `~/Developer/ntu-keynote`, `main`.
- Planning and acceptance owner: `~/Developer/openspec-store`, central change `align-ntu-keynote-with-ntu-brand-theme`.
- No mutation of the earlier `add-ntu-ai-keynote-deck` history; this change is a follow-on enhancement with a separate candidate identity.
- Only implementation CSS/evidence and this central change's planning/acceptance artifacts are in scope.

## Compatibility

The presentation remains a single offline `file://` HTML deck with exactly 17 slides, local fonts/assets, deterministic full/short routes, existing controls, and a PDF fallback. The enhancement is CSS-only in the runtime surface; it must not alter slide text, notes, timing, fragment routing, local-storage behavior, or public package file count.

## Rollout and Verification

Apply the implementation in an isolated worktree, then run the owning suite, static verifier, checksum verification, package-digest recomputation, and a fresh visual inspection of representative title, metric, content, and handoff slides. Bind regenerated evidence to the new committed candidate. Run strict validation for this central change and the central store doctor before integration.

The visual result is automated- and evidence-verified, not institutionally approved, until a qualified human reviewer confirms the actual NTU usage context.

## Rollback

Revert the implementation commit and its candidate evidence refresh as a reviewed pair. The prior implementation candidate and its central acceptance history remain preserved. No external system, logo asset, or source record is mutated.

## Non-Goals

- Official trademark or brand approval.
- Recreating or modifying the NTU crest/logo.
- Selecting exact official Pantone/HEX values when the public official source was not retrieved.
- Changing slide facts, Vietnamese copy, presenter notes, timing, or route behavior.
- Adding photographs, icons, third-party assets, gradients that imply data, or new animations.

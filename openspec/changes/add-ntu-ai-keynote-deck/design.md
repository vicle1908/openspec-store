## Context

See `proposal.md` for motivation and scope. Lê Khánh Vinh (Solutions Architect at Viettel, NTU alumnus 2006–2010) will deliver the 10–15 minute opening keynote **“AI Vượt Qua Trào Lưu — Từ Bức Tranh Vĩ Mô Đến Giá Trị Thực Cho Doanh Nghiệp”** at an NTU alumni event immediately before a roundtable.

The central change is the sole OpenSpec planning, requirements, task, acceptance, validation, and archive lifecycle for this keynote; its six delta specs define the contract. OpenSpec 1.10 binds native edits to the central store root, so implementation, executable verification, private evidence, packaging, rehearsal, release commits, and tagging occur through separately authorized external orchestration. The central workflow may accept immutable, hash-bound external outputs, but it may not mutate their source. External or historical local OpenSpec artifacts are read-only migration or evidence inputs only; no local OpenSpec lifecycle has independent authority or contributes central acceptance state.

The venue surface is exactly 17 Vietnamese slides in three acts: macro picture (0:00–3:45), hype/value gap and transferable three-layer journey (3:45–10:40), and leadership/roundtable handoff (10:40–12:45). The full route is 765 seconds; the short route is 600 seconds, visits 15 slides, and skips only slides 4 and 8.

## Goals / Non-Goals

**Goals:**
- Translate the six central specs into one coherent implementation and acceptance architecture.
- Preserve offline `file://` reliability, fixed-stage presentation, Vietnamese language, factual qualifiers, accessibility, inline visual authorship, and exact release evidence.
- Define clean boundaries among central authority, external implementation, immutable evidence submission, central acceptance, and external human gates.
- Make evidence invalidation, browser-computed acceptance, and release identity deterministic.

**Non-Goals:**
- No central native apply into the external implementation repository.
- No copying implementation or private evidence into the central change.
- No framework, bundler, server, CDN, live network, stock-photo/icon dependency, presenter-window protocol, or additional public venue file.
- No restoration of `localStorage`, the former external-folder model, or legacy task-number assumptions.
- No claim that artifact-presence status proves design coherence, implementation readiness, evidence freshness, archive readiness, or release readiness.

## Decisions

### D1: Central contracts are authoritative; external implementation is a separate transaction

The central proposal, six specs, this design, and the central tasks are the sole OpenSpec lifecycle defining requirements and acceptance for this change. External implementation may satisfy these contracts but may not relax or reinterpret them. External or historical local OpenSpec artifacts are read-only migration or evidence inputs; no local OpenSpec `status`, `validate`, `apply`, `archive`, task completion, or same-named lifecycle has independent authority or contributes central acceptance state.

External orchestration produces an immutable submission descriptor containing at minimum:
- implementation/evidence-base commit identity;
- exact public-package digest and per-file SHA-256 values;
- selected neutral or approved-copy identity;
- requirement IDs covered by each evidence record;
- browser, accessibility, PDF, rehearsal, and release-manifest references.

Central tasks consume that descriptor and its referenced evidence read-only. They may record central acceptance state only inside the central allowed edit root. Missing or failing evidence returns a deficiency for a separately authorized external remediation cycle; central tasks never edit, stage, commit, tag, regenerate, or delete external files.

**Non-circular acceptance:** central release acceptance is derived exclusively from immutable external evidence and the recorded results of named predecessor central gates. The completion state of any final administrative closure task is an output of that decision, never an input; no task may require its own completed state to derive acceptance.

**Transaction boundaries:** central planning commits, external implementation/evidence commits, the external release commit/tag, and central acceptance commits are independent transactions. No operation claims cross-repository atomicity or native central authorization outside the store.

### D2: One self-contained runtime with an exact seven-file public package

The runtime remains one directly opened `index.html` with inline CSS and vanilla JavaScript. The only sibling assets are the transparent 1304×512 NTU logo and Be Vietnam Pro Vietnamese-subset WOFF2 fonts at weights 400, 600, and 800.

All new diagrams, data visualizations, editorial illustrations, and iconography are authored inline in `index.html`. The released package contains exactly:
1. `index.html`
2. `README.md`
3. `keynote-fallback.pdf`
4. `assets/ntu-logo.png`
5. `assets/fonts/be-vietnam-pro-400.woff2`
6. `assets/fonts/be-vietnam-pro-600.woff2`
7. `assets/fonts/be-vietnam-pro-800.woff2`

Planning, source, approval, license, tests, scripts, screenshots, evidence, Git, and worktree files remain private and are never runtime dependencies. The package identity uses `ntu-keynote-package-sha256-v1`: sort the exact seven normalized POSIX paths by UTF-8 bytes; hash the domain prefix `NTU_KEYNOTE_PACKAGE_V1\0`; then for each entry hash uint64-be path-byte-length, path UTF-8 bytes, uint64-be file-byte-length, and raw file bytes. Evidence records the algorithm/version, all seven per-file SHA-256 values, and test vector `a.txt`=`41`, `dir/b.bin`=`00ff` => `b13c66f843d56fdd261d6d57faade59c68f1a349d8f5a467657420cc396ab1ad`.

**Retains:** legacy D1's single HTML and relative local assets.
**Replaces:** the former instruction to copy an unrestricted external folder.

### D3: Fixed stage, safe area, palette, and scoped typography

Slides are authored at 1280×720, centered and scaled by `min(viewportWidth/1280, viewportHeight/720)` with non-distorting letterboxing. Required content remains inside a 5% safe area and is qualified at 1920×1080, 1440×900, 1366×768, and 1024×768. The design claims stable containment and aspect ratio, not pixel identity across devices.

The palette remains NTU Blue `#181C62`, projection-adapted background `#0D1038`, NTU Red `#D71440`, and high-contrast light text. Red is a disciplined accent, not the sole carrier of meaning.

At the unscaled authored 1280×720 stage, every visible element classified as carrying required audience meaning computes to at least 18 CSS pixels in both qualified Safari and Chrome before the stage transform, regardless of element type. Source, citation, and provenance text is auxiliary only when it carries no required audience meaning; a separately classified qualifier within it remains included when narratively required. Evidence records every visible text element, its included-or-auxiliary classification, and the reason. Auxiliary text still requires role-appropriate legibility, contrast, visibility, and overflow acceptance. Required meaning may not bypass the floor by element choice, decorative marking, or an accessible-only description. Local-font failure falls back without content loss.

**Retains:** legacy D2, D5, and D6 with corrected claim scope and fallback acceptance.

### D4: Deterministic routes use canonical fragment state, not persistent storage

Navigation supports next/previous, Home/End, direct access, standard keyboard/clicker input, pointer input, repeat protection, visible progress, and visible route mode. Interactive and notes clicks never trigger background advance.

The full route visits slides 1–17 with seconds `30,60,45,45,45,45,45,45,40,40,50,50,50,50,50,45,30`. The short route visits `1,2,3,5,6,7,9,10,11,12,13,14,15,16,17` with seconds `25,25,35,40,25,35,25,35,45,40,45,45,45,105,30`.

Route mode and current slide are encoded in a canonical URL fragment that works under Safari `file://`. Valid reload restores state; malformed state falls back safely; reset returns to full mode slide 1. Behavior does not depend on `localStorage` or any other persistent storage.

**Retains:** legacy D3's clicker-oriented controls.
**Replaces:** legacy D9 `localStorage` recovery and the former merge-based short route.

### D5: Notes, semantics, and accessibility share one active-slide model

Each slide owns Vietnamese notes with full-route timing, short-route timing or skipped state, source reminders, and one delivery cue. Notes are off by default, synchronized to the active slide, closable with Escape, excluded from print, and visibly warn that they are audience-visible on mirrored displays.

Only the active slide is exposed as active semantic content; inactive slides leave the accessibility tree and focus order. Slide changes announce `Trang X trên 17` without stealing focus. All runtime actions are keyboard-operable with visible focus and no trap. Meaningful visuals expose concise Vietnamese equivalents in logical reading order; decorative vectors are hidden. Normal text meets 4.5:1 contrast, large text 3:1, and all essential color distinctions have non-color counterparts.

**Retains:** legacy D4's single synchronized notes representation.
**Extends:** notes, focus, semantics, visual equivalents, contrast, reduced motion, and fallback requirements from `accessible-stage-presentation`.

### D6: Inline visuals preserve one narrative job and source meaning per slide

Each slide retains one dominant narrative job and one dominant visual job. Inline SVG/CSS is used for diagrams, source-faithful data displays, editorial vector illustrations, and accessible iconography. Visual encodings must preserve source population, denominator, horizon, uncertainty, policy scope, sign, and proportional meaning.

The three acts remain:
- **Act 1:** identity and hook; PwC modeled 2030 potential; Gartner agentic forecasts; Nghị quyết 57 AI R&D target; Google/Access Partnership modeled Vietnam opportunity.
- **Act 2:** explicitly illustrative iceberg; MIT NANDA and Gartner evidence; distinct ChatGPT, internal-LLM, and multi-agent layers; value conversion rather than technology adoption alone; WEF workforce framing across all macro drivers.
- **Act 3:** three leadership mindsets; concise 95%/39%/**hơn 40%** prompts; separate 30-second NTU alumni handoff.

Slide 7 deliberately treats three contexts as independent claims: the registered 95% finding about organizations in the analyzed population, the registered 5% finding about integrated AI pilots that generated substantial value, and the USD 30–40 billion figure only as separate directional investment context. The 95% and 5% figures have distinct populations and units; separate claim identities, labels, and visual groups prevent complementary slices, a shared denominator, a common sample, or causal connectors, and no bar, pie, donut, track, or proportional geometry may join them. No animation, layout, narration, or proportional encoding may link the investment context to either percentage population.

### D7: Attention animations begin only on target-slide active entry

Motion remains limited to the PwC counter, MIT emphasis, and one restrained base transition. An attention effect resets before entry and starts only after its target slide becomes active and visible. It does not start during unrelated page initialization, on the preceding slide's exit, or merely because the inactive slide exists.

Direct fragment entry and reload on an attention slide trigger that slide's defined entry. Revisiting resets and replays once. Reduced-motion and print paths expose complete final values immediately.

**Retains:** legacy D7's animation budget.
**Replaces:** ambiguous activation timing with the exact `timing-and-roundtable-handoff` entry contract.

### D8: Provenance and copy selection are machine-readable acceptance inputs

Every factual claim maps bidirectionally to a stable source record containing organization, title, publication/access dates, lawful reference, exact wording, slide mapping, scope, and qualifier. Meaningful visuals record purpose, authorship/license basis, source IDs, encoded values, qualifier, and accessible equivalent.

PwC, Gartner, Google/Access Partnership, McKinsey, and WEF remain projections, modeled potential, or estimates as registered. The MIT NANDA 95% finding remains scoped to organizations in its analyzed population and the 5% finding remains scoped to integrated AI pilots that generated substantial value; those percentage claims retain distinct populations and units and are not treated as complements; USD 30–40 billion remains separate directional investment context; Gartner remains **hơn 40%**, not an exact 40%; WEF remains across all macro drivers; Nghị quyết 57 remains scoped to AI research and development.

Neutral company-safe copy is the default. Company-specific wording is selectable only through a named, timestamped, scope-limited approval whose SHA-256 matches the exact released wording and covered slides. Missing, rejected, partial, stale, or mismatched approval selects neutral copy and leaves no dormant gated text in the public package.

### D9: Evidence invalidation uses two tiers

**Tier 1 — public-candidate change:** any public package byte, selected audience/notes wording, visual encoding, runtime behavior, or PDF input change invalidates browser, accessibility, viewport, screenshot, PDF, package-checksum, manifest, and copied-folder evidence. All affected evidence is rerun against one exact candidate.

**Tier 2 — private-record-only change:** if every public hash and selected copy remain identical, matching rendering and interaction evidence may be retained. The changed private record and every dependent traceability, freshness, approval, manifest, or checksum assertion are refreshed. If the private change alters selected public meaning, Tier 1 applies.

Evidence retention is therefore decided from recorded hashes and dependency relationships, not filenames, timestamps alone, or agent judgment.

### D10: Browser evidence owns computed-style and rendered-state facts

Static validation owns source-level structure: slide IDs/order, local-only references, declared route arithmetic, source mappings, allowlist shape, and unresolved-marker scans. It MUST NOT claim computed font sizes, rendered contrast, or any other cascade-dependent fact.

Safari/Chrome evidence owns facts produced by the cascade or rendered state: computed font sizes, effective foreground/background colors, display, visibility, opacity, transforms, focus outlines, active/inactive exposure, overflow, clipping, reduced-motion state, animation entry, and print final state. A source declaration cannot override a conflicting computed result.

Both browsers qualify the same candidate hashes and retain environment, timestamp, requirement IDs, initial state, action, resulting state, results, and referenced screenshots/reports. For the scoped 18px floor, each browser enumerates every visible text element, records its semantic classification and reason, and captures each included element’s computed font size at the authored 1280×720 stage before the stage transform; element type does not determine inclusion. Generic pass labels without observable state do not satisfy acceptance.

### D11: PDF and rehearsals are fixed external human gates

The PDF is generated from the accepted candidate, contains exactly 17 ordered pages, preserves dark backgrounds, Vietnamese glyphs, meaningful reading order, and final animation states, and excludes notes and controls. Its hash is bound to `index.html`, selected source/approval state, and the evidence-base commit.

The exact public package digest is first rehearsed from an alternate path containing spaces and Vietnamese characters with network unavailable to the browser context. The same digest is then rehearsed on the actual presenting laptop with projector or external display and real clicker, covering fullscreen, navigation, notes policy, reload recovery, full delivery, exact short route, sleep/display safeguards, and PDF fallback within 30 seconds.

These gates are performed and attested externally. Central tasks verify their immutable records; they do not perform or repair the external rehearsal.

### D12: Release identity uses a fixed annotated tag without circular commit claims

The fixed intended ref is exactly `refs/tags/ntu-ai-keynote-v1.0.0`. The private manifest records the evidence-base commit, exact public digest, selected copy, source/approval state, evidence results, and that fixed intended ref, but never embeds the SHA of the commit containing that manifest.

Before external finalization, immutable evidence SHALL establish that `refs/tags/ntu-ai-keynote-v1.0.0` is available for this release; a conflicting existing ref blocks release and is never moved, deleted, reused, or repointed by a central task. After all automated and human gates pass, external orchestration creates the release commit and then the annotated tag at that exact ref. Acceptance verifies that the ref resolves to an annotated tag object and derives the authoritative final commit externally by peeling `refs/tags/ntu-ai-keynote-v1.0.0^{commit}`; the peeled commit SHALL contain the accepted manifest and exact public package digest. A dynamic, alternate, lightweight, conflicting, or unverifiable ref, a self-referential manifest SHA, or a peeled commit targeting different public bytes fails release identity.

## Traceability

| Central capability | Primary decisions | Acceptance boundary |
|---|---|---|
| `offline-keynote-runtime` | D2–D5, D7 | Offline launch, stage, routes, fragments, notes, motion |
| `keynote-content-and-language` | D3, D6, D8 | 17-slide narrative, Vietnamese policy, independent slide-7 metrics |
| `timing-and-roundtable-handoff` | D4, D5, D7 | Exact route arithmetic, notes timing, animation entry, handoff |
| `factual-provenance-and-approval` | D6, D8, D9, D12 | Source/visual fidelity, neutral/approved copy, invalidation, identity |
| `accessible-stage-presentation` | D3, D5, D7, D10, D11 | Semantics, focus, scoped 18px, contrast, reduced motion, print |
| `browser-qualification-and-release-evidence` | D1, D9–D12 | Hash-bound evidence, computed styles, package/PDF, rehearsals, tag |

## Risks / Trade-offs

- **Central status appears complete while tasks are stale.** Mitigation: treat file-presence status as non-authoritative for coherence; reconcile and approve tasks separately.
- **Evidence bundle is internally valid but targets different public bytes.** Mitigation: require one public-package digest and per-file hashes across every accepted record.
- **Central task attempts to repair external work.** Mitigation: fail the gate and return a deficiency; central allowed-root writes are limited to central acceptance state.
- **Slide 7 visually conflates its three contexts.** Mitigation: separate claim identities, groups, labels, provenance IDs, forbidden complementary geometry, and browser-reviewed connectors and proportions.
- **Static CSS passes while rendered style fails.** Mitigation: browser-computed evidence controls typography, contrast, visibility, overflow, focus, motion, and print acceptance.
- **Tier 2 is used to avoid a required rerun.** Mitigation: allow retention only when all public hashes and selected meaning are identical and dependency records prove the retained evidence remains applicable.
- **Venue browser, font, clicker, projector, or network conditions differ.** Mitigation: Safari/Chrome matrices, font fallback, letterboxing, copied-folder rehearsal, actual hardware rehearsal, and 30-second PDF fallback.
- **Release manifest becomes circular.** Mitigation: fixed annotated tag, pre-release evidence-base commit, public digest, and externally peeled final commit.
- **Company wording ships without exact authority.** Mitigation: neutral default and SHA-bound approval fail closed.

## Migration Plan

1. Replace the legacy design with this reconciled central design; do not change implementation, evidence, tasks, or external repositories in the same approval.
2. Strictly validate the central change and confirm the six specs remain active.
3. In a separate approval, replace the legacy 28-task ledger with central-only planning and read-only acceptance tasks mapped to the traceability table. No central task may mutate the external implementation root or invoke or depend on any local OpenSpec lifecycle. The replacement ledger uses the non-circular closure model: final acceptance is derived from immutable external evidence and named predecessor gates, and the final closure task's own completion is an output of that decision, never an input.
4. Through separately authorized external orchestration, reconcile implementation to the approved central contracts and produce an immutable hash-bound evidence submission. External or historical local OpenSpec artifacts, if any, accompany the submission only as read-only migration or evidence inputs.
5. Central tasks review the submission read-only and record pass, fail, stale, or blocked acceptance state. Failures return to the external owner as a new transaction.
6. Record central release acceptance only after immutable external evidence exists and passes: fresh automated evidence, neutral-or-approved copy, copied-folder rehearsal, actual venue rehearsal, the external release commit, the annotated ref `refs/tags/ntu-ai-keynote-v1.0.0`, and its externally peeled commit. Acceptance is derived from that evidence and the recorded results of predecessor central gates; it does not depend on the completion state of the task that records it.
7. Archive only after proposal, specs, design, tasks, evidence relationships, human gates, and release identity are coherent; artifact-presence status alone is insufficient.

## Open Questions

None. Company-copy selection is fail-closed to neutral, unavailable panelist details use complete neutral handoff copy, and external remediation remains a separately authorized transaction.

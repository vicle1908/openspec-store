## Why

The keynote needs one central, durable source of record for delivery requirements and acceptance while its Git-tracked implementation and evidence remain in the dedicated `ntu-keynote` repository outside this store's native edit root.

Lê Khánh Vinh (Solutions Architect at Viettel, NTU alumnus 2006–2010) will deliver the 10–15 minute opening keynote **“AI Vượt Qua Trào Lưu — Từ Bức Tranh Vĩ Mô Đến Giá Trị Thực Cho Doanh Nghiệp”** at an NTU alumni event immediately before a roundtable. The deliverable must be a stage-ready, fully Vietnamese, offline HTML presentation that preserves the organizer's three-act narrative, factual qualifiers, professional visual direction, accessibility, venue resilience, and auditable release evidence.

## What Changes

### Planning, implementation, and acceptance ownership

- Keep this central change in `/Users/androidteam/Developer/openspec-store` as the sole OpenSpec planning, requirements, task, acceptance, validation, and archive lifecycle for the keynote's identity, content, runtime, visuals, evidence, and release gates.
- Treat implementation, executable checks, private evidence, release packaging, rehearsal, release commits, and tag creation outside this store as separately authorized external orchestration. OpenSpec 1.10 binds this change's native `allowedEditRoots` to the central planning root; central apply does **not** authorize any external implementation write.
- Treat any external or historical local OpenSpec artifact only as a read-only migration or evidence input. No local OpenSpec `status`, `validate`, `apply`, `archive`, task completion, or same-named lifecycle has independent authority for this change or contributes central acceptance state.
- Preserve one-way authority: external implementation and immutable evidence must satisfy the centrally approved proposal, six specs, design, and tasks; external artifacts may not relax, replace, or approve central requirements. A material content, visual, runtime, evidence, or release change must first be approved in the applicable central planning artifact, then implemented through a separately authorized external transaction.
- Preserve relevant histories without copying, deleting, or executing an external same-named OpenSpec change, and do not infer implementation, evidence, task, or release completion from central artifact status.

### Keynote identity and narrative contract

- Deliver exactly 17 audience-visible Vietnamese slides in three acts, preserving slide count, order, mandatory content, and distinct narrative jobs.
- Preserve the exact 765-second (12:45) full route and exact 600-second (10:00) short route. The short route visits 15 slides and skips only slides 4 and 8.
- **Act 1 — Bức tranh vĩ mô (0:00–3:45):** title and NTU alumni identity; two-question audience hook; PwC's modeled 2030 global potential of USD 15.7 trillion / +14% GDP; Gartner's forecasted agentic shift from effectively 0% to at least 15% of daily work decisions and from under 1% to 33% of enterprise software by 2028; Nghị quyết 57's top-three ASEAN target for AI research and development by 2030; and Google/Access Partnership's modeled Vietnam opportunity of USD 79.3 billion, approximately 12% of GDP by 2030.
- **Act 2 — Khoảng cách giữa phong trào và giá trị (3:45–10:40):** an explicitly illustrative iceberg bridge; three independent slide-7 contexts from MIT NANDA—the 95% finding about organizations in the analyzed population, the 5% finding about integrated AI pilots that generated substantial value, and the USD 30–40 billion figure only as separate directional investment context, with distinct populations, units, qualifiers, and no complementary or shared-denominator encoding; Gartner's forecast that **hơn 40%** of agentic-AI projects will be cancelled by the end of 2027; the speaker's transferable three-layer journey from ChatGPT adoption/training, through internal-LLM lessons for customer support and call-center work, to multi-agent/Agentic AI operational discipline; and the WEF projections of 170 million jobs created, 92 million displaced, net +78 million, and 39% of skills changing by 2030 across all macro drivers. The unifying thesis remains that value comes from reducing manual effort and automating repetitive processes rather than adopting technology for its own sake.
- **Act 3 — Tư duy lãnh đạo và bàn tròn (10:40–12:45):** distinguish organizations that convert AI effort into P&L value; present three complete leadership mindsets; retain the 39% WEF skills figure as a concise callback in one of slide 16's three statistically anchored roundtable prompts, with full moderator wording in notes/cue-sheet data; and reserve slide 17 for a distinct 30-second NTU alumni handoff without repeating the questions.
- Preserve the contextual McKinsey 2023 estimate of USD 2.6–4.4 trillion annual GenAI potential when used in planning or notes, subject to the same source registration and qualifier controls as every other factual claim.

### Offline runtime and venue package

- Implement the deck as one directly opened `index.html` with inline CSS and vanilla JavaScript, local relative assets, no server, no build step, no CDN, no live network, and no production runtime dependency.
- Author on a fixed 1280×720 stage with a 5% safe area and centered, non-distorting letterbox scaling qualified at 16:9, 16:10, and 4:3 viewports. Do not claim pixel-identical output across browsers, operating systems, projectors, display scaling, or overscan conditions.
- Bundle only the transparent 1304×512 NTU logo and Be Vietnam Pro Vietnamese-subset WOFF2 fonts at weights 400, 600, and 800. The deck must remain legible without the local font files.
- Provide deterministic keyboard, click, and standard-clicker navigation; Home/End and direct access; repeat protection; full/short route state; a canonical URL-fragment reload state compatible with Safari `file://`; safe invalid-state fallback; and reset to full mode slide 1 without depending on `localStorage`.
- Provide Vietnamese speaker notes with timing windows and delivery cues, an audience-visible mirrored-display warning, active-slide synchronization, Escape close, slide counter/progress, visible route mode, and interaction rules that prevent notes or control clicks from advancing the deck.
- Preserve exactly two attention animations—the PwC counter and MIT emphasis—plus a restrained base transition. Revisit replay, print final states, and `prefers-reduced-motion` final states are required.
- Provide semantic active-slide exposure, keyboard-only operation, visible focus, non-disruptive slide announcements, inactive-slide focus suppression, meaningful logo alternative text, contrast of at least 4.5:1 for normal text and 3:1 for large text, non-color meaning, safe-area fit, Vietnamese glyph coverage, accessible visual reading order, and concise Vietnamese text equivalents for meaningful visuals. Decorative vectors remain hidden from assistive technology.
- Ship an exact seven-file public venue package: `index.html`, `README.md`, `keynote-fallback.pdf`, `assets/ntu-logo.png`, and `assets/fonts/be-vietnam-pro-{400,600,800}.woff2`. Its canonical digest SHALL use `ntu-keynote-package-sha256-v1`: normalize the seven paths to the listed POSIX spellings, sort them by UTF-8 path bytes, initialize the SHA-256 stream with `NTU_KEYNOTE_PACKAGE_V1\0`, then for each entry append the unsigned 64-bit big-endian path-byte length, path UTF-8 bytes, unsigned 64-bit big-endian file-byte length, and raw file bytes. Evidence SHALL record the algorithm/version, the seven actual per-file SHA-256 values, and the deterministic test vector `a.txt`=`41`, `dir/b.bin`=`00ff`, whose package digest is `b13c66f843d56fdd261d6d57faade59c68f1a349d8f5a467657420cc396ab1ad`. The PDF is pre-generated, exactly 17 pages, preserves backgrounds and final animation values, and excludes notes and controls.

### Visual identity and visual-content contract

- Preserve NTU Blue `#181C62` and NTU Red `#D71440` from the official Quick Brand Guide. Use the projection-adapted dark stage background `#0D1038`, high-contrast light text, and NTU Red as the disciplined accent for headline statistics and narrative alarm moments.
- Give every slide one dominant visual that reinforces its existing narrative job without changing content authority, timing, or factual scope.
- Use project-authored inline SVG/CSS diagrams, source-faithful data visualizations, editorial vector illustrations, and accessible iconography inside `index.html`; add no public file or runtime dependency.
- Do not encode forecasts, modeled potential, or directional estimates as observed facts. Any meaningful length, area, position, sign, proportion, label, or comparison must match the registered source value and qualifier. Metaphors such as the iceberg remain explicitly illustrative and not to scale.
- Preserve source and visual-provenance traceability for every audience-visible factual or meaningful visual element, including authorship/license basis and a concise Vietnamese accessible equivalent where required.

### Factual, company-copy, and release evidence

- Preserve the exact scope and uncertainty of all factual claims: PwC, Gartner, Google/Access Partnership, and WEF values remain projections or modeled potential; MIT NANDA's 95% organization finding and 5% integrated-pilot finding retain their distinct registered populations, units, and qualifiers and MUST NOT be presented as complementary parts of one denominator; the USD 30–40 billion figure remains separate directional investment context; Gartner remains **hơn 40%**, not an exact 40%; Nghị quyết 57 remains scoped to AI research and development; and WEF workforce values remain across all macro drivers rather than AI alone.
- Make neutral, company-safe copy the release default. Viettel/company identity, infrastructure, operations, customer context, or metrics may be selected only when a named approval record covers the exact released wording by SHA-256. Rejection, no response, missing coverage, or a hash mismatch must leave the neutral variant selected.
- Retain durable, machine-readable private evidence for factual and visual provenance, authorship/license basis, approvals, static validation, Safari and Chrome `file://` qualification, accessibility, contrast, reduced motion, viewport and PDF checks, representative screenshots, copied-folder/offline rehearsal, actual presenting-laptop/projector/clicker rehearsal, and 30-second PDF fallback reachability.
- Bind all content-dependent evidence to one exact candidate. Any change to public `index.html` bytes invalidates the PDF, public-package digest, browser/accessibility/viewport/PDF evidence, screenshots, checksums, release manifest, and copied-folder rehearsal until regenerated or rerun.
- Keep source, approval, license, planning, scripts, tests, Git/worktree metadata, screenshots, and private evidence out of the public venue package.
- Use non-self checksums, an evidence-base commit, the immutable public package digest, and the fixed intended annotated ref `refs/tags/ntu-ai-keynote-v1.0.0`. Never embed the SHA of the commit containing the manifest inside that manifest. External acceptance must verify an annotated tag object at that exact ref and derive the authoritative final commit by peeling `refs/tags/ntu-ai-keynote-v1.0.0^{commit}`.
- Require strict central planning validation, coherent external executable artifacts, fresh automated evidence, resolved approval-or-neutral selection, and the actual venue rehearsal before the release manifest may say `released`. Central planning completion alone is not implementation or release readiness.

## Capabilities

### New Capabilities

- `offline-keynote-runtime`: Direct offline `file://` launch, fixed-stage scaling, full/short navigation, fragment recovery, notes, motion behavior, local assets, print behavior, and self-contained inline visual rendering.
- `keynote-content-and-language`: The exact 17-slide three-act content contract, Vietnamese audience and notes policy, one dominant visual job per slide, factual framing, leadership mindsets, and concise roundtable copy.
- `timing-and-roundtable-handoff`: Exact 765-second full and 600-second short route arithmetic, route behavior, notes timing, glance-readable visuals within existing durations, and distinct question and handoff responsibilities.
- `factual-provenance-and-approval`: Source and visual-provenance registration, qualifier and visual-encoding fidelity, neutral-copy default, SHA-bound exact-copy company approval, and unresolved-content release gates.
- `accessible-stage-presentation`: Semantic active-slide exposure, keyboard operation, accessible visual reading order and text equivalents, contrast, non-color cues, visible focus, reduced motion, system-font fallback, and accessible print behavior.
- `browser-qualification-and-release-evidence`: Safari and Chrome qualification, inline-SVG and viewport evidence, 17-page PDF fallback, public-package isolation, evidence invalidation and freshness, copied-folder and venue rehearsals, checksums, manifest, and final release gate.

These six capabilities are centrally owned requirements and acceptance contracts. The former `skip_specs` exemption has been removed, and all six central delta specs are active and strictly valid; implementation and executable evidence remain separately orchestrated outside the central OpenSpec lifecycle.

OpenSpec artifact status reports planning-file presence, not implementation readiness, evidence freshness, archive readiness, or release readiness; only the central acceptance ledger may record those outcomes.

### Modified Capabilities

None.

## Impact

- **Sole OpenSpec lifecycle root:** `/Users/androidteam/Developer/openspec-store/openspec/changes/add-ntu-ai-keynote-deck/` owns approved intent, requirements, design, tasks, acceptance boundaries, validation, archive disposition, and central completion state. Applicable lifecycle commands must explicitly select `--store openspec-store`.
- **External orchestration boundary:** implementation, executable verification, private evidence, release packaging, rehearsal, release commits, and tag creation remain separately authorized external work. Central native apply cannot authorize those writes, and historical local OpenSpec artifacts are read-only migration or evidence inputs only.
- **Public delivery surface:** exactly the seven allowlisted venue files copied to USB or the presenting laptop and opened in modern installed Safari or Chrome via `file://`, with a PDF viewer as fallback.
- **Human gates:** exact-copy Viettel approval or proven neutral copy, and an actual presenting-laptop/projector/external-display/real-clicker rehearsal, remain mandatory for release.
- **Authority and history boundary:** central planning/task/validation/archive state is authoritative for this change; external commits, evidence, and the fixed release tag are immutable inputs to central read-only acceptance, not a second OpenSpec lifecycle.
- **Dependencies:** no runtime dependency is added. External orchestration uses its own authorization and commits and must never represent central `allowedEditRoots` as covering an external implementation repository.

## Non-Goals

- No transfer of native OpenSpec apply authorization from the central planning root to `ntu-keynote`; OpenSpec 1.10 has no linked implementation-root capability.
- This authoritative central artifact set changes planning and acceptance contracts only; it performs no external implementation, evidence generation or regeneration, rehearsal, release-status mutation, release commit, or tag mutation.
- Central acceptance execution remains 0/12 until the central tasks run and record their required immutable evidence, gate results, decision, and closure.
- No video/audio, live demo, analytics, internet-dependent feature, network service, CDN, framework, bundler, slide CMS, presenter-window protocol, or runtime-generated chart.
- No stock photography, third-party icon library or icon font, emoji-dependent iconography, external image/SVG reference, extra venue file, or additional animation beyond the two attention moments and restrained base transition.
- No bilingual or dual-column deck; official source titles and approved technical terms may remain untranslated only under the Vietnamese language policy.
- No visual encoding that strengthens a forecast, implies causation, or presents an illustrative metaphor as measured data.
- No confidential Viettel metric, customer detail, internal infrastructure claim, or company attribution without exact-copy approval.
- No unresolved placeholder, conditional audience copy, empty logo/name slot, or release claim based only on undocumented manual testing.
- No private `openspec/`, `evidence/`, `tests/`, `scripts/`, `.git*`, `.omp/`, worktree metadata, source register, approval proposal, or license record in the venue package.

## Why

The keynote needs one central, durable source of record for delivery requirements and acceptance while its Git-tracked implementation and evidence remain in the dedicated `ntu-keynote` repository outside this store's native edit root.

Lê Khánh Vinh (Solutions Architect at Viettel, NTU alumnus 2006–2010) will deliver the 10–15 minute opening keynote **“AI Vượt Qua Trào Lưu — Từ Bức Tranh Vĩ Mô Đến Giá Trị Thực Cho Doanh Nghiệp”** at an NTU alumni event immediately before a roundtable. The deliverable must be a stage-ready, fully Vietnamese, offline HTML presentation that preserves the organizer's three-act narrative, factual qualifiers, professional visual direction, accessibility, venue resilience, and auditable release evidence.

## What Changes

### Planning, implementation, and acceptance ownership

- Keep this central change in `/Users/androidteam/Developer/openspec-store` as the authoritative planning and acceptance record for the keynote's identity, content, runtime, visuals, evidence, and release gates.
- Keep implementation, executable checks, private evidence, release packaging, and the annotated release tag in the Git repository at `/Users/androidteam/Developer/ntu-keynote`.
- Treat work in `ntu-keynote` as explicit external orchestration. OpenSpec 1.10 binds this change's native `allowedEditRoots` to the central planning root; central apply does **not** authorize edits in `ntu-keynote`. Each root therefore uses its own OpenSpec context, validation, Git history, path-limited commit, and approval gate.
- Preserve one-way authority: the repo-local executable change implements and proves the centrally approved requirements; it does not independently relax, replace, or approve them. A material content, visual, runtime, evidence, or release change must first be approved in the applicable central planning artifact, then reconciled separately into the executable local artifacts and implementation.
- Preserve both histories. Do not copy or delete either same-named change as part of this proposal update, and do not infer local task or release completion from central artifact status.

### Keynote identity and narrative contract

- Deliver exactly 17 audience-visible Vietnamese slides in three acts, preserving slide count, order, mandatory content, and distinct narrative jobs.
- Preserve the exact 765-second (12:45) full route and exact 600-second (10:00) short route. The short route visits 15 slides and skips only slides 4 and 8.
- **Act 1 — Bức tranh vĩ mô (0:00–3:45):** title and NTU alumni identity; two-question audience hook; PwC's modeled 2030 global potential of USD 15.7 trillion / +14% GDP; Gartner's forecasted agentic shift from effectively 0% to at least 15% of daily work decisions and from under 1% to 33% of enterprise software by 2028; Nghị quyết 57's top-three ASEAN target for AI research and development by 2030; and Google/Access Partnership's modeled Vietnam opportunity of USD 79.3 billion, approximately 12% of GDP by 2030.
- **Act 2 — Khoảng cách giữa phong trào và giá trị (3:45–10:40):** an explicitly illustrative iceberg bridge; the MIT NANDA finding that 95% of analyzed GenAI pilots showed no measurable P&L impact at evaluation and its directional USD 30–40 billion investment estimate; Gartner's forecast that more than 40% of agentic-AI projects will be cancelled by the end of 2027; and the speaker's transferable three-layer journey from ChatGPT adoption/training, through internal-LLM lessons for customer support and call-center work, to multi-agent/Agentic AI operational discipline. The unifying thesis remains that value comes from reducing manual effort and automating repetitive processes rather than adopting technology for its own sake.
- **Act 3 — Tư duy lãnh đạo và bàn tròn (10:40–12:45):** distinguish organizations that convert AI effort into P&L value; preserve the WEF projections of 170 million jobs created, 92 million displaced, net +78 million, and 39% of skills changing by 2030 across all macro drivers; present three complete leadership mindsets; give slide 16 three concise, statistically anchored roundtable prompts with full moderator wording in notes/cue-sheet data; and reserve slide 17 for a distinct 30-second NTU alumni handoff without repeating the questions.
- Preserve the contextual McKinsey 2023 estimate of USD 2.6–4.4 trillion annual GenAI potential when used in planning or notes, subject to the same source registration and qualifier controls as every other factual claim.

### Offline runtime and venue package

- Implement the deck as one directly opened `index.html` with inline CSS and vanilla JavaScript, local relative assets, no server, no build step, no CDN, no live network, and no production runtime dependency.
- Author on a fixed 1280×720 stage with a 5% safe area and centered, non-distorting letterbox scaling qualified at 16:9, 16:10, and 4:3 viewports. Do not claim pixel-identical output across browsers, operating systems, projectors, display scaling, or overscan conditions.
- Bundle only the transparent 1304×512 NTU logo and Be Vietnam Pro Vietnamese-subset WOFF2 fonts at weights 400, 600, and 800. The deck must remain legible without the local font files.
- Provide deterministic keyboard, click, and standard-clicker navigation; Home/End and direct access; repeat protection; full/short route state; a canonical URL-fragment reload state compatible with Safari `file://`; safe invalid-state fallback; and reset to full mode slide 1 without depending on `localStorage`.
- Provide Vietnamese speaker notes with timing windows and delivery cues, an audience-visible mirrored-display warning, active-slide synchronization, Escape close, slide counter/progress, visible route mode, and interaction rules that prevent notes or control clicks from advancing the deck.
- Preserve exactly two attention animations—the PwC counter and MIT emphasis—plus a restrained base transition. Revisit replay, print final states, and `prefers-reduced-motion` final states are required.
- Provide semantic active-slide exposure, keyboard-only operation, visible focus, non-disruptive slide announcements, inactive-slide focus suppression, meaningful logo alternative text, contrast of at least 4.5:1 for normal text and 3:1 for large text, non-color meaning, safe-area fit, Vietnamese glyph coverage, accessible visual reading order, and concise Vietnamese text equivalents for meaningful visuals. Decorative vectors remain hidden from assistive technology.
- Ship an exact seven-file public venue package: `index.html`, `README.md`, `keynote-fallback.pdf`, `assets/ntu-logo.png`, and `assets/fonts/be-vietnam-pro-{400,600,800}.woff2`. The PDF is pre-generated, exactly 17 pages, preserves backgrounds and final animation values, and excludes notes and controls.

### Visual identity and visual-content contract

- Preserve NTU Blue `#181C62` and NTU Red `#D71440` from the official Quick Brand Guide. Use the projection-adapted dark stage background `#0D1038`, high-contrast light text, and NTU Red as the disciplined accent for headline statistics and narrative alarm moments.
- Give every slide one dominant visual that reinforces its existing narrative job without changing content authority, timing, or factual scope.
- Use project-authored inline SVG/CSS diagrams, source-faithful data visualizations, editorial vector illustrations, and accessible iconography inside `index.html`; add no public file or runtime dependency.
- Do not encode forecasts, modeled potential, or directional estimates as observed facts. Any meaningful length, area, position, sign, proportion, label, or comparison must match the registered source value and qualifier. Metaphors such as the iceberg remain explicitly illustrative and not to scale.
- Preserve source and visual-provenance traceability for every audience-visible factual or meaningful visual element, including authorship/license basis and a concise Vietnamese accessible equivalent where required.

### Factual, company-copy, and release evidence

- Preserve the exact scope and uncertainty of all factual claims: PwC, Gartner, Google/Access Partnership, and WEF values remain projections or modeled potential; MIT NANDA remains scoped to analyzed GenAI pilots and measurable P&L at evaluation; its USD 30–40 billion value remains directional; Nghị quyết 57 remains scoped to AI research and development; and WEF workforce values remain across all macro drivers rather than AI alone.
- Make neutral, company-safe copy the release default. Viettel/company identity, infrastructure, operations, customer context, or metrics may be selected only when a named approval record covers the exact released wording by SHA-256. Rejection, no response, missing coverage, or a hash mismatch must leave the neutral variant selected.
- Retain durable, machine-readable private evidence for factual and visual provenance, authorship/license basis, approvals, static validation, Safari and Chrome `file://` qualification, accessibility, contrast, reduced motion, viewport and PDF checks, representative screenshots, copied-folder/offline rehearsal, actual presenting-laptop/projector/clicker rehearsal, and 30-second PDF fallback reachability.
- Bind all content-dependent evidence to one exact candidate. Any change to public `index.html` bytes invalidates the PDF, public-package digest, browser/accessibility/viewport/PDF evidence, screenshots, checksums, release manifest, and copied-folder rehearsal until regenerated or rerun.
- Keep source, approval, license, planning, scripts, tests, Git/worktree metadata, screenshots, and private evidence out of the public venue package.
- Use non-self checksums, an evidence-base commit, the immutable public package digest, and the intended annotated tag `ntu-ai-keynote-v1.0.0`. Never embed the SHA of the commit containing the manifest inside that manifest; resolve the authoritative final commit externally from the annotated tag.
- Require strict central planning validation, coherent external executable artifacts, fresh automated evidence, resolved approval-or-neutral selection, and the actual venue rehearsal before the release manifest may say `released`. Central planning completion alone is not implementation or release readiness.

## Capabilities

### New Capabilities

- `offline-keynote-runtime`: Direct offline `file://` launch, fixed-stage scaling, full/short navigation, fragment recovery, notes, motion behavior, local assets, print behavior, and self-contained inline visual rendering.
- `keynote-content-and-language`: The exact 17-slide three-act content contract, Vietnamese audience and notes policy, one dominant visual job per slide, factual framing, leadership mindsets, and concise roundtable copy.
- `timing-and-roundtable-handoff`: Exact 765-second full and 600-second short route arithmetic, route behavior, notes timing, glance-readable visuals within existing durations, and distinct question and handoff responsibilities.
- `factual-provenance-and-approval`: Source and visual-provenance registration, qualifier and visual-encoding fidelity, neutral-copy default, SHA-bound exact-copy company approval, and unresolved-content release gates.
- `accessible-stage-presentation`: Semantic active-slide exposure, keyboard operation, accessible visual reading order and text equivalents, contrast, non-color cues, visible focus, reduced motion, system-font fallback, and accessible print behavior.
- `browser-qualification-and-release-evidence`: Safari and Chrome qualification, inline-SVG and viewport evidence, 17-page PDF fallback, public-package isolation, evidence invalidation and freshness, copied-folder and venue rehearsals, checksums, manifest, and final release gate.

These capabilities are centrally owned requirements and acceptance contracts. Their delta specs will be created in a separately approved planning step after `skip_specs: true` is removed from `.openspec.yaml`; implementation and executable evidence remain externally orchestrated in the dedicated `ntu-keynote` repository.

### Modified Capabilities

None.

## Impact

- **Central planning root:** `/Users/androidteam/Developer/openspec-store/openspec/changes/add-ntu-ai-keynote-deck/` owns approved intent, requirements, acceptance boundaries, ownership decisions, and historical archive disposition.
- **External implementation root:** `/Users/androidteam/Developer/ntu-keynote` owns implementation, executable local OpenSpec artifacts, verification tooling, private evidence, release packaging, and release tag. Central native apply cannot authorize edits there.
- **Public delivery surface:** exactly the seven allowlisted venue files copied to USB or the presenting laptop and opened in modern installed Safari or Chrome via `file://`, with a PDF viewer as fallback.
- **Human gates:** exact-copy Viettel approval or proven neutral copy, and an actual presenting-laptop/projector/external-display/real-clicker rehearsal, remain mandatory for release.
- **History and collision boundary:** the same change name may exist in the central and local roots, but every lifecycle command must explicitly select its intended root/store. Their task counts, validation, commits, evidence, and archives remain independent.
- **Dependencies:** no runtime dependency is added. External orchestration may coordinate two repositories, but it must use separate root-scoped commands and commits and must never represent central `allowedEditRoots` as covering the implementation repository.

## Non-Goals

- No transfer of native OpenSpec apply authorization from the central planning root to `ntu-keynote`; OpenSpec 1.10 has no linked implementation-root capability.
- No metadata, design, task, spec-file, implementation, or evidence change in this proposal-only correction. Removing `skip_specs: true` and creating the six central delta specs require a later, separate approval gate.
- No implementation, evidence regeneration, release-status change, task reconciliation, archive, or approval of unreviewed local amendments as part of this proposal-only update.
- No video/audio, live demo, analytics, internet-dependent feature, network service, CDN, framework, bundler, slide CMS, presenter-window protocol, or runtime-generated chart.
- No stock photography, third-party icon library or icon font, emoji-dependent iconography, external image/SVG reference, extra venue file, or additional animation beyond the two attention moments and restrained base transition.
- No bilingual or dual-column deck; official source titles and approved technical terms may remain untranslated only under the Vietnamese language policy.
- No visual encoding that strengthens a forecast, implies causation, or presents an illustrative metaphor as measured data.
- No confidential Viettel metric, customer detail, internal infrastructure claim, or company attribution without exact-copy approval.
- No unresolved placeholder, conditional audience copy, empty logo/name slot, or release claim based only on undocumented manual testing.
- No private `openspec/`, `evidence/`, `tests/`, `scripts/`, `.git*`, `.omp/`, worktree metadata, source register, approval proposal, or license record in the venue package.

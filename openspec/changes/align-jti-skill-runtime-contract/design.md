## Context

The JTI contract is split across three layers:

```text
ticket-intelligence-core spec
          │ intended v2.0 contract
          ▼
jira-skill runtime ───────────► jira-epic-report
       │                       jira-daily-reports
       │                       webhook-receiver
       ▼
skill metadata + generated indexes
```

The specification and skill were updated to describe the v2.0 RCA taxonomy and 28-column Sheets output, but the runtime still has `BundleVersion v1.2`, the ten-entry RCA catalog, and 26 classification columns. The runtime has only partially adopted v2: `RootCauseSignal` contains `four_p_lens` and `secondary_categories`, while `IssueSummary`, Sheets rendering, versioning, taxonomy names, and sentinel behavior remain inconsistent. The three consumer repos use editable `jira-skill` dependencies, so the contract can be migrated atomically in the workspace.

The skill loader separately warns when a description exceeds 1,024 bytes. Its generated index parser accepts only bare `>` and `|` block scalars, causing descriptions declared as `>-` to be indexed as the literal marker. The skill itself is also too large for a reliable routing document and duplicates detailed contract material better suited to reference documentation.

The index audit found four competing/stale surfaces: `.codex/skills-index.json` and both Markdown indexes report 103 skills while 131 valid direct-child skill directories are present, `.agents/skills/_regenerate_index.py` writes only one Markdown index through a second parser, and `config/codex/skills-index.json` is an unreferenced 75-skill snapshot. A 132nd `SKILL.md` exists directly under `.agents/skills/`; it is byte-for-byte identical to `.agents/skills/openspec-update-change/SKILL.md` and violates the directory-owned layout. The current `skill-validation-check.sh` checks only file age and directory count; it does not validate frontmatter, placement, duplicate names, or index consistency.

The OpenSpec audit also found overlapping baseline requirements. `jti-classification-accuracy` already describes most of v2 but uses stale evidence positions, calls the executable survey a 65-case set even though `TestRcaSurveyPrecision.SURVEY` contains 45 cases, and assigns lens ownership to a different table; `impact-sheet-integration` still requires current `analyze_snapshot()` output to be v1.2 and contains obsolete Module Source positions; `fix-rca-fix-status-detection` still requires nine removed categories. These are migrated by dedicated deltas in this change rather than treated as historical prose. All five capabilities declared by the proposal now have concrete delta files; this explicit coverage check is necessary because strict syntax validation alone does not detect a missing capability delta.

GitNexus impact analysis found LOW risk for each targeted symbol, with the following exact upstream scope:

- `BundleVersion`: 5 dependencies, including analyzer, enrichment, Sheets, package exports, and CLI.
- `detect_rca`: 3 callers across analyzer and the filter pipeline.
- `RootCauseSignal`: 7 importing/consuming files, including RCA, bundle, analyzer, enrichment, Sheets, and exports.
- `SheetsWriter.write_bundle`: 9 upstream symbols and the `analyze_filter` execution process, including two classification scripts.

## Goals / Non-Goals

**Goals:**

- Make the runtime, OpenSpec contract, skill guidance, generated indexes, and consumer tests describe the same v2.0 contract.
- Preserve deterministic ticket/SCM analysis while making the eight RCA categories, 4P lens, sentinel, confidence mapping, and secondary-cause output explicit.
- Make the Sheets header and row schemas a single runtime-owned definition with 28 columns.
- Keep all consumer adapters thin and compatible with the shared bundle.
- Make skill metadata parsing tolerant of valid YAML block scalar modifiers and enforce the loader description budget.
- Add regression coverage that fails when runtime and documentation-facing contract metadata drift again.
- Leave no contradictory current-version/category/column requirement in adjacent JTI capability specs.

**Non-Goals:**

- No new package or service dependency.
- No change to Jira authentication, collection, filter discovery, dashboard commands, or policy overlays.
- No full source-code semantic or LLM-based RCA analysis.
- No scheduling, deployment, database, launchd, or Docker migration.

## Decisions

### 1. Ship the existing v2.0 target rather than downgrade the documentation

The baseline `ticket-intelligence-core` spec and current skill already define v2.0, and the runtime has partially introduced the v2 fields. The implementation will finish that contract instead of creating a second v1.2 documentation track. The bundle version will be bumped to `v2.0` only after the taxonomy, fields, and Sheet output are complete and tested.

**Alternative considered:** Roll the skill and spec back to v1.2 and retain the ten-category runtime. Rejected because it would discard the already-approved v2 taxonomy and leave the partially shipped fields without a coherent destination.

### 2. Keep runtime constants as the executable source of truth

- `BundleVersion` in `analysis/bundle.py` owns the emitted version.
- `RCA_PATTERNS` and its catalog metadata own category order, priorities, prevention actions, and 4P lenses.
- `CLASSIFICATION_COLUMNS` in `analysis/sheets_writer.py` owns the header order.
- `RootCauseSignal` owns the typed primary signal surface, while `IssueSummary` mirrors the lens and secondary fields per issue with backward-safe defaults.
- Tests assert these constants and the serialized bundle shape; prose documentation explains them but does not become a second parser or configuration source.

The catalog entry itself will be the only RCA lens mapping. The duplicate `RCA_4P_BUCKET` table will be removed; `detect_rca()` will read `best_match["four_p_lens"]`, and a priority lookup derived once from the catalog will order secondary categories. The skill will reference the canonical contract and operational commands, while detailed taxonomy and column explanations move to a reference document that can be updated alongside the runtime.

The exact v2 lens mapping is Crash → Plant, UI Layout → Plant, Wrong Data → Plant, Text / Font → Plant, Feature Not Working → Procedures, 3rd Party → Policies, Performance → Plant, and Other / Unclassified → `None`. `RootCauseSignal.four_p_lens` will use `Literal["People", "Procedures", "Policies", "Plant"] | None`; `RCAPatternEntry` will use the same concrete lens type. `People` remains an allowed framework value for forward-compatible typed data even though no v2 concrete category currently maps to it. Runtime docstrings and evidence notes will be updated so they no longer claim that generic code hints increase RCA confidence or that secondary priorities are descending.

### 3. Make v2 a deliberate breaking release

The v2 taxonomy removes four category names and changes their routing, so persisted or downstream consumers that key on v1 category strings cannot silently be treated as compatible. `BundleMeta.version` remains the compatibility signal. The editable consumers will continue importing the shared package rather than pinning duplicate models; their tests will assert the expected v2 contract or compare against the exported `BUNDLE_VERSION` where the adapter is version-agnostic.

Existing v1 fixtures remain useful as migration inputs but will not be relabeled as v2 fixtures. New v2 fixtures will cover every category, the distinct unclassified sentinel, multiple secondary categories, and the 28-column output.

### 4. Normalize RCA semantics before changing the version

The classifier will:

- use the seven concrete categories plus `Other / Unclassified` sentinel in the documented priority order;
- preserve the existing ticket-grounded and lightweight SCM evidence boundaries;
- map every concrete category to its specified 4P lens and map the sentinel to `None`;
- compute secondary categories by category, not by matched regex, then sort by priority and cap at three;
- use the v2 confidence ladder in severity scoring.

The category migration is explicit:

| v1.2 category | v2.0 destination |
|---|---|
| Crash / ANR / Force Close | Crash / ANR / Force Close |
| Wrong Data / Incorrect Value | Wrong Data / Incorrect Value |
| Silent Exit / No Feedback | Feature Not Working / Missing |
| Text / Font Display | Text / Font Display |
| UI Layout / Visual Defect | UI Layout / Visual Defect |
| Performance / Slow Loading | Performance / Slow Loading |
| Authentication / Authorization | 3rd Party Issue (WebView, API, SDK) |
| Network / API Connectivity | 3rd Party Issue (WebView, API, SDK) |
| Feature Not Working / Missing | Feature Not Working / Missing |
| General UI/UX Polish | UI Layout or Text/Font only when a specific retained pattern matches; otherwise Other / Unclassified |

Base RCA confidence is fixed by the primary v2 category (`0.7`, `0.6`, `0.5`, `0.4`, or `0.0`). Matching multiple categories will not raise confidence. Generic code-hint presence will not raise RCA confidence either because code evidence already contributes separately to the composite severity score; hints may still add evidence-backed prevention actions. This avoids double counting and makes the documented ladder executable.

The existing 45-case precision survey will be migrated through an explicit v1.2-to-v2.0 expected-category mapping. Its gate becomes exact expected-output accuracy across the full executable survey, including expected unclassified results, rather than relying on the stale 65-case label or excluding unclassified rows from the denominator. This prevents a classifier from meeting the threshold by returning the sentinel too often. Any future expansion to 65 cases must add the missing executable fixtures rather than changing only prose.

Current expected-bundle fixtures will be preserved as explicitly named v1.2 migration inputs and loaded through `TicketIntelligenceBundle.from_json()` to prove backward-safe defaults. Separate v2.0 expected bundles will become the current analyzer golden outputs; implementation must not overwrite v1.2 fixtures in place and relabel them as v2.

These decisions prevent the current collision where the catch-all category and unclassified sentinel share a string, prevent duplicate secondary entries when several patterns within one category match, and remove confidence inflation based on keyword density.

### 5. Treat Sheets output and clearing as one positional compatibility surface

The writer will append `RCA 4P Lens` and `Secondary RCA` at positions 26 and 27 and construct each issue as a mapping keyed by `CLASSIFICATION_COLUMNS`, then materialize the row in header order. This removes the current split between a 22-cell literal and a four-cell `extend()` tail. The complete invariant is:

- `RCA Matched Text`: 10
- `Analysis Evidence`: 13
- `MR Links`, `Files Changed`, `At-Risk Modules`, `Module Source`: 22–25
- `RCA 4P Lens`, `Secondary RCA`: 26–27

The Classification clear range will be derived from the 28-column schema and resolve to `A1:AB1000` before each write. The Summary range remains independent. This is required because `AA:AB` otherwise retain stale values during partial writes or rollback. Tests will verify length, exact positions, derived clear range, empty/sentinel behavior, separator formatting, hyperlink column lookup, and row alignment. Existing tab names, hyperlinks, Summary tab behavior, and output routing remain unchanged.

### 6. Make one testable skill-index implementation deterministic and budget-aware

The embedded parser will be extracted to `config/codex/scripts/build_skills_index.py` with `--check` and `--write` modes and standard-library tests under `config/codex/scripts/tests/`. `build-skills-index.sh` remains the operator-facing wrapper and invokes it through `uv run --no-project python`; `skill-validation-check.sh` delegates semantic validation to `--check` while preserving its hook-facing JSON result.

Discovery accepts exactly `.agents/skills/<directory>/SKILL.md`. It separately detects and rejects root-level or more deeply nested `SKILL.md` files, missing directory-owned files, and duplicate normalized skill names. The parser accepts the supported scalar forms `>`, `>-`, `>+`, `|`, `|-`, and `|+`, then normalizes all description whitespace to the single-line index representation. It validates every discovered skill before writing any index and reports the skill path, byte count, and remediation when a description exceeds 1,024 UTF-8 bytes. A soft warning threshold flags descriptions above 800 bytes without failing generation.

Generation is two-phase: discover, parse, validate, and render all outputs in memory; write temporary files; then replace the canonical JSON and both Markdown companions only after every output is ready. `--check` compares semantic payloads and all three entry sets without writing. `--write` preserves the existing generated timestamp and file mtimes when semantic content is unchanged; when content changes it assigns one shared UTC timestamp and atomically replaces all three outputs. This makes repeated clean runs idempotent while retaining useful generation metadata.

The exact duplicate root-level `.agents/skills/SKILL.md`, `.agents/skills/_regenerate_index.py`, and unreferenced `config/codex/skills-index.json` will be removed after their lack of consumers is rechecked. The canonical generator must produce 131 unique directory-owned entries on the audited workspace rather than preserving the stale count of 103. Both existing matcher scripts must continue consuming the unchanged JSON field schema.

The JTI skill frontmatter will use a short routing description and move verbose contract history into the body/reference documentation. Its allowed command surface will remove direct `python` and `pytest` shells in favor of `uv`, and every executable example will retain the workspace's `uv run` convention.

### 7. Verify in dependency order, without live credentials

Verification uses deterministic fixtures and mocked Sheets/consumer adapters first, then the focused analysis suites and cross-repo parity suites. No live Jira, GitLab, or Sheets call is required for acceptance. The package's existing `uv` environments remain the only execution path. A focused `jira-epic-report` parity invocation uses `--no-cov`; its repository-wide 80% coverage gate is evaluated only by the full suite. Acceptance of `uv run jira-skill version` asserts the `Bundle version: v2.0` line independently of the package/CLI version, which remains a separate release concern.

The consumer audit found no RCA category-name or Classification-position branching in `jira-epic-report`, `jira-daily-reports`, or `webhook-receiver`. Only `webhook-receiver/tests/unit/test_analysis_adapter.py` hardcodes a v1 prefix. Therefore consumer work is a compatibility-matrix verification plus explicit `BUNDLE_VERSION == "v2.0"` assertions in each parity suite; new runtime version guards are not added where no deserialization boundary exists. GitNexus change detection and Git status review run separately inside every changed repository, including `tdt-meta`.

Change-specific strict validation is the release gate for this plan and currently passes with 21 deltas across the five declared capabilities. Workspace-wide `openspec validate --all --strict --no-interactive` currently reports 75 unrelated pre-existing baseline-spec failures while all active changes pass. Implementation MUST capture and compare that failure set, introduce no new workspace validation failure, and keep this change valid; repairing unrelated baseline specs is outside this change.

## Risks / Trade-offs

- **[Risk] Existing consumers or persisted fixtures expect v1 category names.** → **Mitigation:** emit `v2.0`, update editable consumer tests, retain explicit version metadata, and document the migration boundary rather than silently translating old labels.
- **[Risk] Adding two Sheet columns changes positional consumers.** → **Mitigation:** append only at the specified tail positions, keep tab names stable, and assert headers/rows together in writer tests.
- **[Risk] Existing Sheet cells in AA:AB survive rollback or a short write.** → **Mitigation:** clear through AB from the same schema width before writing and cover the exact clear range in tests.
- **[Risk] RCA pattern relocation changes classification results.** → **Mitigation:** add one fixture per category plus regression cases for moved auth/network/silent-exit patterns and the unclassified sentinel.
- **[Risk] Fixed v2 confidence changes composite severity ordering.** → **Mitigation:** snapshot the v1 ordering, add v2 score/rank fixtures, and test the documented weighted formula and tie-break order.
- **[Risk] Skill index regeneration overwrites unrelated catalog edits or creates timestamp-only churn.** → **Mitigation:** preserve the current generated-file ownership, use semantic `--check`, make unchanged `--write` idempotent, regenerate only from the canonical script, and review the generated diff for all three index outputs.
- **[Risk] Adjacent baseline specs continue to demand v1 behavior.** → **Mitigation:** include deltas for all four affected JTI capabilities and validate the merged contract, not only this change's file syntax.
- **[Risk] The combined change spans metadata and a Python runtime.** → **Mitigation:** keep application edits behind this active OpenSpec change, run impact/detect-changes checks, and verify each repo independently before integration.

## Migration Plan

1. With all five capability deltas validated, add v2 fixtures, preserve explicitly named v1.2 migration fixtures, add the v1→v2 mapping for the executable 45-case survey, and add Sheet-range and index-parser tests without changing emitted behavior.
2. Implement the RCA catalog, signal/summary fields, fixed confidence, and 28-column writer; bump `BundleVersion` to `v2.0` last.
3. Run the consumer compatibility matrix and update the one known v1-only assertion.
4. Align all four JTI capability specs, `jira-skill` docs, and the JTI skill.
5. Remove the stray/duplicate index paths, regenerate all canonical index outputs from 131 valid skills, verify both existing matchers still consume the JSON schema, and review the generated diff.
6. Run focused tests, full suites where coverage policy requires them, consumer parity tests, uv-based lint/type checks, per-repo GitNexus change detection, merged-spec checks, and strict OpenSpec validation.
7. Deploy through the normal `jira-skill`/consumer release workflow; no database migration is required.

Rollback is a source rollback to the pre-v2 implementation and matching docs/index artifacts. It must roll back the runtime and consumers together; reverting only the skill would recreate the original drift.

## Open Questions

No blocking design questions remain. Release preflight MUST still search deployment manifests and external integration documentation for a non-editable v1 consumer; if one is found, implementation pauses for an explicit compatibility decision rather than silently expanding this change.

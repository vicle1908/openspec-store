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
runtime docs + OpenSpec specs
```

The specification was updated to describe the v2.0 RCA taxonomy and 28-column Sheets output, but the runtime previously had `BundleVersion v1.2`, the ten-entry RCA catalog, and 26 classification columns. The runtime had only partially adopted v2: `RootCauseSignal` contained `four_p_lens` and `secondary_categories`, while `IssueSummary`, Sheets rendering, versioning, taxonomy names, and sentinel behavior remained inconsistent. The three consumer repos use editable `jira-skill` dependencies, so the contract can be migrated atomically in the workspace.

The OpenSpec audit also found overlapping baseline requirements. `jti-classification-accuracy` already describes most of v2 but uses stale evidence positions, calls the executable survey a 65-case set even though `TestRcaSurveyPrecision.SURVEY` contains 45 cases, and assigns lens ownership to a different table; `impact-sheet-integration` still requires current `analyze_snapshot()` output to be v1.2 and contains obsolete Module Source positions; `fix-rca-fix-status-detection` still requires nine removed categories. These are migrated by dedicated deltas in this change rather than treated as historical prose. All four capabilities declared by the proposal now have concrete delta files; this explicit coverage check is necessary because strict syntax validation alone does not detect a missing capability delta.

GitNexus impact analysis found LOW risk for each targeted symbol, with the following exact upstream scope:

- `BundleVersion`: 5 dependencies, including analyzer, enrichment, Sheets, package exports, and CLI.
- `detect_rca`: 3 callers across analyzer and the filter pipeline.
- `RootCauseSignal`: 7 importing/consuming files, including RCA, bundle, analyzer, enrichment, Sheets, and exports.
- `SheetsWriter.write_bundle`: 9 upstream symbols and the `analyze_filter` execution process, including two classification scripts.

## Goals / Non-Goals

**Goals:**

- Make the runtime, OpenSpec contract, and consumer tests describe the same v2.0 contract.
- Preserve deterministic ticket/SCM analysis while making the eight total RCA categories (seven concrete plus the `Other / Unclassified` sentinel), 4P lens, confidence mapping, and secondary-cause output explicit.
- Make the Sheets header and row schemas a single runtime-owned definition with 28 columns.
- Keep all consumer adapters thin and compatible with the shared bundle.
- Add regression coverage that fails when runtime and documentation-facing contract metadata drift again.
- Leave no contradictory current-version/category/column requirement in adjacent JTI capability specs.

**Non-Goals:**

- No new package or service dependency.
- No change to Jira authentication, collection, filter discovery, dashboard commands, or policy overlays.
- No full source-code semantic or LLM-based RCA analysis.
- No scheduling, deployment, database, launchd, or Docker migration.
- No skill-index tooling changes (the `tdt-meta` repository and its index infrastructure are no longer present in this workspace).

## Decisions

### 1. Ship the existing v2.0 target rather than downgrade the documentation

The baseline `ticket-intelligence-core` spec already defines v2.0, and the runtime had partially introduced the v2 fields. The implementation finishes that contract instead of creating a second v1.2 documentation track. The bundle version is bumped to `v2.0` only after the taxonomy, fields, and Sheet output are complete and tested.

**Alternative considered:** Roll the spec back to v1.2 and retain the ten-category runtime. Rejected because it would discard the already-approved v2 taxonomy and leave the partially shipped fields without a coherent destination.

### 2. Keep runtime constants as the executable source of truth

- `BundleVersion` in `analysis/bundle.py` owns the emitted version.
- `RCA_PATTERNS` and its catalog metadata own category order, priorities, prevention actions, and 4P lenses.
- `CLASSIFICATION_COLUMNS` in `analysis/sheets_writer.py` owns the header order.
- `RootCauseSignal` owns the typed primary signal surface, while `IssueSummary` mirrors the lens and secondary fields per issue with backward-safe defaults.
- Tests assert these constants and the serialized bundle shape; prose documentation explains them but does not become a second parser or configuration source.

The catalog entry itself is the only RCA lens mapping. The duplicate `RCA_4P_BUCKET` table is removed; `detect_rca()` reads `best_match["four_p_lens"]`, and a priority lookup derived once from the catalog orders secondary categories.

The exact v2 lens mapping is Crash → Plant, UI Layout → Plant, Wrong Data → Plant, Text / Font → Plant, Feature Not Working → Procedures, 3rd Party → Policies, Performance → Plant, and Other / Unclassified → `None`. `RootCauseSignal.four_p_lens` uses `Literal["People", "Procedures", "Policies", "Plant"] | None`; `RCAPatternEntry` uses the same concrete lens type. `People` remains an allowed framework value for forward-compatible typed data even though no v2 concrete category currently maps to it. Runtime docstrings and evidence notes are updated so they no longer claim that generic code hints increase RCA confidence or that secondary priorities are descending.

### 3. Make v2 a deliberate breaking release

The v2 taxonomy removes four category names and changes their routing, so persisted or downstream consumers that key on v1 category strings cannot silently be treated as compatible. `BundleMeta.version` remains the compatibility signal. The editable consumers continue importing the shared package rather than pinning duplicate models; their tests assert the expected v2 contract or compare against the exported `BUNDLE_VERSION` where the adapter is version-agnostic.

Existing v1 fixtures remain useful as migration inputs but are not relabeled as v2 fixtures. New v2 fixtures cover every category, the distinct unclassified sentinel, multiple secondary categories, and the 28-column output.

### 4. Normalize RCA semantics before changing the version

The classifier:

- uses the seven concrete categories plus `Other / Unclassified` sentinel in the documented priority order;
- preserves the existing ticket-grounded and lightweight SCM evidence boundaries;
- maps every concrete category to its specified 4P lens and maps the sentinel to `None`;
- computes secondary categories by category, not by matched regex, then sorts by priority and caps at three;
- uses the v2 confidence ladder in severity scoring.

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

Base RCA confidence is fixed by the primary v2 category (`0.7`, `0.6`, `0.5`, `0.4`, or `0.0`). Matching multiple categories does not raise confidence. Generic code-hint presence does not raise RCA confidence either because code evidence already contributes separately to the composite severity score; hints may still add evidence-backed prevention actions. This avoids double counting and makes the documented ladder executable.

The existing 45-case precision survey is migrated through an explicit v1.2-to-v2.0 expected-category mapping. Its gate becomes exact expected-output accuracy across the full executable survey, including expected unclassified results, rather than relying on the stale 65-case label or excluding unclassified rows from the denominator. This prevents a classifier from meeting the threshold by returning the sentinel too often. Any future expansion to 65 cases must add the missing executable fixtures rather than changing only prose.

Current expected-bundle fixtures are preserved as explicitly named v1.2 migration inputs and loaded through `TicketIntelligenceBundle.from_json()` to prove backward-safe defaults. Separate v2.0 expected bundles become the current analyzer golden outputs; implementation does not overwrite v1.2 fixtures in place and relabel them as v2.

These decisions prevent the current collision where the catch-all category and unclassified sentinel share a string, prevent duplicate secondary entries when several patterns within one category match, and remove confidence inflation based on keyword density.

### 5. Treat Sheets output and clearing as one positional compatibility surface

The writer appends `RCA 4P Lens` and `Secondary RCA` at positions 26 and 27 and constructs each issue as a mapping keyed by `CLASSIFICATION_COLUMNS`, then materializes the row in header order. This removes the split between a 22-cell literal and a four-cell `extend()` tail. The complete invariant is:

- `RCA Matched Text`: 10
- `Analysis Evidence`: 13
- `MR Links`, `Files Changed`, `At-Risk Modules`, `Module Source`: 22–25
- `RCA 4P Lens`, `Secondary RCA`: 26–27

The Classification clear range is derived from the 28-column schema and resolves to `A1:AB1000` before each write. The Summary range remains independent. This is required because `AA:AB` otherwise retain stale values during partial writes or rollback. Tests verify length, exact positions, derived clear range, empty/sentinel behavior, separator formatting, hyperlink column lookup, and row alignment. Existing tab names, hyperlinks, Summary tab behavior, and output routing remain unchanged.

### 6. Verify in dependency order, without live credentials

Verification uses deterministic fixtures and mocked Sheets/consumer adapters first, then the focused analysis suites and cross-repo parity suites. No live Jira, GitLab, or Sheets call is required for acceptance. The package's existing `uv` environments remain the only execution path. A focused `jira-epic-report` parity invocation uses `--no-cov`; its repository-wide 80% coverage gate is evaluated only by the full suite. Acceptance of `uv run jira-skill version` asserts the `Bundle version: v2.0` line independently of the package/CLI version, which remains a separate release concern.

The consumer audit found no RCA category-name or Classification-position branching in `jira-epic-report`, `jira-daily-reports`, or `webhook-receiver`. Only `webhook-receiver/tests/adapters/test_parity.py` hardcodes a v1 prefix. Therefore consumer work is a compatibility-matrix verification plus explicit `BUNDLE_VERSION == "v2.0"` assertions in each parity suite; new runtime version guards are not added where no deserialization boundary exists. GitNexus change detection and Git status review run separately inside every changed repository.

Change-specific strict validation is the release gate for this plan. Workspace-wide `openspec validate --all --strict --no-interactive` currently reports unrelated pre-existing baseline-spec failures while all active changes pass. Implementation MUST capture and compare that failure set, introduce no new workspace validation failure, and keep this change valid; repairing unrelated baseline specs is outside this change.

## Risks / Trade-offs

- **[Risk] Existing consumers or persisted fixtures expect v1 category names.** → **Mitigation:** emit `v2.0`, update editable consumer tests, retain explicit version metadata, and document the migration boundary rather than silently translating old labels.
- **[Risk] Adding two Sheet columns changes positional consumers.** → **Mitigation:** append only at the specified tail positions, keep tab names stable, and assert headers/rows together in writer tests.
- **[Risk] Existing Sheet cells in AA:AB survive rollback or a short write.** → **Mitigation:** clear through AB from the same schema width before writing and cover the exact clear range in tests.
- **[Risk] RCA pattern relocation changes classification results.** → **Mitigation:** add one fixture per category plus regression cases for moved auth/network/silent-exit patterns and the unclassified sentinel.
- **[Risk] Fixed v2 confidence changes composite severity ordering.** → **Mitigation:** snapshot the v1 ordering, add v2 score/rank fixtures, and test the documented weighted formula and tie-break order.
- **[Risk] Adjacent baseline specs continue to demand v1 behavior.** → **Mitigation:** include deltas for all four affected JTI capabilities and validate the merged contract, not only this change's file syntax.
- **[Risk] The combined change spans multiple Python repos.** → **Mitigation:** keep application edits behind this active OpenSpec change, run impact/detect-changes checks, and verify each repo independently before integration.

## Migration Plan

1. With all four capability deltas validated, add v2 fixtures, preserve explicitly named v1.2 migration fixtures, add the v1→v2 mapping for the executable 45-case survey, and add Sheet-range tests without changing emitted behavior.
2. Implement the RCA catalog, signal/summary fields, fixed confidence, and 28-column writer; bump `BundleVersion` to `v2.0` last.
3. Run the consumer compatibility matrix and update the one known v1-only assertion.
4. Align all four JTI capability specs and `jira-skill` docs.
5. Run focused tests, full suites where coverage policy requires them, consumer parity tests, uv-based lint/type checks, per-repo GitNexus change detection, merged-spec checks, and strict OpenSpec validation.
6. Deploy through the normal `jira-skill`/consumer release workflow; no database migration is required.

Rollback is a source rollback to the pre-v2 implementation and matching docs. It must roll back the runtime and consumers together; reverting only one side would recreate the original drift.

## Open Questions

No blocking design questions remain. Release preflight MUST still search deployment manifests and external integration documentation for a non-editable v1 consumer; if one is found, implementation pauses for an explicit compatibility decision rather than silently expanding this change.

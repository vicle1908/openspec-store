# impact-sheet-integration Specification

## Purpose
Define the deterministic contracts between the `TicketIntelligenceBundle` model, the `SheetsWriter` adapter, and the rendered Google Sheet output for the `jira-skill` ticket-intelligence classifier. This spec is the canonical source for the v1.1 (impact columns) and v1.2 (module provenance + comment-noise stripping + hyperlink embedding) additive extensions.

## Requirements
### Requirement: ImpactSnapshot field on TicketIntelligenceBundle
The `TicketIntelligenceBundle` model MUST expose an optional `impact: ImpactSnapshot | None = None` field. When `JIRA_SKILL_IMPACT_IN_SHEETS=true` (default) the field SHALL be populated by `ImpactEnricher.enrich_bundle()` inside `analyze_snapshot()`. When the flag is `false`, the field SHALL remain `None`. The bundle version SHALL advance from `v1.0` to `v1.1` to mark the additive extension; v1.0 bundles MUST remain valid when deserialized (impact renders as `None`). v1.2 adds the IMPACT-1 `at_risk_modules_provenance` extension plus the hyperlink embedding and comment-noise-stripping requirements documented below — see "Module provenance on at_risk_modules", "Issue-Key hyperlinks", "MR-link hyperlinks", and "Comment-noise stripping for RCA classification".

#### Scenario: Bundle v1.2 carries an ImpactSnapshot with provenance
- **WHEN** `analyze_snapshot()` is called with `enrich_impact=True` against a Jira filter containing at least one merged-MR-bearing ticket
- **THEN** the returned `TicketIntelligenceBundle` MUST contain `meta.version == "v1.2"`
- **AND** `bundle.impact` MUST NOT be `None`
- **AND** each `ImpactRow` MUST include `at_risk_modules_provenance: dict[str, str]` keyed by module name

#### Scenario: Bundle v1.0 / v1.1 deserializes unchanged
- **WHEN** a serialized v1.0 or v1.1 bundle JSON is loaded via `TicketIntelligenceBundle.from_json()`
- **THEN** `bundle.impact` MUST default to `None` for v1.0
- **AND** `ImpactRow.at_risk_modules_provenance` MUST default to `{}` for v1.1
- **AND** all other prior-version fields MUST be present with their original values

### Requirement: ImpactRow shape
Each entry in `ImpactSnapshot.by_issue_key` MUST be an `ImpactRow` containing: `issue_key: str`, `mr_links: list[str]`, `last_commit_sha: str | None`, `files_changed_count: int`, `at_risk_modules: list[str]`, `impact_status: Literal["ok", "stale", "unavailable", "no_mrs"]`, and `extras: dict[str, Any]`. The `extras` field MUST be a forward-compatible escape hatch; consumers MUST treat unknown keys as opaque.

#### Scenario: ImpactRow populated from a merged MR
- **WHEN** the resolver finds a merged MR with `merge_commit_sha`, `url`, and the impact pipeline produces a report with 3 changed files and at-risk modules `["payment-core"]`
- **THEN** the row MUST contain `mr_links=["<url>"]`, `last_commit_sha="<sha>"`, `files_changed_count=3`, `at_risk_modules=["payment-core"]`, `impact_status="ok"`

#### Scenario: ImpactRow with no resolved MRs
- **WHEN** the resolver returns no merged MRs for a Jira ticket key
- **THEN** the row MUST contain `mr_links=[]`, `files_changed_count=0`, `at_risk_modules=[]`, `impact_status="no_mrs"`

#### Scenario: ImpactRow with GitLab unreachable
- **WHEN** `analyze_mr_to_report()` raises a transport exception while resolving an MR
- **THEN** the row MUST contain `impact_status="unavailable"`
- **AND** the row MUST still be present in `by_issue_key` so the bundle is complete

### Requirement: Classification tab impact columns
The Classification tab MUST include three new columns appended to the existing 21-column layout: `MR Links`, `Files Changed`, `At-Risk Modules`. The columns MUST be sourced from `bundle.impact.by_issue_key[<issue_key>]` when present. When `bundle.impact is None` or the row is missing for a given issue, the three cells MUST render as empty strings. The total column count SHALL be 24, and `CLASSIFICATION_COLUMNS` MUST be the single source of truth for header ordering.

#### Scenario: Classification tab renders all 24 columns
- **WHEN** `SheetsWriter.write_bundle()` is called against a v1.1 bundle with impact populated
- **THEN** the first row of the Classification tab MUST equal `CLASSIFICATION_COLUMNS` (length 24)
- **AND** the last three headers MUST be `"MR Links"`, `"Files Changed"`, `"At-Risk Modules"`

#### Scenario: Empty impact cells when bundle.impact is None
- **WHEN** `bundle.impact is None` (e.g. flag disabled or enrichment skipped)
- **THEN** each Classification row's last three cells MUST be empty strings
- **AND** no error MUST be raised

### Requirement: Summary tab Impact Summary section
The Summary tab MUST include an `--- Impact Summary ---` section when `bundle.impact is not None`. The section MUST render: `Issues with MRs`, `Total MRs Analyzed`, `Total Files Changed`, `At-Risk Modules (unique across filter)`, `Unavailable`, and `Cache Hits / Misses` metrics computed via `ImpactCascadeSummary.build()`.

#### Scenario: Cascade Summary section rendered
- **WHEN** `bundle.impact` is populated with rows that have a mix of `ok` and `no_mrs` statuses
- **THEN** the Summary tab MUST contain a section header row `["--- Impact Summary ---", ""]`
- **AND** MUST render the six metric rows derived from `ImpactCascadeSummary.build()`
- **AND** the `At-Risk Modules` value MUST be the deduplicated sorted union of `at_risk_modules` across all rows

#### Scenario: Cascade Summary section absent when impact is None
- **WHEN** `bundle.impact is None`
- **THEN** the Summary tab MUST NOT contain the `--- Impact Summary ---` section
- **AND** the Summary tab MUST render only the existing pre-impact rows

### Requirement: analyze_snapshot enrichment wiring
`analyze_snapshot()` MUST accept an `enrich_impact: bool = True` parameter. When `True`, it SHALL construct an `ImpactEnricher` and run `enrich_bundle()` after the deterministic bundle construction completes. The enricher MUST NOT raise into the caller; any per-ticket or pipeline failure MUST be logged and produce `bundle.impact = None`.

#### Scenario: Default-on enrichment
- **WHEN** `analyze_snapshot(snapshot)` is called without `enrich_impact`
- **THEN** the default MUST be `True`
- **AND** `bundle.impact` MUST be populated when the Jira/GitLab APIs are reachable

#### Scenario: Opt-out via parameter
- **WHEN** `analyze_snapshot(snapshot, enrich_impact=False)`
- **THEN** `bundle.impact` MUST be `None`
- **AND** the existing 993 tests for `analyze_snapshot` MUST continue to pass without modification

#### Scenario: Enrichment failure is non-fatal
- **WHEN** `ImpactEnricher.enrich_bundle()` raises an unexpected exception
- **THEN** `analyze_snapshot()` MUST log the exception and return the bundle with `bundle.impact = None`
- **AND** MUST NOT propagate the exception to the caller

### Requirement: Module provenance on at_risk_modules
`ImpactRow` MUST gain an additive field `at_risk_modules_provenance: dict[str, str]` mapping module names to source labels. Three source labels are valid: `"gitnexus_callgraph"`, `"feature_map"`, `"base_module_escalation"`. **Provenance flow:** `coverage_analyzer.AnalysisResult.at_risk_modules_provenance` → `impact_report.ImpactReport.at_risk_modules_provenance` → `ImpactRow.at_risk_modules_provenance`. The Classification tab MUST render a new "Module Source" column at zero-indexed position 24, formatted as `module(source_short)` joined by `" | "`. Backward compatibility: `at_risk_modules: list[str]` MUST remain populated; the new field defaults to `{}` and is omitted from sheet rendering when empty. Spec source-of-truth: `openspec/changes/jti-classification-accuracy/specs/jti-classification-accuracy/spec.md` (IMPACT-1).

#### Scenario: GitNexus call-graph tag
- **WHEN** a GitNexus impact run returns `affected_modules=["feature.payments"]` for a diff symbol
- **THEN** the resulting `ImpactRow` MUST contain `at_risk_modules_provenance={"feature.payments": "gitnexus_callgraph"}`

#### Scenario: Feature-map fallback tag
- **WHEN** a file path is resolved via the YAML feature map (no GitNexus call-graph hit)
- **THEN** the resulting module entry MUST have `provenance[module] == "feature_map"`

#### Scenario: Base-module escalation tag
- **WHEN** the base-module heuristic fires (`is_base_module=True` AND `abs(net_lines) > 3`)
- **THEN** every platform-wide module appended MUST have `provenance[module] == "base_module_escalation"`

#### Scenario: Classification tab Module Source column
- **WHEN** a row has `at_risk_modules=["feature.common", "App"]` with provenance `{"feature.common": "gitnexus_callgraph", "App": "base_module_escalation"}`
- **THEN** the Module Source column at zero-indexed position 24 MUST render the string `feature.common(gitnexus) | App(base)`

#### Scenario: v1.1 bundles deserialize unchanged
- **WHEN** a v1.1 bundle JSON is loaded that lacks `at_risk_modules_provenance`
- **THEN** `ImpactRow.at_risk_modules_provenance` MUST default to `{}`
- **AND** `at_risk_modules` MUST be populated as before

### Requirement: Issue-Key hyperlinks (HYPERLINK-1)
The Classification tab's "Issue Key" column (zero-indexed position 2 in `CLASSIFICATION_COLUMNS`; 1-indexed column C) MUST render each `issue_key` as a clickable hyperlink whose target URL is `f"{ATLASSIAN_SITE}/browse/{issue_key}"`. When `ATLASSIAN_SITE` is unset, the column MUST fall back to plain text rather than emit a broken link. The hyperlink MUST be embedded via a Sheets API `batchUpdate` `updateCells` request that sets `userEnteredValue.hyperlink` (not as a plain string in `values.update`, which would render the URL as text), and the cell text MUST remain the bare `issue_key` (e.g. `PDS-365`) so that sorting and filtering on the column continue to work.

#### Scenario: Issue Key cell carries a hyperlink
- **WHEN** a row's `bundle.issue_identities[i].key == "PDS-365"` and `ATLASSIAN_SITE == "https://psplit.atlassian.net"`
- **THEN** the corresponding Classification row's "Issue Key" cell MUST contain the displayed text `PDS-365`
- **AND** the cell MUST have an attached hyperlink whose URL is `https://psplit.atlassian.net/browse/PDS-365`
- **AND** clicking the cell MUST navigate to that URL

#### Scenario: Missing ATLASSIAN_SITE falls back to plain text
- **WHEN** `ATLASSIAN_SITE` (or `JIRA_URL` / `JIRA_BASE_URL`) is unset or empty
- **THEN** the "Issue Key" column MUST render plain text with no hyperlink
- **AND** MUST NOT throw or emit a broken link

#### Scenario: Hyperlinks survive subsequent value writes
- **WHEN** the writer first writes the data rows via `values.update` and then applies hyperlink formatting via `batchUpdate`
- **THEN** all "Issue Key" cells MUST retain their hyperlinks on subsequent reads
- **AND** the data write MUST NOT clear the hyperlinks (the operations are sequenced in the writer: data-write first, hyperlink-batchUpdate second)

### Requirement: MR-link hyperlinks (HYPERLINK-2)
The Classification tab's "MR Links" column (zero-indexed position 22 in `CLASSIFICATION_COLUMNS`; 1-indexed column W) MUST render each `ImpactRow.mr_links` entry as a comma-separated list of clickable hyperlinks. When a single row carries multiple MRs, each URL MUST be its own clickable hyperlink, separated from the next by `", "`. URLs that are empty or whitespace MUST be omitted. When `mr_links` is empty, the cell MUST render an empty string with no hyperlink.

#### Scenario: Single MR link cell
- **WHEN** an `ImpactRow` has `mr_links=["https://git.ecomedic.vn/pspl/poems-mobile3-android/-/merge_requests/23096"]`
- **THEN** the cell's displayed text MUST equal that URL
- **AND** the cell MUST have an attached hyperlink pointing to that URL

#### Scenario: Multiple MR link cells
- **WHEN** an `ImpactRow` has `mr_links=["https://.../mrs/1", "https://.../mrs/2"]`
- **THEN** the cell's displayed text MUST equal `https://.../mrs/1, https://.../mrs/2`
- **AND** BOTH URLs MUST be embedded as separate hyperlinks in the same cell, in order

### Requirement: Comment-noise stripping for RCA classification (RCA-5)
`analyze_snapshot()` MUST apply the same QA noise-stripping regex (`_strip_qa_noise()` from `rca.py`) to each Jira *comment body* before concatenating them with the description into the input passed to `detect_rca()`. Today `_strip_qa_noise()` runs against `combined_content` at `rca.py:916` which concatenates `[summary, description, *comment_bodies]` *after* the noise-stripping step. The fix: extend the contract so each comment body in `analyzer.py:630-634` (`comment_bodies` list comprehension) is independently passed through `_strip_qa_noise()` and then concatenated. The `_strip_qa_noise()` function MUST remain idempotent and MUST handle empty/whitespace inputs without raising.

#### Scenario: Comment-embedded "no crash" doesn't trigger Crash classification
- **WHEN** a Jira issue's description contains no crash keyword
- **AND** a Jira comment contains `"Screen loads normally without crash or layout issue"` inside a `||` regression table
- **THEN** the resulting `rca_category` MUST NOT equal `"Crash / ANR / Force Close"`
- **AND** `matched_text` MUST NOT equal `"crash"`
- **AND** the comment's `||` table rows MUST be replaced by the `<!-- RCA-NOISE: QA assertion row stripped -->` marker before pattern matching

#### Scenario: Empty comments and missing ATLASSIAN_SITE are no-ops
- **WHEN** a Jira issue has zero comments or all empty comment bodies
- **THEN** `_strip_qa_noise()` MUST NOT raise
- **AND** the resulting `rca_content` MUST equal the description-only concatenation

### Requirement: Issue-key stripping for RCA classification (RCA-6)
`detect_rca()` MUST strip Jira issue-key-shaped tokens (`\b[A-Z][A-Z0-9]{1,9}-\d{1,6}\b`) from the input content before pattern matching. Issue keys appear in three contexts that are noise to RCA classification: (a) the `<KEY>:` narrative prefix produced by `_build_narrative()` (`analyzer.py`), (b) multi-ticket branch names embedded in developer comments (`tuanla/PDS-504,505,513,RMD-4342`), and (c) cross-references in prose (`see PDS-502 for similar layout`). In all three cases the digits inside the key trigger status-code patterns (`\b(500|502|503|504)\b`, `\b(401|403)\b`) and produce false `Network / API Connectivity` / `Authentication / Authorization` classifications on unrelated tickets. The strip replaces each key with a neutral `<!--RCA-NOISE:key-->` marker; the surrounding text is preserved for evidence audits. The 5xx status-code pattern MUST additionally apply a `(?<!=)` negative lookbehind to avoid matching URL/HTTP attribute values such as `width=502` in Jira image markup. The fix is purely additive — it does not change which real network/auth errors still match (`API returned 500`, `401 Unauthorized`).

#### Scenario: Issue key digits in narrative prefix don't trigger 5xx
- **WHEN** the input content begins with `"PDS-502: Annual Performance Return label not same as figma"`
- **THEN** the resulting `rca_category` MUST NOT equal `"Network / API Connectivity"`
- **AND** the `"PDS-502"` token MUST be replaced by `<!--RCA-NOISE:key-->` in the processed content

#### Scenario: Multi-ticket branch names don't trigger 5xx
- **WHEN** a developer comment contains the branch reference `tuanla/PDS-504,505,513,RMD-4342`
- **THEN** the resulting `rca_category` MUST NOT equal `"Network / API Connectivity"`
- **AND** each `PDS-NNN` / `RMD-NNN` token MUST be replaced by the noise marker

#### Scenario: width=502 in Jira image markup doesn't trigger 5xx
- **WHEN** the input content contains `!image.png|width=502,alt="..."!`
- **THEN** the resulting `rca_category` MUST NOT equal `"Network / API Connectivity"`
- **AND** a real error reference like `"API returned 502 Bad Gateway"` MUST still match `Network / API Connectivity`

### Requirement: High-precision RCA pattern coverage (RCA-7)
The RCA taxonomy MUST include additional high-precision patterns addressing the classification gaps identified during the v1.2 live-data audit of filter 15269 (Unclassified dropped from 18 → 12). Each pattern is scoped narrowly (specific noun phrases) to avoid over-matching against UI/visual defects, preserving the recall-vs-precision balance established by RCA-4 / RCA-6.

The 9 new patterns (5 Wrong Data, 2 Auth, 2 UI Layout):
- **Wrong Data / Incorrect Value** (5 patterns):
  - `\bnot\s+allow(?:ing|s)?\s+(?:input|entering|to\s+enter|decimal|numeric|integer)\b` — input validation rejects valid format
  - `\ballow(?:s|ing)?\s+(?:decimal|numeric|integer|input|invalid)\b` — input validation accepts invalid format
  - `\b(sort|filter)\s+by\b.*\b(not\s+correct|incorrect|wrong|not\s+follow)\b` — sort/filter ORDERING defect
  - `\bcaret\b.*\b(placed|position).*\b(incorrect|wrong|unexpectedly)\b` — caret positioning defect in text input
  - `\b(calculation|computation|computed\s+result|formula)\b.*\b(incorrect|wrong|returns?\s+wrong)\b` — computed result defect
- **Authentication / Authorization** (2 patterns):
  - `\b(able\s+to\s+(?:login|access|proceed|continue))\b.*\bexpired\s+(?:otp|token|password)\b` — auth bypass via expired credential
  - `\bexpired\s+(?:otp|token)\b` — direct expired-credential reference
- **UI Layout / Visual Defect** (2 patterns):
  - `\b(dialog|popup|bottomsheet|sheet|menu|alert)\b.*\b(shifts?|moves?|jumps?)\b.*\b(position|unexpectedly|unexpected)\b` — element position shifts unexpectedly (note: all verb alternatives end with `?` to avoid Python regex `re` module's alternation+`\b` quirk)
  - `\bnavigation\s+issue\s+is\s+there\b` — specific navigation-defect descriptor

These patterns are additive and MUST NOT regress existing classifications: UI/visual "incorrect size", "incorrect color", "icon size wrong", and "placeholder text wrong" MUST remain in UI Layout / Text / Font / General UI/UX Polish categories (verified by `TestRcaRca7NewPatterns`).

#### Scenario: Input validation defect routes to Wrong Data
- **WHEN** the input content contains `"Not allow entering decimal amount on deposit screen"`
- **THEN** the resulting `rca_category` MUST equal `"Wrong Data / Incorrect Value"`
- **AND** `matched_text` MUST contain `"not allow"` (case-insensitive)

#### Scenario: Sort/filter ordering defect routes to Wrong Data
- **WHEN** the input content contains `"Sort by Status Type is not correct"`
- **THEN** the resulting `rca_category` MUST equal `"Wrong Data / Incorrect Value"`
- **AND** `matched_text` MUST contain `"sort by"` (case-insensitive)

#### Scenario: Auth bypass with expired OTP routes to Authentication
- **WHEN** the input content contains `"Able to login to the page even when entered the expired OTP"`
- **THEN** the resulting `rca_category` MUST equal `"Authentication / Authorization"`
- **AND** `matched_text` MUST contain `"expired"` (case-insensitive)

#### Scenario: Dialog position shift routes to UI Layout
- **WHEN** the input content contains `"Preferred counter alert dialog shifts position unexpectedly"`
- **THEN** the resulting `rca_category` MUST equal `"UI Layout / Visual Defect"`
- **AND** `matched_text` MUST contain `"shifts"` (case-insensitive)

#### Scenario: UI/visual defects stay in UI categories
- **WHEN** the input content contains `"Sort icon size was previously incorrect"` or `"Incorrect color of Requested button"`
- **THEN** the resulting `rca_category` MUST NOT equal `"Wrong Data / Incorrect Value"`
- **AND** the category MUST remain in `{"UI Layout / Visual Defect", "Text / Font Display", "General UI/UX Polish — no specific pattern matched"}`


## MODIFIED Requirements

### Requirement: RCA-2 — Evidence propagation
`detect_rca()` MUST populate `RootCauseSignal.matched_text` with the regex match substring that triggered the classification, and `RootCauseSignal.evidence` MUST contain at least one entry with `rule_tag="rca_pattern_match"` whenever a pattern matches. The `IssueSummary.code_evidence` field MUST include the deterministic provenance entry `rca:match:<category>:<matched_text>` whenever an issue is RCA-classified. The Classification tab MUST render the extracted substring in `RCA Matched Text` at zero-indexed position 10 and MUST render the complete provenance entry in `Analysis Evidence` at zero-indexed position 13. The RCA evidence entry MUST appear before any worktree-commit or MR-reference evidence in the joined Analysis Evidence cell.

#### Scenario: RCA match appears in both evidence surfaces
- **WHEN** an issue has `rca_category="UI Layout / Visual Defect"` and `matched_text="tab isn't highlight"`
- **THEN** the Classification row's `RCA Matched Text` cell at position 10 MUST equal `tab isn't highlight`
- **AND** its `Analysis Evidence` cell at position 13 MUST contain `rca:match:UI Layout / Visual Defect:tab isn't highlight`
- **AND** the prefix MUST be parseable by the regex `^rca:match:(.+?):(.*)$`
- **AND** `matched_text` MUST be the exact regex match substring, not truncated

#### Scenario: Non-RCA evidence remains in the column with RCA evidence first
- **WHEN** an issue has both RCA evidence AND worktree commit evidence
- **THEN** the Analysis Evidence column MUST contain both, joined with `" | "`
- **AND** the RCA evidence entry MUST appear first in the joined string

#### Scenario: Unmatched issues do not emit rca:match evidence
- **WHEN** an issue falls into the unclassified bucket with `matched_text=""`
- **THEN** no `rca:match:*` entry MUST appear in the Analysis Evidence column for that issue
- **AND** the RCA Matched Text cell MUST be empty
#### Scenario: RCA match appears in Analysis Evidence column
- **WHEN** an issue has `rca_category="UI Layout / Visual Defect"` and `matched_text="tab isn't highlight"`
- **THEN** the corresponding Classification row's "Analysis Evidence" column MUST contain `rca:match:UI Layout / Visual Defect:tab isn't highlight`
- **AND** the prefix MUST be parseable by the regex `^rca:match:(.+?):(.*)$`
- **AND** `matched_text` MUST be the exact regex match substring, not truncated
### Requirement: RCA-3 — Unclassified fallback
When the input to `detect_rca()` is non-empty but no pattern in the seven-category concrete `RCA_PATTERNS` catalog matches `combined_content`, `detect_rca()` MUST return a `RootCauseSignal` with `category="Other / Unclassified"`, `confidence=0.0`, `matched_text=""`, `four_p_lens=None`, `secondary_categories=[]`, `evidence=[SignalEvidence(rule_tag="rca_unclassified", ...)]`, and empty `prevention_actions`. When the input is empty, whitespace-only, or `None`, `detect_rca()` MUST continue returning `None`. The sheet MUST render the literal sentinel in the RCA cell and empty lens/secondary cells.

#### Scenario: Unmatched content gets sentinel category
- **WHEN** non-empty content matches no concrete taxonomy pattern
- **THEN** `RootCauseSignal.category` MUST equal `"Other / Unclassified"`
- **AND** `RootCauseSignal.confidence` MUST equal `0.0`
- **AND** `RootCauseSignal.matched_text` MUST equal `""`
- **AND** `RootCauseSignal.four_p_lens` MUST be `None`
- **AND** `RootCauseSignal.secondary_categories` MUST equal `[]`
- **AND** the Classification RCA cell MUST render `"Other / Unclassified"`

#### Scenario: Unclassified carries explanatory evidence
- **WHEN** the unclassified fallback fires
- **THEN** `RootCauseSignal.evidence` MUST contain at least one entry with `rule_tag="rca_unclassified"`
- **AND** that entry's note MUST explain that non-empty content matched no RCA taxonomy pattern

#### Scenario: Empty input still returns None
- **WHEN** `detect_rca("")`, `detect_rca("   ")`, or `detect_rca(None)` is called
- **THEN** the function MUST return `None`
- **AND** `None` MUST NOT be confused with the `Other / Unclassified` sentinel

#### Scenario: Executable survey accuracy regression gate
- **WHEN** the executable 45-case `TestRcaSurveyPrecision.SURVEY` runs against the v2 taxonomy
- **THEN** the test MUST assert that the fixture count is 45 and exact expected-category accuracy is at least 85%
- **AND** expected unclassified results MUST remain in the denominator
- **AND** the suite MUST NOT claim 65 cases unless 65 executable fixtures are actually present
#### Scenario: Unclassified carries rca_unclassified evidence
- **WHEN** the unclassified fallback fires
- **THEN** `RootCauseSignal.evidence` MUST contain at least one entry with `rule_tag="rca_unclassified"`
- **AND** that entry's `note` MUST mention the phrase "No RCA pattern matched"
#### Scenario: Survey precision regression gate
- **NOTE** This baseline scenario name is retained, but the executable v2 survey is the 45-case fixture set defined by RCA-3; the old 65-ticket count is historical and not an active denominator.
- **WHEN** the executable 45-case precision survey runs against the updated taxonomy
- **THEN** the survey MUST continue to assert precision at or above 85%
- **AND** expected unclassified results MUST remain in the denominator
### Requirement: RCA-4 — Coverage gap closure (v2.0 taxonomy)
The `RCA_PATTERNS` catalog MUST contain the v2.0 seven-category concrete taxonomy in priority order: Crash p1, UI Layout p2, Wrong Data p3, Text/Font p4, Feature Not Working p5, 3rd Party p6, and Performance p7. The distinct `Other / Unclassified` sentinel MUST remain outside the concrete pattern catalog. v2.0 MUST migrate Silent Exit patterns to Feature Not Working, Authentication and Network patterns to `3rd Party Issue (WebView, API, SDK)`, and only specific retained General UI patterns to UI Layout or Text/Font; unmatched general content MUST fall back to the sentinel. Each retained or new pattern MUST continue through `_stem_pattern()` expansion where applicable and MUST have a positive fixture plus false-positive guards.

#### Scenario: Authentication patterns route to 3rd Party
- **WHEN** `combined_content` contains `sso`, `saml`, `token expired`, `jwt invalid`, expired OTP, or their supported inflections
- **THEN** the resulting category MUST be `"3rd Party Issue (WebView, API, SDK)"` at priority 6
- **AND** `RootCauseSignal.four_p_lens` MUST be `"Policies"`
- **AND** base confidence MUST be `0.5`

#### Scenario: Network patterns route to 3rd Party
- **WHEN** `combined_content` contains an API 5xx error, offline queue, retry storm, circuit breaker, reconnect, vendor outage, or their supported inflections
- **THEN** the resulting category MUST be `"3rd Party Issue (WebView, API, SDK)"` at priority 6
- **AND** `RootCauseSignal.four_p_lens` MUST be `"Policies"`

#### Scenario: Silent failure patterns route to Feature Not Working
- **WHEN** `combined_content` contains `button has no effect`, `loading spinner never stops`, blank content, or another retained Silent Exit pattern
- **THEN** the resulting category MUST be `"Feature Not Working / Missing"` at priority 5
- **AND** `RootCauseSignal.four_p_lens` MUST be `"Procedures"`

#### Scenario: Wrong Data patterns remain precise
- **WHEN** `combined_content` contains decimal precision, currency conversion wrong, FX rate stale, invalid numeric input, incorrect sorting, or an incorrect calculation
- **THEN** the resulting category MUST be `"Wrong Data / Incorrect Value"` at priority 3
- **AND** visual size, color, icon, or placeholder defects MUST NOT be absorbed by the Wrong Data patterns

#### Scenario: Text and UI patterns keep their concrete ownership
- **WHEN** content contains a concrete translation, locale, font, or text-rendering defect
- **THEN** the resulting category MUST be `"Text / Font Display"` at priority 4 with `four_p_lens="Plant"`
- **AND** concrete layout, alignment, spacing, hidden-element, disabled-control, or dialog-position defects MUST remain `"UI Layout / Visual Defect"` at priority 2 with `four_p_lens="Plant"`

#### Scenario: Performance patterns remain priority seven
- **WHEN** `combined_content` contains startup time slow, launch time high, memory leak, lag, jank, or supported inflections
- **THEN** the resulting category MUST be `"Performance / Slow Loading"` at priority 7
- **AND** base confidence MUST be `0.4`

#### Scenario: 3rd Party WebView SDK IdP and vendor patterns
- **WHEN** `combined_content` contains WebView, WKWebView, SDK, IdP, OIDC, Firebase, Crashlytics, Google sign-in, Apple sign-in, third party, vendor, or broker evidence
- **THEN** the resulting category MUST be `"3rd Party Issue (WebView, API, SDK)"` at priority 6
- **AND** `RootCauseSignal.four_p_lens` MUST be `"Policies"`
#### Scenario: Authentication patterns
- **NOTE** These retained baseline pattern names are explicit v2 coverage; they route to the current `3rd Party Issue (WebView, API, SDK)` category and are not the removed v1 Authentication category.
- **WHEN** `combined_content` contains `sso`, `saml`, `token expired`, `jwt invalid`, or their inflections
- **THEN** the resulting category MUST be `"3rd Party Issue (WebView, API, SDK)"` (priority 6)
- **AND** the resulting `RootCauseSignal.four_p_lens` MUST be `"Policies"`
#### Scenario: Network patterns
- **WHEN** `combined_content` contains `offline queue`, `retry storm`, `circuit breaker`, `reconnect`, or their inflections
- **THEN** the resulting category MUST be `"3rd Party Issue (WebView, API, SDK)"` (priority 6)
- **AND** the resulting `RootCauseSignal.four_p_lens` MUST be `"Policies"`
#### Scenario: Feature Not Working patterns
- **WHEN** `combined_content` contains `filter doesn't reset`, `pagination broken`, `scroll to top fails`, `button has no effect`, `loading spinner never stops`, or their inflections
- **THEN** the resulting category MUST be `"Feature Not Working / Missing"` (priority 5)
- **AND** the resulting `RootCauseSignal.four_p_lens` MUST be `"Procedures"`
#### Scenario: Wrong Data patterns
- **WHEN** `combined_content` contains `decimal precision`, `currency conversion wrong`, `fx rate stale`, or their inflections
- **THEN** the resulting category MUST be `"Wrong Data / Incorrect Value"` (priority 3)
#### Scenario: Text / Font i18n patterns
- **WHEN** `combined_content` contains `locale broken`, `translation cut off`, `i18n overflow`, or their inflections
- **THEN** the resulting category MUST be `"Text / Font Display"` (priority 4)
#### Scenario: Performance patterns
- **WHEN** `combined_content` contains `startup time slow`, `launch time high`, `memory leak`, or their inflections
- **THEN** the resulting category MUST be `"Performance / Slow Loading"` (priority 7)
#### Scenario: 3rd Party WebView / SDK / IdP / vendor patterns
- **WHEN** `combined_content` contains `webview`, `wkwebview`, `sdk`, `idp`, `oidc`, `firebase`, `crashlytics`, `google sign-in`, `apple sign-in`, `3rd party`, `third party`, `vendor`, `broker`, or their inflections
- **THEN** the resulting category MUST be `"3rd Party Issue (WebView, API, SDK)"` (priority 6)
- **AND** the resulting `RootCauseSignal.four_p_lens` MUST be `"Policies"`
### Requirement: RCA-8 — 4P Lens and multi-cause surfacing (v2.0)
`detect_rca()` MUST attach `four_p_lens: Literal["People", "Procedures", "Policies", "Plant"] | None` to every returned `RootCauseSignal`, populated directly from the winning `RCA_PATTERNS` catalog entry. The catalog entry MUST be the only category-to-lens mapping; no duplicate lens table may participate in classification. The unclassified sentinel MUST have `four_p_lens=None`. `detect_rca()` MUST also populate `secondary_categories: list[str]` with every other distinct matched concrete category, sorted by ascending taxonomy priority, excluding the primary, deduplicated, and capped at three. `IssueSummary` MUST mirror `four_p_lens: str | None` and `secondary_rca: list[str]`. The Classification tab MUST render `RCA 4P Lens` at zero-indexed position 26 and `Secondary RCA` at position 27, joining categories with `" | "`.

#### Scenario: Exact category-to-lens mapping is catalog-owned
- **WHEN** a concrete v2 category wins classification
- **THEN** Crash, UI Layout, Wrong Data, Text/Font, and Performance MUST map to `Plant`
- **AND** Feature Not Working MUST map to `Procedures`
- **AND** 3rd Party MUST map to `Policies`
- **AND** the signal lens MUST equal the winning catalog entry's lens

#### Scenario: 3rd Party WebView SDK keywords map to 3rd Party Issue
- **WHEN** `combined_content="WebView returns blank page after navigation"`
- **THEN** `RootCauseSignal.category` MUST be `"3rd Party Issue (WebView, API, SDK)"`
- **AND** `RootCauseSignal.four_p_lens` MUST be `"Policies"`
- **AND** `RootCauseSignal.confidence` MUST be `0.5`

#### Scenario: Multi-cause ticket exposes bounded secondary causes
- **WHEN** `combined_content="App crashes after WebView fails to load SDK returns 502"`
- **THEN** `RootCauseSignal.category` MUST be `"Crash / ANR / Force Close"` at priority 1
- **AND** `RootCauseSignal.secondary_categories` MUST contain `"3rd Party Issue (WebView, API, SDK)"` once
- **AND** the list MUST be sorted by ascending priority, exclude the primary, and contain at most three entries
- **AND** matching several regexes from the same category MUST NOT duplicate that category

#### Scenario: Generic code hints do not inflate confidence
- **WHEN** a ticket matches a concrete category and generic code hints are also present
- **THEN** the category's fixed base confidence MUST remain unchanged
- **AND** evidence-backed prevention actions MAY be appended once
- **AND** emitted evidence MUST NOT claim that the RCA confidence was strengthened

#### Scenario: Unclassified ticket has no 4P lens and no secondary categories
- **WHEN** non-empty content matches no concrete taxonomy pattern
- **THEN** `RootCauseSignal.category` MUST be `"Other / Unclassified"`
- **AND** `RootCauseSignal.four_p_lens` MUST be `None`
- **AND** `RootCauseSignal.secondary_categories` MUST be `[]`

#### Scenario: Summary and sheet surfaces mirror the signal
- **WHEN** a per-issue RCA signal has `four_p_lens="Policies"` and `secondary_categories=["Performance / Slow Loading"]`
- **THEN** its `IssueSummary` MUST carry `four_p_lens="Policies"` and `secondary_rca=["Performance / Slow Loading"]`
- **AND** Classification positions 26 and 27 MUST render `"Policies"` and `"Performance / Slow Loading"` respectively
#### Scenario: 3rd Party WebView / SDK keywords map to 3rd Party Issue
- **WHEN** `combined_content="WebView returns blank page after navigation"`
- **THEN** `RootCauseSignal.category` MUST be `"3rd Party Issue (WebView, API, SDK)"`
- **AND** `RootCauseSignal.four_p_lens` MUST be `"Policies"`
- **AND** `RootCauseSignal.confidence` MUST be `0.5`
#### Scenario: Multi-cause ticket exposes secondary causes
- **WHEN** `combined_content="App crashes after WebView fails to load SDK returns 502"`
- **THEN** `RootCauseSignal.category` MUST be `"Crash / ANR / Force Close"` (winner-takes-all primary, priority 1)
- **AND** `RootCauseSignal.secondary_categories` MUST contain `"3rd Party Issue (WebView, API, SDK)"` (the secondary cause)
- **AND** the secondary list MUST be sorted by priority ascending
- **AND** the joined string `"3rd Party Issue (WebView, API, SDK)"` MUST appear in the Classification tab's `Secondary RCA` column
#### Scenario: Plant categories never carry a Policies 4P lens
- **WHEN** `combined_content` matches a Plant-lens category (Crash, UI Layout, Wrong Data, Text/Font, Performance)
- **THEN** `RootCauseSignal.four_p_lens` MUST NOT be `"Policies"`
- **AND** it MUST be `"Plant"`
#### Scenario: Secondary categories capped at three
- **WHEN** `combined_content` matches 5 or more distinct taxonomy categories
- **THEN** `RootCauseSignal.secondary_categories` MUST contain at most 3 entries
- **AND** the 3 entries MUST be the 3 most severe (lowest priority numbers) after the primary is removed
#### Scenario: Classification tab columns 26 and 27
- **WHEN** the sheets writer renders a row whose `IssueSummary` has `four_p_lens="Policies"` and `secondary_rca=["3rd Party Issue (WebView, API, SDK)"]`
- **THEN** the cell at position 26 (0-indexed) MUST be the string `"Policies"`
- **AND** the cell at position 27 (0-indexed) MUST be the string `"3rd Party Issue (WebView, API, SDK)"`
### Requirement: IMPACT-1 — `at_risk_modules` provenance
`ImpactRow` MUST expose the additive field `at_risk_modules_provenance: dict[str, str]` mapping module names to one of `"gitnexus_callgraph"`, `"feature_map"`, or `"base_module_escalation"`. The value MUST flow unchanged through `coverage_analyzer.AnalysisResult.at_risk_modules_provenance` → `impact_report.ImpactReport.at_risk_modules_provenance` → `ImpactRow.at_risk_modules_provenance`. The v2 Classification tab MUST render `Module Source` at zero-indexed position 25, formatted as `module(source_short)` joined by `" | "`. `at_risk_modules` MUST remain populated, and provenance MUST default to `{}` when absent from v1.1 bundle JSON.

#### Scenario: GitNexus-derived module is tagged correctly
- **WHEN** `run_impact()` supplies `affected_modules=["feature.payments"]`
- **THEN** the resulting `ImpactRow.at_risk_modules_provenance` MUST contain `{"feature.payments": "gitnexus_callgraph"}`

#### Scenario: Feature-map fallback is tagged correctly
- **WHEN** a file path resolves via the YAML feature map and no GitNexus call-graph match exists
- **THEN** the resulting module entry MUST have `provenance[module] == "feature_map"`

#### Scenario: Base-module escalation is tagged correctly
- **WHEN** `resolution.is_base_module=True` AND `abs(net_lines) > 3`
- **THEN** every platform-wide module appended by escalation MUST have `provenance[module] == "base_module_escalation"`

#### Scenario: Classification tab Module Source position is stable in v2
- **WHEN** a row has `at_risk_modules=["feature.common", "App"]` with provenance `{"feature.common": "gitnexus_callgraph", "App": "base_module_escalation"}`
- **THEN** the Module Source cell at zero-indexed position 25 MUST render `feature.common(gitnexus) | App(base)`
- **AND** `RCA 4P Lens` and `Secondary RCA` MUST follow at positions 26 and 27

#### Scenario: v1.1 bundles deserialize unchanged
- **WHEN** a v1.1 bundle JSON is loaded without `at_risk_modules_provenance`
- **THEN** `ImpactRow.at_risk_modules_provenance` MUST default to `{}`
- **AND** `at_risk_modules` MUST remain populated
- **AND** consumers that only read `at_risk_modules` MUST NOT break

#### Scenario: Same module can appear via two sources
- **WHEN** the same module is appended by two sources in one deterministic pipeline
- **THEN** `at_risk_modules_provenance[module]` MUST record the last source applied
- **AND** `at_risk_modules` MUST contain the module once
#### Scenario: GitNexus-derived module tagged correctly
- **NOTE** This duplicate baseline scenario identity is retained for archive compatibility; the v2 position and provenance contract are the same as the canonical scenario above.
- **WHEN** `coverage_analyzer.analyze_diff()` returns an `AnalysisResult.at_risk_modules` entry that originated from `run_impact(symbol, repo)` returning `affected_modules=["feature.payments"]`
- **THEN** the resulting `ImpactRow.at_risk_modules_provenance` MUST contain `{"feature.payments": "gitnexus_callgraph"}`
#### Scenario: Feature-map fallback tagged correctly
- **WHEN** a file path resolves via the YAML feature map and no GitNexus call-graph match exists
- **THEN** the resulting module entry MUST have `provenance[module] == "feature_map"`
#### Scenario: Base-module escalation tagged correctly
- **WHEN** `resolution.is_base_module=True` AND `abs(net_lines) > BASE_MODULE_LINE_DELTA_THRESHOLD (=3)`
- **THEN** every platform-wide feature module appended in the escalation loop MUST have `provenance[module] == "base_module_escalation"`
#### Scenario: Classification tab Module Source column
- **NOTE** This baseline scenario identity is retained; the v2 column position is 25 (zero-indexed) as required by the current 28-column schema.
- **WHEN** a row has `at_risk_modules=["feature.common", "App"]` with provenance `{"feature.common": "gitnexus_callgraph", "App": "base_module_escalation"}`
- **THEN** the Module Source column at zero-indexed position 25 MUST render the string `feature.common(gitnexus) | App(base)`

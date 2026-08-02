# jti-classification-accuracy Specification

## Purpose
TBD - created by archiving change jti-classification-accuracy. Update Purpose after archive.
## Requirements
### Requirement: RCA-2 — Evidence propagation
`detect_rca()` MUST populate `RootCauseSignal.matched_text` with the regex match substring that triggered the classification, and `RootCauseSignal.evidence` MUST contain at least one entry with `rule_tag="rca_pattern_match"` whenever a pattern matches. The `IssueSummary.code_evidence` field MUST include the deterministic provenance entry `rca:match:<category>:<matched_text>` whenever an issue is RCA-classified. The "Analysis Evidence" column in the Classification tab (zero-indexed position 12 in `CLASSIFICATION_COLUMNS`; 1-indexed position 13) MUST render this entry verbatim. The RCA evidence entry MUST appear before any worktree-commit or MR-reference evidence in the joined cell.

#### Scenario: RCA match appears in Analysis Evidence column
- **WHEN** an issue has `rca_category="UI Layout / Visual Defect"` and `matched_text="tab isn't highlight"`
- **THEN** the corresponding Classification row's "Analysis Evidence" column MUST contain `rca:match:UI Layout / Visual Defect:tab isn't highlight`
- **AND** the prefix MUST be parseable by the regex `^rca:match:(.+?):(.*)$`
- **AND** `matched_text` MUST be the exact regex match substring, not truncated

#### Scenario: Non-RCA evidence remains in the column with RCA evidence first
- **WHEN** an issue has both RCA evidence AND worktree commit evidence
- **THEN** the Analysis Evidence column MUST contain both, joined with `" | "`
- **AND** the RCA evidence entry MUST appear first in the joined string

#### Scenario: Unmatched issues do not emit rca:match evidence
- **WHEN** an issue falls into the unclassified bucket (RCA-3 with `matched_text=""`)
- **THEN** no `rca:match:*` entry MUST appear in the Analysis Evidence column for that issue

### Requirement: RCA-3 — Unclassified fallback
When the input to `detect_rca()` is **non-empty** but no pattern in `RCA_PATTERNS` matches `combined_content`, `detect_rca()` MUST return a `RootCauseSignal` with `category="Other / Unclassified"`, `confidence=0.0`, `matched_text=""`, `evidence=[SignalEvidence(rule_tag="rca_unclassified", ...)]`, and empty `prevention_actions`. When the input is empty (empty string, whitespace-only, or `None`), `detect_rca()` MUST continue returning `None`. The sheet MUST render the literal string `"Other / Unclassified"` for any issue whose `rca_category` is the sentinel.

#### Scenario: Unmatched content gets sentinel category
- **WHEN** `combined_content="The widget is broken"` does not match any taxonomy pattern
- **THEN** `RootCauseSignal.category` MUST equal `"Other / Unclassified"`
- **AND** `RootCauseSignal.confidence` MUST equal `0.0`
- **AND** `RootCauseSignal.matched_text` MUST equal `""`
- **AND** the Classification tab RCA cell MUST render the string `"Other / Unclassified"`

#### Scenario: Unclassified carries rca_unclassified evidence
- **WHEN** the unclassified fallback fires
- **THEN** `RootCauseSignal.evidence` MUST contain at least one entry with `rule_tag="rca_unclassified"`
- **AND** that entry's `note` MUST mention the phrase "No RCA pattern matched"

#### Scenario: Empty input still returns None
- **WHEN** `detect_rca("")`, `detect_rca("   ")`, or `detect_rca(None)` is called
- **THEN** the function MUST return `None` (preserving the existing early-exit behavior at `rca.py:901-902`)
- **AND** `None` MUST NOT be confused with the "Other / Unclassified" sentinel

#### Scenario: Survey precision regression gate
- **WHEN** the existing 65-ticket precision survey runs against the updated taxonomy
- **THEN** the survey MUST continue to assert precision ≥85%
- **AND** unclassified tickets MUST be excluded from the precision denominator (they are explicit fallbacks, not misclassifications)

### Requirement: RCA-4 — Coverage gap closure (v2.0 taxonomy)
The `RCA_PATTERNS` taxonomy MUST add coverage patterns distributed across the v2.0 7-category list (Crash p1, UI Layout p2, Wrong Data p3, Text/Font p4, Feature Not Working p5, 3rd Party p6, Performance p7) plus the `Other / Unclassified` sentinel. v2.0 replaces the four deprecated categories (Silent Exit, Authentication, Network, General UI/UX Polish) with a single new category `3rd Party Issue (WebView, API, SDK)` at priority 6 that absorbs all of their patterns plus new WebView / SDK / IdP / vendor keywords. Each new pattern MUST go through the existing `_stem_pattern()` inflection expansion at module load. Each new pattern MUST add one survey-positive fixture to `tests/analysis/test_rca.py::TestRcaCoverage`.

#### Scenario: Authentication patterns
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
`detect_rca()` MUST attach a `four_p_lens` field of type `Literal["People", "Procedures", "Policies", "Plant"] | None` to every returned `RootCauseSignal`, populated from the `RCA_FOUR_P_LENS` table in `rca.py`. The unclassified sentinel MUST have `four_p_lens = None`. `detect_rca()` MUST also populate a `secondary_categories: list[str]` field listing every other taxonomy category that also matched `combined_content`, sorted by priority ascending (most severe first), deduplicated, capped at 3 entries. The `IssueSummary` MUST carry additive fields `secondary_rca: list[str]` and `four_p_lens: str | None`. The Classification tab MUST render `RCA 4P Lens` at position 26 (1-indexed: position 27) and `Secondary RCA` at position 27 (1-indexed: position 28) for every issue. The `Secondary RCA` cell MUST join categories with `" | "`.

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

#### Scenario: Unclassified ticket has no 4P lens and no secondary categories
- **WHEN** `combined_content="The widget is broken"` matches no taxonomy pattern
- **THEN** `RootCauseSignal.category` MUST be `"Other / Unclassified"`
- **AND** `RootCauseSignal.four_p_lens` MUST be `None`
- **AND** `RootCauseSignal.secondary_categories` MUST be `[]`

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
`ImpactRow` MUST gain an additive field `at_risk_modules_provenance: dict[str, str]` (module name → source label). Three source labels are valid: `"gitnexus_callgraph"` (from `run_impact()` invoked inside `coverage_analyzer.py`), `"feature_map"` (from YAML substring resolution inside `coverage_analyzer.py`), `"base_module_escalation"` (from the `is_base_module AND abs(net_lines) > 3` heuristic inside `coverage_analyzer.py`). **Provenance threading requirement:** the `dict[str, str]` value MUST be populated along the data flow `coverage_analyzer.AnalysisResult.at_risk_modules_provenance` → `impact_report.ImpactReport.at_risk_modules_provenance` → `ImpactRow.at_risk_modules_provenance`. The `ImpactEnricher._enrich_keys()` function at `impact/enrichment.py:138,150` is the final step that copies provenance into `ImpactRow` and MUST propagate `at_risk_modules_provenance` unchanged (no re-mapping, no dropping). The Classification tab MUST render a new "Module Source" column at zero-indexed position 24, formatted as `module(source_short)` joined by `" | "`. Backward compatibility: `at_risk_modules: list[str]` MUST remain populated; `at_risk_modules_provenance` defaults to `{}` when not present in v1.1 bundle JSON.

#### Scenario: GitNexus-derived module tagged correctly
- **WHEN** `coverage_analyzer.analyze_diff()` returns an `AnalysisResult.at_risk_modules` entry that originated from `run_impact(symbol, repo)` returning `affected_modules=["feature.payments"]`
- **THEN** the resulting `ImpactRow.at_risk_modules_provenance` MUST contain `{"feature.payments": "gitnexus_callgraph"}`

#### Scenario: Feature-map fallback tagged correctly
- **WHEN** a file path resolves via the YAML feature map and no GitNexus call-graph match exists
- **THEN** the resulting module entry MUST have `provenance[module] == "feature_map"`

#### Scenario: Base-module escalation tagged correctly
- **WHEN** `resolution.is_base_module=True` AND `abs(net_lines) > BASE_MODULE_LINE_DELTA_THRESHOLD (=3)`
- **THEN** every platform-wide feature module appended in the escalation loop MUST have `provenance[module] == "base_module_escalation"`

#### Scenario: Classification tab Module Source column
- **WHEN** a row has `at_risk_modules=["feature.common", "App"]` with provenance `{"feature.common": "gitnexus_callgraph", "App": "base_module_escalation"}`
- **THEN** the Module Source column at zero-indexed position 24 MUST render the string `feature.common(gitnexus) | App(base)`

#### Scenario: v1.1 bundles deserialize unchanged
- **WHEN** a v1.1 bundle JSON is loaded that lacks `at_risk_modules_provenance`
- **THEN** `ImpactRow.at_risk_modules_provenance` MUST default to `{}`
- **AND** `at_risk_modules` MUST be populated as before
- **AND** consumers that only read `at_risk_modules` MUST NOT break

#### Scenario: Same module can appear via two sources
- **WHEN** the same module name is appended by two different sources in the same pipeline (e.g. feature_map AND base_module_escalation)
- **THEN** `at_risk_modules_provenance[module]` MUST record the LAST source applied (deterministic, last-write-wins)
- **AND** `at_risk_modules` MUST contain the module once (deduplicated, preserving existing `set` accumulator behavior in `enrichment.py:138`)


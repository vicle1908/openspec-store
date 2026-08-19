## MODIFIED Requirements

### Requirement: ImpactSnapshot field on TicketIntelligenceBundle
The `TicketIntelligenceBundle` model MUST expose `impact: ImpactSnapshot | None = None`. When `JIRA_SKILL_IMPACT_IN_SHEETS=true` and enrichment is requested, the field SHALL be populated by `ImpactEnricher.enrich_bundle()` inside `analyze_snapshot()` when dependencies are available; when disabled or unavailable, it SHALL remain `None`. Historical v1.0, v1.1, and v1.2 serialized bundles MUST remain valid migration inputs. Newly produced bundles after the complete RCA/model/Sheet migration MUST emit `meta.version == "v2.0"`.

#### Scenario: Current v2 bundle carries an ImpactSnapshot with provenance
- **WHEN** `analyze_snapshot()` is called with `enrich_impact=True` for a snapshot containing at least one merged-MR-bearing ticket and mocked dependencies succeed
- **THEN** the returned bundle MUST contain `meta.version == "v2.0"`
- **AND** `bundle.impact` MUST NOT be `None`
- **AND** each `ImpactRow` MUST expose `at_risk_modules_provenance: dict[str, str]`

#### Scenario: Historical v1.0 v1.1 and v1.2 bundles deserialize unchanged
- **NOTE** This scenario is a legacy deserialization contract; it does not require the current v2 writer to emit v1.1 output or 24 columns.
- **WHEN** explicitly labeled v1.0, v1.1, or v1.2 JSON is loaded through `TicketIntelligenceBundle.from_json()`
- **THEN** `bundle.impact` MUST default to `None` when absent from v1.0
- **AND** `ImpactRow.at_risk_modules_provenance` MUST default to `{}` when absent from v1.1
- **AND** additive v2 summary fields MUST receive backward-safe defaults when absent from v1 payloads
- **AND** the original serialized `BundleMeta.version` MUST be preserved rather than rewritten to v2.0

#### Scenario: Version bump occurs after the complete v2 surface
- **WHEN** the taxonomy, summary fields, fixed confidence mapping, and 28-column writer are not all implemented and passing contract tests
- **THEN** `BundleVersion.current()` MUST NOT be changed to `v2.0`
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
### Requirement: Classification tab impact columns
The v2 Classification tab MUST contain exactly 28 columns materialized from `CLASSIFICATION_COLUMNS`. Impact data MUST occupy `MR Links`, `Files Changed`, `At-Risk Modules`, and `Module Source` at zero-indexed positions 22, 23, 24, and 25. `RCA 4P Lens` and `Secondary RCA` MUST follow at positions 26 and 27. When `bundle.impact is None` or an issue has no impact row, all four impact cells MUST be empty strings without shifting the two RCA enrichment cells.

#### Scenario: Classification tab renders the complete v2 schema
- **WHEN** `SheetsWriter.write_bundle()` renders a v2 bundle with impact populated
- **THEN** the first row MUST equal `CLASSIFICATION_COLUMNS` with length 28
- **AND** positions 22 through 27 MUST equal `MR Links`, `Files Changed`, `At-Risk Modules`, `Module Source`, `RCA 4P Lens`, and `Secondary RCA` in that order
- **AND** every data row MUST also contain exactly 28 cells

#### Scenario: Empty impact cells preserve RCA tail alignment
- **WHEN** `bundle.impact is None` or no `ImpactRow` exists for an issue
- **THEN** positions 22 through 25 MUST be empty strings
- **AND** positions 26 and 27 MUST still render that issue's RCA lens and secondary categories when present
- **AND** no error MUST be raised

#### Scenario: Classification clearing covers the v2 tail
- **WHEN** a Classification tab is refreshed
- **THEN** the clear range MUST be derived from the 28-column schema and resolve through column `AB`
- **AND** stale Module Source, lens, or secondary cells MUST NOT survive a shorter write
#### Scenario: Classification tab renders all 24 columns
- **NOTE** This legacy scenario name and 24-column assertion are retained for the archived v1.1 writer contract only; the current v2 writer is governed by the 28-column scenarios above.
- **WHEN** `SheetsWriter.write_bundle()` renders a historical v1.1 bundle with impact populated
- **THEN** the first row of the historical Classification tab MUST equal the legacy `CLASSIFICATION_COLUMNS` (length 24)
- **AND** the last three legacy headers MUST be `"MR Links"`, `"Files Changed"`, `"At-Risk Modules"`
#### Scenario: Empty impact cells when bundle.impact is None
- **WHEN** `bundle.impact is None` (e.g. flag disabled or enrichment skipped)
- **THEN** each Classification row's last three cells MUST be empty strings
- **AND** no error MUST be raised
### Requirement: Module provenance on at_risk_modules
`ImpactRow` MUST expose `at_risk_modules_provenance: dict[str, str]` mapping modules to `"gitnexus_callgraph"`, `"feature_map"`, or `"base_module_escalation"`. Provenance MUST flow through `coverage_analyzer.AnalysisResult.at_risk_modules_provenance` → `impact_report.ImpactReport.at_risk_modules_provenance` → `ImpactRow.at_risk_modules_provenance` without remapping or dropping entries. The Classification tab MUST render `Module Source` at zero-indexed position 25 as `module(source_short)` joined by `" | "`. `at_risk_modules` MUST remain populated, and provenance MUST default to `{}` when absent from v1.1 JSON.

#### Scenario: GitNexus call-graph tag
- **WHEN** a GitNexus impact run returns `affected_modules=["feature.payments"]`
- **THEN** the resulting `ImpactRow` MUST contain `at_risk_modules_provenance={"feature.payments": "gitnexus_callgraph"}`

#### Scenario: Feature-map fallback tag
- **WHEN** a file path resolves through the YAML feature map without a GitNexus call-graph hit
- **THEN** the resulting module entry MUST have `provenance[module] == "feature_map"`

#### Scenario: Base-module escalation tag
- **WHEN** the base-module heuristic fires with `is_base_module=True` and `abs(net_lines) > 3`
- **THEN** every platform-wide appended module MUST have `provenance[module] == "base_module_escalation"`

#### Scenario: Classification tab Module Source column
- **WHEN** a row has `at_risk_modules=["feature.common", "App"]` with provenance `{"feature.common": "gitnexus_callgraph", "App": "base_module_escalation"}`
- **THEN** the Module Source cell at zero-indexed position 25 MUST render `feature.common(gitnexus) | App(base)`

#### Scenario: v1.1 bundles deserialize unchanged
- **WHEN** v1.1 JSON lacks `at_risk_modules_provenance`
- **THEN** `ImpactRow.at_risk_modules_provenance` MUST default to `{}`
- **AND** `at_risk_modules` MUST remain populated as before

### Requirement: Issue-key stripping for RCA classification (RCA-6)
`detect_rca()` MUST strip Jira issue-key-shaped tokens (`\b[A-Z][A-Z0-9]{1,9}-\d{1,6}\b`) before pattern matching. Issue-key digits in narrative prefixes, branch names, and cross-references MUST NOT trigger 4xx/5xx integration patterns. The strip MUST replace each key with a neutral `<!--RCA-NOISE:key-->` marker while preserving surrounding text. The 5xx pattern MUST reject URL or Jira-image attribute values such as `width=502`; genuine API status evidence such as `API returned 502 Bad Gateway` MUST route to the v2 `3rd Party Issue (WebView, API, SDK)` category.

#### Scenario: Issue key digits in narrative prefix do not trigger 3rd Party
- **WHEN** input begins with `"PDS-502: Annual Performance Return label not same as figma"`
- **THEN** the result MUST NOT be `"3rd Party Issue (WebView, API, SDK)"` solely because of `PDS-502`
- **AND** the issue key MUST be replaced by `<!--RCA-NOISE:key-->` in processed content

#### Scenario: Multi-ticket branch names do not trigger 3rd Party
- **WHEN** a developer comment contains `tuanla/PDS-504,505,513,RMD-4342`
- **THEN** the result MUST NOT be 3rd Party solely because of issue-key digits
- **AND** full issue-key tokens MUST be replaced by the noise marker

#### Scenario: Width attribute does not trigger 5xx but a real API error does
- **WHEN** input contains `!image.png|width=502,alt="..."!`
- **THEN** it MUST NOT match a 5xx RCA pattern
- **AND** `"API returned 502 Bad Gateway"` MUST match `"3rd Party Issue (WebView, API, SDK)"`
#### Scenario: Issue key digits in narrative prefix don't trigger 5xx
- **WHEN** the input content begins with `"PDS-502: Annual Performance Return label not same as figma"`
- **THEN** the resulting `rca_category` MUST NOT equal `"3rd Party Issue (WebView, API, SDK)"` solely because of `PDS-502`
- **AND** the `"PDS-502"` token MUST be replaced by `<!--RCA-NOISE:key-->` in the processed content
#### Scenario: Multi-ticket branch names don't trigger 5xx
- **WHEN** a developer comment contains the branch reference `tuanla/PDS-504,505,513,RMD-4342`
- **THEN** the resulting `rca_category` MUST NOT equal `"3rd Party Issue (WebView, API, SDK)"` solely because of issue-key digits
- **AND** each `PDS-NNN` / `RMD-NNN` token MUST be replaced by the noise marker
#### Scenario: width=502 in Jira image markup doesn't trigger 5xx
- **WHEN** the input content contains `!image.png|width=502,alt="..."!`
- **THEN** it MUST NOT match a 5xx RCA pattern
- **AND** a real error reference like `"API returned 502 Bad Gateway"` MUST match `"3rd Party Issue (WebView, API, SDK)"`
### Requirement: High-precision RCA pattern coverage (RCA-7)
The v2 taxonomy MUST retain the nine high-precision patterns identified by the v1.2 live-data audit while routing their outputs through the current category names. The five Wrong Data patterns MUST remain in `Wrong Data / Incorrect Value`; the two former Authentication patterns MUST route to `3rd Party Issue (WebView, API, SDK)`; and the two UI Layout patterns MUST remain in `UI Layout / Visual Defect`. These patterns MUST remain narrowly scoped and MUST retain false-positive guards for visual/text defects.

The retained patterns are:
- **Wrong Data / Incorrect Value**: invalid-input rejection, invalid-input acceptance, incorrect sort/filter ordering, incorrect caret position, and incorrect calculation result.
- **3rd Party Issue (WebView, API, SDK)**: auth bypass with expired OTP/token/password and direct expired OTP/token evidence.
- **UI Layout / Visual Defect**: dialog/popup position shifts and the specific navigation-defect descriptor.

#### Scenario: Input validation defect routes to Wrong Data
- **WHEN** input contains `"Not allow entering decimal amount on deposit screen"`
- **THEN** the category MUST equal `"Wrong Data / Incorrect Value"`
- **AND** `matched_text` MUST contain `"not allow"` case-insensitively

#### Scenario: Sort or filter ordering defect routes to Wrong Data
- **WHEN** input contains `"Sort by Status Type is not correct"`
- **THEN** the category MUST equal `"Wrong Data / Incorrect Value"`
- **AND** `matched_text` MUST contain `"sort by"` case-insensitively

#### Scenario: Expired OTP auth bypass routes to 3rd Party
- **WHEN** input contains `"Able to login to the page even when entered the expired OTP"`
- **THEN** the category MUST equal `"3rd Party Issue (WebView, API, SDK)"`
- **AND** `matched_text` MUST contain `"expired"` case-insensitively

#### Scenario: Dialog position shift routes to UI Layout
- **WHEN** input contains `"Preferred counter alert dialog shifts position unexpectedly"`
- **THEN** the category MUST equal `"UI Layout / Visual Defect"`
- **AND** `matched_text` MUST contain `"shifts"` case-insensitively

#### Scenario: UI and text defects stay out of Wrong Data
- **WHEN** input contains an incorrect icon size, incorrect color, or wrong placeholder language
- **THEN** the category MUST NOT equal `"Wrong Data / Incorrect Value"`
- **AND** a concrete match MUST remain in `UI Layout / Visual Defect` or `Text / Font Display`; otherwise it MUST fall back to `Other / Unclassified`
#### Scenario: Sort/filter ordering defect routes to Wrong Data
- **WHEN** the input content contains `"Sort by Status Type is not correct"`
- **THEN** the resulting `rca_category` MUST equal `"Wrong Data / Incorrect Value"`
- **AND** `matched_text` MUST contain `"sort by"` (case-insensitive)
#### Scenario: Auth bypass with expired OTP routes to Authentication
- **NOTE** This legacy scenario name is retained for baseline identity; the v2 runtime destination is `"3rd Party Issue (WebView, API, SDK)"`, not the removed `"Authentication / Authorization"` category.
- **WHEN** the input content contains `"Able to login to the page even when entered the expired OTP"`
- **THEN** the resulting `rca_category` MUST equal `"3rd Party Issue (WebView, API, SDK)"`
- **AND** `matched_text` MUST contain `"expired"` (case-insensitive)
#### Scenario: UI/visual defects stay in UI categories
- **WHEN** the input content contains `"Sort icon size was previously incorrect"` or `"Incorrect color of Requested button"`
- **THEN** the resulting `rca_category` MUST NOT equal `"Wrong Data / Incorrect Value"`
- **AND** the category MUST remain in `{"UI Layout / Visual Defect", "Text / Font Display", "Other / Unclassified"}`

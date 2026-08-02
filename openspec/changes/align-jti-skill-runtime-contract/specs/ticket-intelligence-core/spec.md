## MODIFIED Requirements

### Requirement: Produce a reusable ticket intelligence bundle
The system SHALL produce a reusable ticket intelligence bundle for Jira issues that multiple ecosystem tools can consume without changing analysis semantics. The shipped contract for this change SHALL be explicitly versioned as `v2.0`, and consumers SHALL be able to inspect `BundleMeta.version` before interpreting breaking RCA or output-schema changes.

#### Scenario: Bundle contract is validated and serializable
- **WHEN** the shared bundle crosses a repo boundary or is persisted as a fixture artifact
- **THEN** it SHALL be represented by versioned Pydantic models that validate structure and support deterministic serialization
- **AND** the emitted `BundleMeta.version` SHALL equal `v2.0` for the v2 implementation

#### Scenario: Multiple consumers read the same bundle
- **WHEN** `jira-epic-report`, `jira-daily-reports`, or `webhook-receiver` requests analysis for the same Jira snapshot
- **THEN** the system SHALL produce the same canonical v2.0 bundle for that snapshot
- **AND** each consumer SHALL be able to read the bundle without needing repo-specific analysis logic

#### Scenario: The bundle is versioned
- **WHEN** the intelligence contract changes
- **THEN** the system SHALL expose a versioned bundle shape so consumers can detect compatible versus breaking changes
- **AND** v2.0 consumers SHALL NOT silently treat removed v1 category names or positional output columns as unchanged semantics

#### Scenario: Historical v1.2 fixtures remain valid migration inputs
- **WHEN** an explicitly labeled v1.2 expected-bundle fixture is loaded through `TicketIntelligenceBundle.from_json()` after the v2 models ship
- **THEN** its original `BundleMeta.version` SHALL remain `v1.2`
- **AND** newly additive `IssueSummary.four_p_lens` and `IssueSummary.secondary_rca` fields SHALL use backward-safe defaults
- **AND** the fixture SHALL NOT be overwritten or relabeled as a v2.0 golden output

#### Scenario: Evidence is attached
- **WHEN** a normalized signal is emitted in the bundle
- **THEN** the bundle SHALL carry evidence references or summaries that explain the signal source

## ADDED Requirements

### Requirement: Runtime RCA catalog matches the v2.0 taxonomy
The executable RCA catalog SHALL contain the seven concrete categories and the distinct `Other / Unclassified` sentinel in the priority order defined by the `ticket-intelligence-core` contract. The catalog SHALL preserve deterministic ticket/SCM evidence boundaries and SHALL NOT introduce a source-semantic or LLM dependency.

#### Scenario: Concrete category and lens mapping is complete
- **WHEN** a non-empty ticket matches a concrete RCA category
- **THEN** the primary category SHALL be one of `Crash / ANR / Force Close`, `UI Layout / Visual Defect`, `Wrong Data / Incorrect Value`, `Text / Font Display`, `Feature Not Working / Missing`, `3rd Party Issue (WebView, API, SDK)`, or `Performance / Slow Loading`
- **AND** its `four_p_lens` SHALL use this exact mapping: Crash → `Plant`, UI Layout → `Plant`, Wrong Data → `Plant`, Text / Font → `Plant`, Feature Not Working → `Procedures`, 3rd Party → `Policies`, and Performance → `Plant`
- **AND** the executable catalog entry SHALL be the only category-to-lens mapping used by `detect_rca()`

#### Scenario: Unclassified content has a distinct sentinel
- **WHEN** non-empty content matches no concrete RCA category
- **THEN** `detect_rca()` SHALL return `category="Other / Unclassified"`, `confidence=0.0`, `four_p_lens=null`, and an unclassified evidence marker
- **AND** the sentinel SHALL be distinguishable from every concrete category, including any UX or text pattern

#### Scenario: Empty content remains unclassified by absence
- **WHEN** RCA input is empty, whitespace-only, or `None`
- **THEN** `detect_rca()` SHALL return `None`
- **AND** it SHALL NOT manufacture an `Other / Unclassified` signal for absent content

### Requirement: RCA enrichment is deterministic and bounded
The v2.0 `RootCauseSignal` SHALL expose `four_p_lens: Literal["People", "Procedures", "Policies", "Plant"] | None` and `secondary_categories: list[str]` consistently on the primary signal and the mirrored per-issue `IssueSummary` fields `four_p_lens: str | None` and `secondary_rca: list[str]`. The executable catalog lens field SHALL use the same concrete literal type. Secondary categories SHALL represent distinct category names, be sorted by ascending taxonomy priority, exclude the primary, and contain no more than three entries.

#### Scenario: Multiple categories are surfaced once
- **WHEN** content matches patterns from more than one concrete category
- **THEN** the primary category SHALL be selected by taxonomy priority
- **AND** `secondary_categories` SHALL contain each other matched category at most once, sorted by priority, capped at three, and exclude the primary

#### Scenario: Single-cause and sentinel results have no secondary causes
- **WHEN** content matches exactly one concrete category or produces the unclassified sentinel
- **THEN** `secondary_categories` SHALL be an empty list

#### Scenario: Summary fields mirror RCA enrichment
- **WHEN** `analyze_snapshot()` emits an issue summary for an RCA-bearing issue
- **THEN** the summary SHALL expose `four_p_lens` and `secondary_rca` using the same deterministic semantics as the root-cause signal

#### Scenario: Confidence is a category-priority base value
- **WHEN** `detect_rca()` returns a matched v2.0 signal without an external semantic enrichment layer
- **THEN** its base confidence SHALL be `0.7` for Crash, `0.6` for UI Layout/Wrong Data/Text/Feature, `0.5` for 3rd Party, `0.4` for Performance, or `0.0` for Other / Unclassified
- **AND** matching multiple categories or merely having generic code hints SHALL NOT increase that base confidence
- **AND** code hints MAY add deduplicated evidence-backed prevention actions but SHALL NOT claim that RCA confidence was strengthened

### Requirement: Classification Sheets output is a v2.0 positional contract
The canonical Classification tab SHALL contain exactly 28 columns. The header and every data row SHALL be materialized from the same ordered schema, with `RCA Matched Text` at zero-indexed position 10, `Analysis Evidence` at position 13, `MR Links` through `Module Source` at positions 22–25, `RCA 4P Lens` at position 26, and `Secondary RCA` at position 27. Existing tab naming, hyperlink targets, and filter routing SHALL remain unchanged, and hyperlink column indexes SHALL be resolved from the canonical schema rather than duplicated constants.

#### Scenario: Header exposes the v2 columns
- **WHEN** `SheetsWriter.write_bundle()` creates or updates a Classification tab
- **THEN** the header SHALL contain 28 columns
- **AND** the final two headers SHALL be `RCA 4P Lens` and `Secondary RCA` in that order

#### Scenario: Data rows remain aligned with headers
- **WHEN** a bundle contains matched, multi-cause, unclassified, or no-impact issues
- **THEN** every emitted row SHALL have exactly 28 cells
- **AND** the RCA lens and secondary values SHALL appear under their matching headers
- **AND** the `Secondary RCA` cell SHALL join categories with `" | "`
- **AND** absent values SHALL remain empty rather than shifting later cells

#### Scenario: Existing tail cells are cleared before a v2 write
- **WHEN** the writer refreshes a Classification tab that previously contained v1.2 or partial v2 data
- **THEN** it SHALL derive the Classification clear range from the 28-column schema and resolve it through column `AB` before writing the new rows
- **AND** stale `AA:AB` values SHALL NOT survive a shorter or rollback write
- **AND** the independent Summary-tab clear behavior SHALL remain unchanged

### Requirement: Editable consumers verify the v2.0 boundary
The shared consumer adapters SHALL continue delegating core analysis to `jira-skill` and SHALL explicitly verify or safely consume the v2.0 bundle version. Consumer-local policy and presentation logic SHALL remain outside the canonical analyzer.

#### Scenario: Consumer parity uses the shared v2 bundle
- **WHEN** a parity or adapter test constructs a bundle through `jira-skill`
- **THEN** it SHALL observe `BUNDLE_VERSION == "v2.0"` and the adapter SHALL not reimplement RCA or Sheet classification logic
- **AND** each editable consumer parity suite SHALL contain an explicit v2.0 compatibility assertion

#### Scenario: Version mismatch is visible
- **WHEN** a consumer receives a bundle with an unsupported version
- **THEN** the consumer or compatibility test SHALL report the mismatch explicitly rather than silently treating it as a compatible v1 payload
- **AND** no runtime version guard SHALL be added to an adapter that has no external deserialization boundary solely to satisfy this scenario

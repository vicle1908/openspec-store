## Purpose

Ensures comprehensive executable test coverage for the v2.0 RCA classification system, covering all seven concrete categories, the Other / Unclassified sentinel, taxonomy priority, confidence values, multi-cause deduplication, false-positive resistance, and preservation of fix-status detection tests.

## Requirements

### Requirement: RCA Detection Test Coverage

The RCA classification system SHALL have comprehensive executable test coverage for all seven concrete v2.0 categories plus the distinct `Other / Unclassified` sentinel. Coverage SHALL include taxonomy priority, exact category-to-4P mapping, fixed confidence values, empty-input behavior, pattern false positives, multi-cause deduplication/order/cap behavior, and preservation of fix-status detection coverage.

#### Scenario: All seven concrete v2 categories are correctly classified

- **WHEN** `detect_rca()` is called with representative inputs for each concrete category
- **THEN** it SHALL return each exact category name: `Crash / ANR / Force Close`, `UI Layout / Visual Defect`, `Wrong Data / Incorrect Value`, `Text / Font Display`, `Feature Not Working / Missing`, `3rd Party Issue (WebView, API, SDK)`, and `Performance / Slow Loading`
- **AND** each result SHALL carry the category's exact Plant, Procedures, or Policies lens
- **AND** the removed Silent Exit, Authentication, Network, and General UI/UX category names SHALL NOT be emitted by new v2 analysis

#### Scenario: Sentinel and empty input remain distinct

- **WHEN** non-empty content matches no concrete category
- **THEN** `detect_rca()` SHALL return `Other / Unclassified` with `confidence=0.0`, `four_p_lens=None`, and `secondary_categories=[]`
- **AND** empty, whitespace-only, or `None` input SHALL return `None`

#### Scenario: Fixed confidence ladder is covered

- **WHEN** representative inputs match the seven concrete categories
- **THEN** tests SHALL assert confidence `0.7` for Crash; `0.6` for UI Layout, Wrong Data, Text/Font, and Feature Not Working; `0.5` for 3rd Party; and `0.4` for Performance
- **AND** multiple category matches or generic code hints SHALL NOT increase those base values

#### Scenario: Multi-cause output is deterministic and bounded

- **WHEN** content matches patterns from several distinct categories and multiple patterns inside one category
- **THEN** the primary SHALL be chosen by ascending taxonomy priority
- **AND** secondary categories SHALL be unique, exclude the primary, be sorted by ascending priority, and contain at most three entries

#### Scenario: Greedy patterns do not create false positives

- **WHEN** issue keys contain 4xx/5xx digits, QA tables contain negative crash assertions, Jira image attributes contain `width=502`, or UI/text defects contain generic words also used by Wrong Data patterns
- **THEN** those noise cases SHALL NOT route to Crash, 3rd Party, or Wrong Data solely because of the noisy token
- **AND** genuine crash, API status, wrong-data, UI, and text evidence SHALL still classify correctly

#### Scenario: Fix-status regression coverage remains intact

- **WHEN** the v2 RCA taxonomy tests are added
- **THEN** existing fix-status tests for structured SCM state, QA evidence, MR text, Jira status, and worktree evidence SHALL continue to pass
#### Scenario: All 9 RCA categories are correctly classified

- **NOTE** This legacy scenario name is retained because the MODIFIED requirement must preserve the archived baseline scenario identity; it describes historical v1 taxonomy fixtures, not the v2 runtime output.
- **WHEN** an archived v1 fixture is evaluated through its historical classifier contract
- **THEN** the fixture SHALL cover the nine archived labels: Crash/ANR, Wrong Data, Silent Exit, UI Layout, Performance, Auth, Network, Feature Not Working, and General Polish
- **AND** the v2 classifier SHALL instead emit only the seven concrete v2 categories plus `Other / Unclassified`, as specified above
- **AND** empty content SHALL return `None`
- **AND** greedy patterns SHALL NOT match false positives

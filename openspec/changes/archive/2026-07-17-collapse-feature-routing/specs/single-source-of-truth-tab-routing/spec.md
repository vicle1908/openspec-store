# Spec for single-source-of-truth-tab-routing

This is a new capability introduced by the `collapse-feature-routing`
change. It will be archived to
`openspec/specs/single-source-of-truth-tab-routing/spec.md` when the
change is applied.

## ADDED Requirements

### Requirement: FEATURE_TAB_MAP Is The Single Source Of Truth

The system SHALL treat `feature_resolver.FEATURE_TAB_MAP` as the
only sanctioned source of tab names in `code-daily-scan`. The
function `feature_resolver.feature_to_tab()` SHALL be the only
sanctioned way to map a `Finding.feature` value to a tab name.

A contract test in `tests/test_feature_resolver.py` SHALL pin
`FEATURE_TAB_MAP` to a fixed, ordered set of strings. The test
SHALL fail if any value is added, removed, or renamed, forcing
the change to be intentional and reviewed.

#### Scenario: Vocabulary is pinned by test

- **WHEN** a developer adds, removes, or renames a value in
  `feature_resolver.FEATURE_TAB_MAP`
- **THEN** the contract test in `test_feature_resolver.py` SHALL
  fail until the test is updated in the same commit

#### Scenario: Mapper fallback agrees with FEATURE_TAB_MAP

- **WHEN** `sheets/mapper.py:_DEFAULT_MODULE_PATTERNS` is reviewed
- **THEN** every `(fragment, tab_name)` pair in that tuple MUST
  have `tab_name` present as a key in `FEATURE_TAB_MAP`. A
  contract test in `tests/test_sheet.py` SHALL enforce this.

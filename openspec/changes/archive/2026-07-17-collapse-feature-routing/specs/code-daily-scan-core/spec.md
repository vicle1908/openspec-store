# Spec delta for code-daily-scan-core

This delta is applied to
`openspec/changes/unified-code-daily-scan/specs/code-daily-scan-core/spec.md`
when the `collapse-feature-routing` change is archived.

## ADDED Requirements

### Requirement: Single Source Of Truth For Tab Names

The system SHALL treat `feature_resolver.FEATURE_TAB_MAP` as the only
sanctioned source of tab names. The function
`feature_resolver.feature_to_tab()` SHALL be the only sanctioned way
to map a `Finding.feature` value to a tab name. Any other code path
that produces a tab name MUST raise an error in tests, and MUST be
backed by a test that pins its output to the values in
`FEATURE_TAB_MAP`.

The system MUST include a contract test in
`tests/test_feature_resolver.py` that asserts
`FEATURE_TAB_MAP` is a fixed, ordered set of strings. The test MUST
fail if any value in `FEATURE_TAB_MAP` is added, removed, or
renamed, forcing the change to be intentional and reviewed.

#### Scenario: Tab name vocabulary is pinned

- **WHEN** a developer adds, removes, or renames a value in
  `feature_resolver.FEATURE_TAB_MAP`
- **THEN** the contract test in `test_feature_resolver.py` SHALL fail
  until the test is updated in the same commit

#### Scenario: Mapper fallback is bounded by FEATURE_TAB_MAP

- **WHEN** `sheets/mapper.py:_DEFAULT_MODULE_PATTERNS` is reviewed
- **THEN** every `(fragment, tab_name)` pair in that tuple MUST have
  `tab_name` present as a key in `FEATURE_TAB_MAP`. A contract test in
  `tests/test_sheet.py` SHALL enforce this.

### Requirement: SheetMapper Plugin-Required

`SheetMapper` MUST be constructed with a `plugin` argument. Calling
`SheetMapper()` with `plugin=None` MUST raise a `ValueError` with a
message directing the caller to inject a `PlatformPlugin` instance
from `PLUGINS`. The `_fallback_tab_name` dynamic TitleCase generator
in `sheets/mapper.py` SHALL be deleted.

#### Scenario: Missing plugin raises clearly

- **WHEN** a caller constructs `SheetMapper()` without a plugin
- **THEN** the constructor SHALL raise `ValueError("SheetMapper requires
  a plugin. Use PLUGINS['android'] or PLUGINS['ios'].")`

#### Scenario: SheetMapper with a plugin delegates tab resolution

- **WHEN** `SheetMapper(plugin=PLUGINS["android"]).resolve_tab(path)`
  is called
- **THEN** the result SHALL be identical to
  `PLUGINS["android"].resolve_tab(path)`. The contract is preserved.

### Requirement: Android Plugin Resolves Tabs Via Resolver

The Android plugin's `resolve_tab(file_path)` SHALL delegate to
`feature_resolver.resolve_feature(file_path, platform="android")` and
then `feature_to_tab(feature)`. The plugin SHALL NOT maintain its
own `ANDROID_FEATURE_PATTERNS` table or any other local feature
mapping. The plugin MAY keep a resource-file extension check
(`.endswith((".xml", ".layout", ".drawable", ".png", ".jpg", ".svg"))`)
as a last-resort fallback, but the resolver MUST be consulted
first so the spec's "Resource files SHALL map to Common" contract
is honoured for paths the resolver already understands.

#### Scenario: Android resolve_tab uses the resolver

- **WHEN** `android_plugin.resolve_tab("app/src/main/java/com/tdt/pmobile3/auth/LoginViewModel.kt")` is called
- **THEN** it SHALL return `"Auth"` (the resolver's answer, not a
  local table lookup)

#### Scenario: Android resource file resolves to Common via the resolver

- **WHEN** `android_plugin.resolve_tab("PoemsUIComponents/src/main/res/values/styles.xml")` is called
- **THEN** it SHALL return `"Common"` (the resolver's answer via
  `ANDROID_ONLY_RULES["Common"]`), overriding the extension-based
  fallback that would otherwise return `"Others"`.

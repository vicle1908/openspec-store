# Specs — Android rule refinements

## Capability: feature-resolution-android

The `feature-resolver` SHALL resolve Android file paths to feature categories using Android-specific patterns in addition to the global rule set, with no leakage to iOS.

#### Scenario: Android Kotlin file under `ui/common` resolves to `Common`

- GIVEN a file path `app/src/main/java/com/tdt/pmobile3/ui/common/DialogOrderDetail.kt`
- WHEN `resolve_feature(path, platform="android")` is called
- THEN it returns `"Common"`

#### Scenario: Android resource file resolves to `Common`

- GIVEN a file path `app/src/main/res/values/strings.xml`
- WHEN `resolve_feature(path, platform="android")` is called
- THEN it returns `"Common"`

#### Scenario: iOS path under `Common/Extensions` does NOT match Android-only rules

- GIVEN a file path `Pmobile3/Common/Extensions/String+Extensions.swift`
- WHEN `resolve_feature(path, platform="ios")` is called
- THEN it returns `"Others"` (does not match Android `extensions/` pattern)

#### Scenario: PoemsUIComponents Kotlin file resolves to `Common`

- GIVEN a file path `PoemsUIComponents/src/main/java/com/tdt/poemsui/utils/Extensions.kt`
- WHEN `resolve_feature(path, platform="android")` is called
- THEN it returns `"Common"`

## Capability: security-s2-xml-namespace-filter

The S2 rule (`Cleartext HTTP endpoints or mixed transport`) SHALL exclude XML namespace URIs (`schemas.android.com`, `www.w3.org`) from its detection patterns.

#### Scenario: XML namespace in layout file is not flagged

- GIVEN a file `app/src/main/res/layout/activity_main.xml` containing
  `xmlns:android="http://schemas.android.com/apk/res/android"`
- WHEN the S2 rule is run against the file
- THEN zero S2 findings are reported for that file

#### Scenario: Real `http://` URL in Kotlin code is flagged

- GIVEN a file `NetworkModule.kt` containing `val baseUrl = "http://api.example.com"`
- WHEN the S2 rule is run
- THEN one S2 finding is reported for that line

#### Scenario: `https://` URL is still detected

- GIVEN a file containing `BASE_URL = "https://api.example.com"`
- WHEN the S2 rule is run
- THEN one S2 finding is reported (https is also covered for mixed-transport review)

## Capability: p2-priority-calibration-android

The Android scanner SHALL produce P2 findings when concrete regex patterns are present in the rule book for P2 rules, completing the priority calibration loop.

#### Scenario: P2 rule with concrete regex produces findings

- GIVEN the rule `A6` (Missing single source of truth) has a pattern `(?:\bval\b|\bvar\b)\s+\w+\s*=\s*MutableLiveData\b` in the rule book
- WHEN the Android scanner runs
- THEN it produces at least one P2 finding for each file containing `MutableLiveData` declarations
- AND each P2 finding has `priority: "P2"`

#### Scenario: P2 rule with multi-line heuristic is documented

- GIVEN the rule `A5` (God classes) requires a per-file count threshold (e.g., >30 private functions)
- WHEN the scanner does not support per-file count thresholds
- THEN the rule SHALL be marked in the rule book as "Heuristic, requires scanner support" with no machine-parseable patterns
- AND the scanner SHALL produce 0 A5 findings (no false-positive class-declaration matches)

#### Scenario: A1 (MVVM violation) single-line proxy is a best-effort detection

- GIVEN the rule `A1` (Business logic in view) has a single-line proxy `onViewCreated.*\.callApi` 
- WHEN a Fragment file contains `override fun onViewCreated(view: View) { callApi() }` on the same line
- THEN one P2 finding is reported for that line
- AND multi-line variants (callApi on a separate line within onViewCreated) are NOT reported (ripgrep single-line limitation, documented)

## Capability: rule-pattern-loader-grammar

The `RulePatternLoader` SHALL correctly parse a Markdown bullet pattern of the form `  - \`regex\` — description` and extract only the regex portion (without the em-dash description).

#### Scenario: Pattern with em-dash description is split correctly

- GIVEN a bullet pattern `  - \`Log\.[dviwe]\(.*token.*\` — log of sensitive token`
- WHEN the loader parses it
- THEN it extracts `Log\.[dviwe]\(.*token.*` as the regex
- AND the em-dash description is stored separately

#### Scenario: Comma-separated patterns are split

- GIVEN a bullet pattern `  - \`pattern1\`, \`pattern2\` — both options`
- WHEN the loader parses it
- THEN it extracts `pattern1` and `pattern2` as separate regex entries
- (Comma in the middle of a single backtick-enclosed pattern is interpreted as starting a new pattern)

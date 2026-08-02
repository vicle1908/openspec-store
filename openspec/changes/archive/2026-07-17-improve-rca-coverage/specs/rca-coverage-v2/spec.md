# rca-coverage-v2 Specification

## ADDED Requirements

### Requirement: Stem-suffix pattern expansion
RCA patterns SHALL match common English inflections of bare keywords to prevent false negatives caused by word-boundary mismatches. The stem-suffix expansion SHALL apply uniformly to all patterns in `RCA_PATTERNS` at compile time, before the `detect_rca()` engine consumes them.

#### Scenario: Verb stem "hang" matches all inflections
- **WHEN** `detect_rca()` is called with `"App hangs on splash"`, `"App hanging on splash"`, or `"App hung on splash"`
- **THEN** it SHALL return category `"Performance / Slow Loading"` for all three inputs

#### Scenario: Past tense "deadlocked" matches stem "deadlock"
- **WHEN** `detect_rca()` is called with `"App is deadlocked"`
- **THEN** it SHALL return category `"Crash / ANR / Force Close"`

#### Scenario: Plural "drops" matches stem "drop"
- **WHEN** `detect_rca()` is called with `"Frame drops during scroll"`
- **THEN** it SHALL return category `"Performance / Slow Loading"`

#### Scenario: Stem wrapper does not match unrelated words
- **WHEN** `detect_rca()` is called with `"User is stuck in traffic"` or `"Hang the laundry"`
- **THEN** it SHALL NOT misclassify these as `"Performance / Slow Loading"` (false-positive guard)

### Requirement: Crash / ANR / Force Close matches "stops responding"
The Crash category SHALL include the pattern for application hangs described as "stops responding" or "not responding".

#### Scenario: "stops responding" returns Crash
- **WHEN** `detect_rca("Application stops responding on login")` is called
- **THEN** it SHALL return category `"Crash / ANR / Force Close"`

### Requirement: Wrong Data / Incorrect Value matches bare "incorrect"
The Wrong Data category SHALL include a pattern for bare "incorrect" without requiring the suffix ".*value".

#### Scenario: Bare "incorrect" returns Wrong Data
- **WHEN** `detect_rca("Account balance is incorrect after transfer")` is called
- **THEN** it SHALL return category `"Wrong Data / Incorrect Value"`

#### Scenario: "wrong format" returns Wrong Data
- **WHEN** `detect_rca("Wrong date format in invoice")` is called
- **THEN** it SHALL return category `"Wrong Data / Incorrect Value"`

### Requirement: Silent Exit / No Feedback matches "has no effect" and "fails to validate"
The Silent Exit category SHALL include patterns for user-action failures that don't crash but produce no visible feedback.

#### Scenario: "has no effect" returns Silent Exit
- **WHEN** `detect_rca("Submit button has no effect")` is called
- **THEN** it SHALL return category `"Silent Exit / No Feedback"`

#### Scenario: "fails to validate" returns Silent Exit
- **WHEN** `detect_rca("Login form fails to validate email")` is called
- **THEN** it SHALL return category `"Silent Exit / No Feedback"`

### Requirement: Performance / Slow Loading matches "stuck" and "blocked"
The Performance category SHALL include the bare keywords "stuck" and "blocked" for cases where the app is not actively crashing but is unresponsive.

#### Scenario: "App stuck" returns Performance
- **WHEN** `detect_rca("App stuck after login")` is called
- **THEN** it SHALL return category `"Performance / Slow Loading"`

#### Scenario: "Thread blocked" returns Performance
- **WHEN** `detect_rca("Thread blocked waiting for response")` is called
- **THEN** it SHALL return category `"Performance / Slow Loading"`

### Requirement: Authentication / Authorization matches "SSO fails"
The Auth category SHALL include plural-inflected forms of common auth terms (sso.*fails, sso.*redirect, sso.*broken).

#### Scenario: "SSO fails" returns Auth
- **WHEN** `detect_rca("SSO fails to redirect")` is called
- **THEN** it SHALL return category `"Authentication / Authorization"`

### Requirement: UI Layout / Visual Defect matches "cuts off"
The UI Layout category SHALL include the phrase "cuts off" (with space) and "cut off" in addition to the existing `cut.?off` contraction.

#### Scenario: "Image cuts off" returns UI Layout
- **WHEN** `detect_rca("Image cuts off at bottom")` is called
- **THEN** it SHALL return category `"UI Layout / Visual Defect"`

### Requirement: Network / API Connectivity matches "fails to load"
The Network category SHALL include the phrase "fails to load", "won't load", and "image not loading" for asset/image loading failures.

#### Scenario: "Profile photo fails to load" returns Network
- **WHEN** `detect_rca("Profile photo fails to load on cellular")` is called
- **THEN** it SHALL return category `"Network / API Connectivity"`

### Requirement: Feature Not Working / Missing matches "need to add"
The Feature category SHALL include the phrase "need to add" and "add feature" for unimplemented feature requests.

#### Scenario: "Need to add feature" returns Feature
- **WHEN** `detect_rca("Need to add feature X for client")` is called
- **THEN** it SHALL return category `"Feature Not Working / Missing"`

### Requirement: General UI/UX Polish matches i18n and "confused"
The UI/UX category SHALL include the pattern for i18n issues ("wrong language", "wrong translation", "localization") and the user-state adjective "confused".

#### Scenario: "wrong language" returns UI/UX
- **WHEN** `detect_rca("Button text is wrong language")` is called
- **THEN** it SHALL return category `"General UI/UX Polish — no specific pattern matched"`

#### Scenario: "User confused" returns UI/UX
- **WHEN** `detect_rca("User confused by error message")` is called
- **THEN** it SHALL return category `"General UI/UX Polish — no specific pattern matched"`

### Requirement: Survey precision target
The `detect_rca()` function SHALL achieve ≥ 85% precision on a 65-ticket real-world survey set, where precision = correct / (correct + incorrect), excluding ambiguous cases.

#### Scenario: Survey regression test
- **WHEN** the survey set (defined in `tests/analysis/test_rca.py::TestRcaCoverage::test_survey_precision`) is run
- **THEN** the precision SHALL be ≥ 85%

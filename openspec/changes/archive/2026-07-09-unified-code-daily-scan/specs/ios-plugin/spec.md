## ADDED Requirements

### Requirement: iOS Plugin Registration And Configuration

The system SHALL provide an `IOSPlugin` implementing `PlatformPlugin`, registered in `PLUGINS` under the key `"ios"`, with `name = "ios"` and `supported_extensions = (".swift", ".m", ".h")`.

#### Scenario: iOS plugin resolved

- **WHEN** the CLI is invoked with `--platform ios`
- **THEN** the core SHALL select `IOSPlugin` and scan only files whose extension is in `supported_extensions`

### Requirement: iOS Rule Loading From Markdown

The system SHALL load iOS rules from `{worktree}/docs/technical-debt-scan/categories/*.md`, parsing the same bullet-pattern Markdown dialect as Android, and SHALL fall back to `config/rule_patterns.yaml` when those documents are absent.

The parser MUST extract `rule_id` from the `## <id> — <title>` heading, `priority` from `- Priority:`, `category` from the explicit `- Category:` field, one `pattern` per bullet under `- Detection patterns:`, `title` from the heading text, and `description` from `- Why it matters:`.

#### Scenario: Parse an iOS rule with explicit category

- **WHEN** `retain-cycle-memory.md` contains `## M1 — ...` with `- Category: ` set to `Memory Leak`
- **THEN** the loader SHALL produce a `RulePattern` for `M1` whose category is `Memory Leak`

#### Scenario: Category taken from the Category field, not the rule-ID prefix

- **WHEN** `concurrency.md` contains `## C9 — ...` with `- Category: ` set to `Performance`
- **THEN** the loader SHALL assign category `Performance` even though the rule-ID prefix `C` is shared with crash rules

### Requirement: iOS Feature-Based Tab Resolution

The system SHALL resolve the spreadsheet tab for an iOS finding from `finding.feature` using `FEATURE_TAB_MAP`, and SHALL NOT route by category or rule-ID prefix because:

1. Feature-based routing is consistent with Android
2. Cross-platform comparison is possible
3. Feature field is 100% populated via path-based resolution

`FEATURE_TAB_MAP` MUST map all canonical features as: `Auth` to `Auth`, `Home` to `Home`, `WatchList` to `WatchList`, `Market` to `Market`, `Trade` to `Trade`, `Community` to `Community`, `Me/Settings` to `Me/Settings`, `Deposit/Withdraw` to `Deposit/Withdraw`, `Form` to `Form`, `Common` to `Common`. Any unmapped feature SHALL resolve to `Others`. The iOS spec MUST list the same set of features as the Android spec (10 features + `Common` + `Others` = 11 tabs total) to keep the cross-platform taxonomy unified.

#### Scenario: Auth finding routes to Auth tab

- **WHEN** a finding has feature `Auth`
- **THEN** `resolve_finding_tab` SHALL return `Auth`

#### Scenario: Trade finding routes to Trade tab

- **WHEN** a finding has feature `Trade`
- **THEN** `resolve_finding_tab` SHALL return `Trade`

#### Scenario: Unmapped feature falls back to Others

- **WHEN** a finding has a feature not present in `FEATURE_TAB_MAP`
- **THEN** `resolve_finding_tab` SHALL return `Others`

### Requirement: iOS Coverage Levels

The system SHALL support a `baseline` coverage level limited to Memory Leak (M1–M8) and Lifecycle (L1–L6), and a `full` coverage level covering all categories.

#### Scenario: Baseline coverage

- **WHEN** `scan --platform ios --coverage baseline` runs
- **THEN** only Memory Leak and Lifecycle rules SHALL be evaluated

### Requirement: iOS Spreadsheet Target

The system SHALL determine the iOS spreadsheet from `ios.spreadsheet_id` in `~/.tdt/code-daily-scan.yaml`, overridable by the `IOS_SCAN_SPREADSHEET_ID` environment variable, using a workbook separate from Android.

#### Scenario: Separate iOS workbook

- **WHEN** an iOS scan writes findings and `ios.spreadsheet_id` differs from `android.spreadsheet_id`
- **THEN** iOS findings SHALL be written only to the iOS workbook

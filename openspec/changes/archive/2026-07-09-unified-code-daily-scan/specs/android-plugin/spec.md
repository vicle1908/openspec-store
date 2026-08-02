## ADDED Requirements

### Requirement: Android Plugin Registration And Configuration

The system SHALL provide an `AndroidPlugin` implementing `PlatformPlugin`, registered in `PLUGINS` under the key `"android"`, with `name = "android"` and `supported_extensions = (".kt", ".kts", ".java", ".xml", ".gradle", ".groovy")`.

#### Scenario: Android plugin resolved

- **WHEN** the CLI is invoked with `--platform android`
- **THEN** the core SHALL select `AndroidPlugin` and scan only files whose extension is in `supported_extensions`

### Requirement: Android Rule Loading From Markdown

The system SHALL load Android rules from `{worktree}/docs/rules/categories/*.md`, parsing the bullet-pattern Markdown dialect where each detection pattern is a bullet line under `- Detection patterns:` (not a fenced code block). It SHALL fall back to `config/rule_patterns.yaml` when those documents are absent.

The parser MUST extract `rule_id` from the `## <id> - <title>` heading (supporting both `C1` and `RCA-ARCH-001` forms), `priority` from `- Priority:`, `category` inferred from the filename, one `pattern` per bullet under `- Detection patterns:`, `title` from the heading text, and `description` from `- Why it matters:`.

#### Scenario: Parse a crash rule with multiple patterns

- **WHEN** `crash-runtime.md` contains a `## C1 - ...` rule with several bullet detection patterns
- **THEN** the loader SHALL produce a `RulePattern` for `C1` with category `Crash` and one entry per detection-pattern bullet

#### Scenario: Category inferred from filename

- **WHEN** a rule is parsed from `memory-lifecycle.md`
- **THEN** its category SHALL be `Memory Leak`, derived from the filename convention

### Requirement: Android Path-Based Tab Resolution

The system SHALL resolve the spreadsheet tab for an Android finding from the file path using the cross-platform unified taxonomy: `Auth`, `Home`, `WatchList`, `Market`, `Trade`, `Community`, `Me/Settings`, `Deposit/Withdraw`, `Form`, `Common`, `Others`. Resource files SHALL map to `Common`, and unknown modules SHALL map to `Others`. The set of tabs MUST agree with the canonical `feature_resolver.FEATURE_TAB_MAP`.

#### Scenario: Known module path

- **WHEN** a finding's path contains a recognized module prefix such as `trade/`
- **THEN** `resolve_finding_tab` SHALL return the mapped tab (`Trade`)

#### Scenario: Resource file with feature=Common

- **WHEN** a finding's `file_path` is `PoemsUIComponents/src/main/res/values/styles.xml` and `feature` is `Common`
- **THEN** `resolve_finding_tab` SHALL return `Common`. The resource-file extension check is a last-resort fallback and SHALL NOT mask the resolver's answer.

#### Scenario: Unknown module path

- **WHEN** a finding's path matches no module prefix
- **THEN** `resolve_finding_tab` SHALL return `Others`. There is no `Infrastructure` tab; the system SHALL NOT route to a fabricated tab name.

### Requirement: Android Coverage Levels

The system SHALL support a `baseline` coverage level limited to Crash, Lifecycle, Performance, and Security categories, and a `full` coverage level covering all categories.

#### Scenario: Baseline coverage

- **WHEN** `scan --platform android --coverage baseline` runs
- **THEN** only Crash, Lifecycle, Performance, and Security rules SHALL be evaluated

### Requirement: Android Spreadsheet Target

The system SHALL determine the Android spreadsheet from `android.spreadsheet_id` in `~/.tdt/code-daily-scan.yaml`, overridable by the `ANDROID_SCAN_SPREADSHEET_ID` environment variable.

#### Scenario: Environment override

- **WHEN** `ANDROID_SCAN_SPREADSHEET_ID` is set
- **THEN** it SHALL take precedence over the value in the config file

#### Scenario: Legacy `android_scan` section is not read at runtime

- **WHEN** `~/.tdt/config.yaml` contains a legacy `android_scan.spreadsheet_id` and `~/.tdt/code-daily-scan.yaml` is absent
- **THEN** the system SHALL NOT read the legacy section; the operator MUST run `code-daily-scan migrate-config` to import it, or the system SHALL fall through to the built-in empty default

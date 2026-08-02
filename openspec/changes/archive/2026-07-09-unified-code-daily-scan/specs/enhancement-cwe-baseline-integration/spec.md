## ADDED Requirements

### Requirement: CWE Mapping On Findings

The system SHALL support an optional `cwe_id` field on `RulePattern` and propagate it onto each `Finding`, parsed from a `- CWE:` field in the rule markdown (for example `- CWE: ` set to `CWE-400`). When a rule declares no CWE, `cwe_id` SHALL be `None` and the finding SHALL still be emitted.

CWE identifiers MUST be assigned per the rule's actual `- Category:` and intent. The pre-existing iOS CWE label table is non-authoritative and MUST be reconciled against the rule books before use (verified discrepancies: `C4` is a `crash.md` rule with category `Crash`, not "Design Issues"; `S3` is a `swiftui.md` rule with category `SwiftUI`, not "Synchronization"; concurrency rules `C7`–`C10` are not yet represented).

#### Scenario: CWE parsed from rule markdown

- **WHEN** a rule document contains a `- CWE:` field
- **THEN** the loader SHALL set the rule's `cwe_id` and findings produced from it SHALL carry that `cwe_id`

#### Scenario: Missing CWE is non-fatal

- **WHEN** a rule document omits the `- CWE:` field
- **THEN** the finding SHALL have `cwe_id = None` and SHALL otherwise be emitted normally

#### Scenario: CWE column in sheet output

- **WHEN** findings are written to a spreadsheet tab
- **THEN** the output SHALL include a CWE column populated from each finding's `cwe_id` (blank when unset)

### Requirement: False Positive Tracking

The system SHALL support marking findings as false positives and SHALL persist these decisions in a dedicated `FP-Tracking` sheet tab keyed by rule ID, file path, and a content hash, recording reason, verifier, and timestamp.

The `Finding` model MUST carry `is_false_positive`, `false_positive_reason`, `verified_by`, and `verified_at` fields, defaulting to a non-false-positive state. The system SHALL also apply auto-detection heuristics that classify findings in test or generated paths as likely false positives.

#### Scenario: Mark a finding as false positive

- **WHEN** the user runs the `mark-false-positive` command for a finding
- **THEN** the system SHALL record the decision in `FP-Tracking` with reason, verifier, and timestamp, and SHALL suppress that finding's blocking effect on subsequent runs

#### Scenario: Auto-detected false positive in test path

- **WHEN** a finding's path matches a known test or generated-file pattern
- **THEN** the system SHALL flag it as a likely false positive rather than reporting it as an active issue

### Requirement: Metrics Framework

The system SHALL compute and persist scan KPIs to a dedicated `Metrics` sheet tab, including total findings, per-priority counts, false-positive count, KLOC, findings-per-KLOC, and false-positive rate, with one row per scan date.

#### Scenario: Metrics row appended per scan

- **WHEN** a daily scan completes
- **THEN** the system SHALL append a `Metrics` row containing the date, finding counts by priority, false-positive count, KLOC, findings-per-KLOC, and false-positive rate

#### Scenario: Report metrics on demand

- **WHEN** the user runs the `report-metrics` command
- **THEN** the system SHALL emit the current KPI values and chart-ready trend data

### Requirement: Optional Tooling Integration

The system SHALL support an optional extended scan, enabled by a `--full-scan` flag, that augments grep findings with Semgrep rule export, MobSF binary analysis, and SBOM-based dependency vulnerability checks. These integrations MUST be non-fatal: when a tool or its input is unavailable, the scan SHALL continue and report the integration as skipped.

#### Scenario: Full scan with tooling available

- **WHEN** `--full-scan` is set and the tooling inputs exist
- **THEN** the system SHALL include Semgrep, MobSF, and dependency findings mapped into the shared `Finding` format

#### Scenario: Tooling unavailable is non-fatal

- **WHEN** `--full-scan` is set but a tool or its input artifact is missing
- **THEN** the system SHALL skip that integration, mark it skipped in the output, and complete the rest of the scan

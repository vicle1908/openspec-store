# structured-findings Specification

## Purpose

`structured-findings` is the capability that defines how `ai-review` normalizes LLM reviewer output into typed `StructuredFinding` objects, validates them against the MR diff, deduplicates cross-reviewer duplicates, and renders them as GitLab MR comment lines.
## Requirements
### Requirement: StructuredFinding model

The system SHALL provide a `StructuredFinding` model (in `src/ai_review/validation/models.py`) with fields: `category`, `severity`, `file_path`, `line_start`, `line_end`, `description`, and optional `suggestion`. Each field SHALL be type-checked at construction time; invalid types SHALL raise `ValueError`.

#### Scenario: valid finding constructs

- **WHEN** `StructuredFinding(category="BUG", severity="HIGH", file_path="src/main.py", line_start=10, line_end=12, description="off-by-one")` is constructed
- **THEN** the object is returned with all fields populated

#### Scenario: invalid type raises ValueError

- **WHEN** `StructuredFinding(category="BUG", severity="HIGH", file_path="src/main.py", line_start="10", line_end=12, description="x")` is constructed
- **THEN** a `ValueError` is raised mentioning `line_start` and the expected `int` type

### Requirement: ValidationContext enforces finding validity

The `ValidationContext` (in `src/ai_review/validation/context.py`) SHALL reject findings that fail any of: line range validity, file path existence, severity-category alignment, description quality. Invalid findings SHALL be logged with the reason and dropped from the rendered MR note.

#### Scenario: line range invalid

- **WHEN** a finding has `line_start > line_end`
- **THEN** the finding is rejected with `reason="invalid_line_range"`

#### Scenario: file path not in diff

- **WHEN** a finding references a file that is not in the MR diff
- **THEN** the finding is rejected with `reason="file_not_in_diff"`

#### Scenario: SEC category requires HIGH/CRITICAL severity

- **WHEN** a finding has `category="SEC"` and `severity="LOW"`
- **THEN** the finding is rejected with `reason="severity_category_mismatch"`

### Requirement: FindingDeduplicator collapses cross-reviewer duplicates

The `FindingDeduplicator` (in `src/ai_review/validation/deduplicator.py`) SHALL collapse findings from multiple reviewers with key `(file_path, line_start, line_end, description_hash)`. The merge policy SHALL keep the highest severity and concatenate suggestions.

#### Scenario: identical findings from two reviewers

- **GIVEN** reviewer A emits finding F1 with severity=LOW
- **AND** reviewer B emits finding F1 with severity=HIGH
- **WHEN** deduplication runs
- **THEN** exactly one finding is rendered with severity=HIGH and a comment noting "[merged from A, B]"

#### Scenario: non-overlapping findings preserved

- **GIVEN** findings F1, F2, F3 with distinct keys
- **WHEN** deduplication runs
- **THEN** all three findings are rendered

### Requirement: Backward compatibility with legacy freeform notes

The orchestrator SHALL fall back to the legacy review note rendering path when `StructuredFinding` extraction yields zero findings. The legacy path SHALL use the unchanged freeform review note format. No existing reviewer output SHALL be silently dropped.

#### Scenario: zero structured findings

- **WHEN** the orchestrator extracts zero findings from reviewer output
- **THEN** the legacy freeform review note is rendered as the MR comment
- **AND** no structured-finding rendering is attempted

#### Scenario: existing notes still parseable

- **WHEN** legacy freeform notes are parsed by the orchestrator
- **THEN** the orchestrator does not raise and renders the notes verbatim

_(Additional documentation requirements are tracked in the change's verification checklist.)_

### Requirement: Finding extraction SHALL parse LLM output into structured format

The finding extractor SHALL identify findings using markdown list patterns,
section headers, and inline severity markers.

#### Scenario: Markdown list item is extracted

```python
# Input
output = """


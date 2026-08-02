# ai-review Structured Findings Specification

## Purpose

Define the structured finding model, extraction, validation, and deduplication
contract for the `ai-review` service. This spec is the source of truth for
what constitutes a valid, publishable finding.

## Overview

Current state: Findings are published as raw strings with hardcoded `"suggestion"`
severity, no file/line context, and no deduplication across reviewers.

Target state: Findings are structured objects with severity, file, line, message,
confidence, extracted from LLM output, validated against diff context, and
deduplicated before publication.

## Data Models

### StructuredFinding

```python
@dataclass(slots=True)
class StructuredFinding:
    severity: str           # "critical", "high", "medium", "low", "suggestion"
    file: str | None       # Path relative to repo root
    line: int | None       # Line number in file
    message: str           # Human-readable finding message
    confidence: str         # "high", "medium", "low"
    reviewer: str           # Source reviewer (kimi, claude, codex, pi)
    raw_text: str           # Original LLM output for this finding
```

### Finding Extraction Patterns

Findings SHALL be extracted from LLM output using these patterns:

#### Pattern 1: Markdown List Item
```markdown
- [critical] file/path.swift:15 - Memory leak in closure
- [high] src/utils.js - Missing null check
```

#### Pattern 2: Section Header
```markdown
## Critical Issues
### file.swift:42 - Issue description
```

#### Pattern 3: Inline Severity
```markdown
CRITICAL in ViewController.swift line 55: Description
```

### Finding Severity Levels

| Level | Description | Publish Threshold |
|-------|-------------|------------------|
| critical | Security vulnerability, data loss, crash | Always |
| high | Major bug, significant performance issue | Always |
| medium | Code quality, maintainability concern | Medium+ confidence |
| low | Style, minor optimization | High confidence only |
| suggestion | Informational, no action required | Never (filtered) |

## ADDED Requirements

### Requirement: Finding extraction SHALL parse LLM output into structured format

The finding extractor SHALL identify findings using markdown list patterns,
section headers, and inline severity markers.

#### Scenario: Markdown list item is extracted

```python
# Input
output = """
## Review Summary
- [critical] src/app.swift:42 - Memory leak in closure
- [high] lib/utils.kt - Missing null check
"""

# Expected output
findings = [
    StructuredFinding(
        severity="critical",
        file="src/app.swift",
        line=42,
        message="Memory leak in closure",
        confidence="medium",  # Default if not specified
        reviewer="kimi",
        raw_text="- [critical] src/app.swift:42 - Memory leak in closure"
    ),
    StructuredFinding(
        severity="high",
        file="lib/utils.kt",
        line=None,  # Line not parseable
        message="Missing null check",
        confidence="medium",
        reviewer="kimi",
        raw_text="- [high] lib/utils.kt - Missing null check"
    ),
]
```

### Requirement: Findings SHALL be validated against diff context

Before publication, findings SHALL be validated for context relevance.

#### Scenario: File not in diff is suppressed

```python
finding = StructuredFinding(
    severity="high",
    file="src/not_changed.swift",
    line=10,
    message="Bug in unchanged file"
)
diff_text = "...src/changed.swift..."

validated = validator.validate(finding, diff_text)

assert validated.suppressed == True
assert validated.suppression_reason == "file_not_in_diff"
```

#### Scenario: Line number out of range is adjusted

```python
finding = StructuredFinding(
    severity="medium",
    file="src/changed.swift",
    line=9999,  # File only has 100 lines
    message="Style issue"
)
diff_text = "...file with 100 lines..."

validated = validator.validate(finding, diff_text)

# Line is clamped to max valid line
assert validated.line <= max_valid_line
```

#### Scenario: Unused import finding with no import in diff

```python
finding = StructuredFinding(
    severity="suggestion",
    file="src/app.swift",
    line=5,
    message="Unused import should be removed"
)
diff_text = "func main() { print(\"hi\") }"  # No import

validated = validator.validate(finding, diff_text)

assert validated.suppressed == True
assert validated.suppression_reason == "no_matching_import"
```

### Requirement: Findings SHALL be deduplicated across reviewers

Duplicate findings from multiple reviewers SHALL be merged.

#### Scenario: Identical finding from two reviewers is deduplicated

```python
findings = [
    StructuredFinding(severity="high", file="a.swift", line=10, message="Null check", reviewer="kimi"),
    StructuredFinding(severity="high", file="a.swift", line=10, message="Null check", reviewer="claude"),
    StructuredFinding(severity="high", file="a.swift", line=10, message="Null check", reviewer="codex"),
]

deduplicated = deduplicator.deduplicate(findings)

assert len(deduplicated) == 1
assert deduplicated[0].reviewer == "kimi, claude, codex"  # Merged
```

#### Scenario: Similar but different findings are preserved

```python
findings = [
    StructuredFinding(severity="high", file="a.swift", line=10, message="Null check missing"),
    StructuredFinding(severity="medium", file="a.swift", line=11, message="Similar but different"),
]

deduplicated = deduplicator.deduplicate(findings)

assert len(deduplicated) == 2  # Both preserved
```

### Requirement: Severity calibration SHALL adjust based on context

Findings SHALL have severity adjusted based on validation results.

#### Scenario: High severity for memory leak without weak reference

```python
finding = StructuredFinding(
    severity="high",
    message="Potential memory leak in closure"
)

validated = validator.validate(finding, diff_text)
# diff_text has no "[weak" reference

assert validated.confidence == "high"
```

#### Scenario: Confidence downgraded for memory leak WITH weak reference

```python
finding = StructuredFinding(
    severity="high",
    message="Potential memory leak in closure"
)

validated = validator.validate(finding, diff_text)
# diff_text contains "[weak self]"

assert validated.confidence == "medium"
assert validated.severity_adjusted == True
```

### Requirement: Publication format SHALL include structured finding metadata

Published review notes SHALL include structured finding format for parsing.

#### Scenario: Structured findings in publication

```markdown
## AI Review Summary

**Reviewed by:** kimi, claude, codex
**Findings:** 3 (2 critical, 1 high)

### [CRITICAL] Memory leak in closure
- **File:** src/app.swift
- **Line:** 42
- **Confidence:** high
- **Reviewers:** kimi, claude

### [HIGH] Missing null check
- **File:** lib/utils.kt
- **Line:** 15
- **Confidence:** medium
- **Reviewers:** codex

### [MEDIUM] Unused variable
- **File:** src/main.swift
- **Line:** 100
- **Confidence:** high
- **Reviewers:** kimi
```

## Validation Rules

| Rule | Condition | Action |
|------|-----------|--------|
| file_not_in_diff | File path not in diff | Suppress |
| line_out_of_range | Line > max line in file | Clamp to max |
| no_import_for_unused | "unused import" but no import | Suppress |
| weak_reference | "memory leak" with [weak self] | Downgrade confidence |
| generic_message | Message matches no-content pattern | Flag for review |
| duplicate | Same file+line+similar message | Deduplicate |

## Deduplication Algorithm

Findings are deduplicated using:

1. **Exact match**: Same file, line, and message (case-insensitive)
2. **Fuzzy match**: Levenshtein distance < 3 for message
3. **Clustering**: Group by file, then by line proximity (within 3 lines)

Merged findings SHALL:
- Keep highest severity
- Keep highest confidence
- Combine reviewer list with comma separation
- Keep longest raw_text

## Integration Points

### ReviewOrchestrator Changes

```python
# Before
if execution.message:
    finding = ValidatedFinding(
        severity="suggestion",  # Hardcoded!
        file=None,
        line=None,
        message=execution.message,
        confidence=ConfidenceLevel.MEDIUM,
    )

# After
if execution.message:
    findings = finding_parser.extract(execution.message)
    for finding in findings:
        validated = validator.validate(finding, diff_text)
        calibrated = calibrator.calibrate(validated)
        if calibrated.include:
            publishable.append(calibrated)
```

### CoverageScanner Integration

Coverage gap detection SHALL trigger re-review:

```python
def on_coverage_gap(gap: CoverageGap):
    if gap.reason == "stale_review":
        # Re-trigger review for this MR
        payload = ReviewIntakeRequest(...)
        orchestrator.enqueue(payload, handoff_id=...)
```

## Open Questions

1. **Extraction confidence**: How to determine initial confidence for extracted findings?
2. **Fuzzy threshold**: What Levenshtein distance threshold for "similar" messages?
3. **Reviewer weighting**: Should some reviewers have higher weight in confidence calculation?
4. **False positive handling**: How to suppress clearly wrong findings without manual config?

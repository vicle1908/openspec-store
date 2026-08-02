## Purpose

This specification defines requirements for Validation Consistency.

# Validation Consistency Spec

## Overview

Refactor ai-review validation pipeline for consistency.

## Requirements

### Requirement: GENERIC_PATTERNS Consolidation

`validation/models.py` MUST export `GENERIC_PATTERNS` as a module-level constant.

`validation/parser.py` MUST import `GENERIC_PATTERNS` from `models`.

`validation/context.py` MUST import `GENERIC_PATTERNS` from `models`.

No duplicate pattern definitions allowed.

#### Scenario: Parser imports consolidated patterns

- Given: `GENERIC_PATTERNS` is defined in `models.py`
- When: `parser.py` is imported
- Then: `parser.py` uses `from ai_review.validation.models import GENERIC_PATTERNS`

#### Scenario: Context imports consolidated patterns

- Given: `GENERIC_PATTERNS` is defined in `models.py`
- When: `context.py` is imported
- Then: `context.py` uses `from ai_review.validation.models import GENERIC_PATTERNS`

### Requirement: EnhancedValidationContext Integration

`orchestrator.py` MUST use enhanced validation rules.

Enhanced rules MUST be applied:
- FILE_NOT_IN_DIFF: Reject findings for files not in diff
- LINE_OUT_OF_RANGE: Clamp line numbers to valid range
- NO_IMPORT_FOR_UNUSED: Reject unused import findings without imports
- WEAK_REFERENCE: Downgrade memory leak confidence when weak refs present
- GENERIC_MESSAGE: Suppress findings with generic messages

#### Scenario: Generic message suppressed

- Given: A finding with message "fix this"
- When: ValidationContext.validate() is called
- Then: The finding is suppressed with reason "generic message"

#### Scenario: File not in diff rejected

- Given: A finding with file="NonExistent.swift"
- And: The diff does not contain "NonExistent.swift"
- When: ValidationContext.validate() is called
- Then: The finding is suppressed with reason "file not in diff"

### Requirement: Confidence Propagation

Parser-extracted confidence MUST be used in validation.

If confidence is invalid, fallback to `ConfidenceLevel.MEDIUM`.

Confidence MUST be preserved through calibration stage.

#### Scenario: Parser confidence is used

- Given: A finding extracted with confidence="high"
- When: Validation is performed
- Then: The ValidatedFinding has confidence=ConfidenceLevel.HIGH

#### Scenario: Invalid confidence fallback

- Given: A finding with confidence="invalid"
- When: Validation is performed
- Then: The ValidatedFinding has confidence=ConfidenceLevel.MEDIUM

### Requirement: Reviewer Propagation

`SeverityCalibrator.calibrate()` MUST propagate reviewers list.

`CalibratedFinding` MUST include reviewers field from ValidatedFinding.

Early publication MUST show all reviewers who flagged each finding.

#### Scenario: Reviewers propagate through calibration

- Given: A ValidatedFinding with reviewers=["claude", "kimi"]
- When: SeverityCalibrator.calibrate() is called
- Then: The CalibratedFinding has reviewers=["claude", "kimi"]

## Acceptance Criteria

1. All GENERIC_PATTERNS definitions consolidated to single location
2. Enhanced validation rules wired into ValidationContext
3. Parser confidence used (not hardcoded)
4. Reviewers propagated through calibration
5. All existing tests pass (with necessary updates)

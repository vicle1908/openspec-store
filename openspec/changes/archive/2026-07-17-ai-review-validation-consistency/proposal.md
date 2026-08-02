## Why

The ai-review validation pipeline has 4 consistency issues discovered during code review: (1) duplicate GENERIC_PATTERNS defined in 3 locations, (2) EnhancedValidationContext not wired into the main flow, (3) parser confidence being ignored, and (4) reviewers field not propagated through calibration. These issues cause degraded validation quality and maintenance burden.

## What Changes

1. **Consolidate GENERIC_PATTERNS** - Define once in `validation/models.py`, import everywhere
2. **Migrate to EnhancedValidationContext** - Wire the rich validation rules into the main orchestrator
3. **Use parser confidence** - Replace hardcoded `ConfidenceLevel.MEDIUM` with extracted confidence
4. **Propagate reviewers field** - Pass reviewers through SeverityCalibrator to CalibratedFinding

## Capabilities

### New Capabilities

- `validation-consistency`: Core refactoring of ai-review validation pipeline for consistency

### Modified Capabilities

- `mr-review-orchestration`: Updated to use EnhancedValidationContext and propagate confidence/reviewers

## Impact

- **Files affected**: `parser.py`, `context.py`, `severity.py`, `orchestrator.py`
- **Models affected**: `StructuredFinding`, `ValidatedFinding`, `CalibratedFinding`
- **No breaking API changes**: Internal refactoring only
- **Tests**: Update to match new behavior

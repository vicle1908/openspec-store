# Implementation Tasks

## ai-review-validation-consistency

### Phase 1: Consolidate GENERIC_PATTERNS

- [x] 1.1 Add `GENERIC_PATTERNS` constant to `validation/models.py`
- [x] 1.2 Update `validation/parser.py` to import from models
- [x] 1.3 Update `validation/context.py` to import from models
- [x] 1.4 Remove duplicate definitions from parser.py and context.py

### Phase 2: Migrate to EnhancedValidationContext

- [x] 2.1 Update `orchestrator.py` import to use `EnhancedValidationContext`
- [x] 2.2 Update orchestrator to handle `ValidationResult` return type
- [x] 2.3 Add reviewers list to ValidatedFinding in orchestrator

### Phase 3: Use Parser Confidence

- [x] 3.1 Update orchestrator to use extracted confidence
- [x] 3.2 Add try/except with MEDIUM fallback for invalid confidence

### Phase 4: Propagate Reviewers

- [x] 4.1 Update `SeverityCalibrator.calibrate()` to accept and propagate reviewers
- [x] 4.2 Update CalibratedFinding creation with reviewers list

### Phase 5: Testing

- [x] 5.1 Update validation tests for new behavior
- [x] 5.2 Run full test suite
- [x] 5.3 Fix any test failures

### Phase 6: Verification

- [x] 6.1 Run ruff/mypy checks
- [x] 6.2 Verify all changes in git diff
- [x] 6.3 Commit changes
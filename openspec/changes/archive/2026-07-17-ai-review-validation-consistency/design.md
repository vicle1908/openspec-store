## Context

The ai-review validation pipeline processes MR reviews through: Parser → Validator → Calibrator → Deduplicator → Poster. Analysis revealed 4 consistency issues:

1. **Duplicate GENERIC_PATTERNS**: Defined identically in 3 files (parser.py, context.py x2)
2. **Legacy ValidationContext**: Main orchestrator uses lightweight legacy class; EnhancedValidationContext has richer rules but is unused
3. **Confidence ignored**: Parser extracts confidence but orchestrator hardcodes `ConfidenceLevel.MEDIUM`
4. **Reviewers not propagated**: SeverityCalibrator doesn't pass reviewers to CalibratedFinding

## Goals / Non-Goals

**Goals:**
- Single source of truth for GENERIC_PATTERNS in validation/models.py
- Wire EnhancedValidationContext into main orchestrator flow
- Use parser-extracted confidence instead of hardcoded value
- Propagate reviewers field through calibration stage

**Non-Goals:**
- No API changes to StructuredFinding, ValidatedFinding, CalibratedFinding
- No changes to GitLab posting logic
- No changes to deduplication logic (already handles reviewers)

## Decisions

### 1. Define GENERIC_PATTERNS in models.py

**Decision:** Create `GENERIC_PATTERNS` as a module-level constant in `validation/models.py`.

**Rationale:** Centralizes the pattern definition, allows import in parser.py and context.py.

**Alternatives considered:**
- Define in context.py and import to parser.py (parser would depend on context)
- Keep duplicated (rejected - maintenance burden)

### 2. Migrate to EnhancedValidationContext

**Decision:** Replace `ValidationContext` with `EnhancedValidationContext` in orchestrator.

**Rationale:** EnhancedValidationContext has FILE_NOT_IN_DIFF, LINE_OUT_OF_RANGE, NO_IMPORT_FOR_UNUSED rules that improve finding quality.

**Alternative considered:**
- Keep both and add migration flag (rejected - adds complexity)

### 3. Use parser confidence

**Decision:** Pass `ConfidenceLevel(structured_finding.confidence)` instead of hardcoded MEDIUM.

**Rationale:** Parser already extracts confidence; this makes validation use actual extracted values.

**Alternative considered:**
- Keep hardcoded MEDIUM for safety (rejected - defeats purpose of confidence extraction)

### 4. Propagate reviewers in calibrator

**Decision:** Add `reviewers=finding.reviewers` to CalibratedFinding construction.

**Rationale:** Early publication will then show which reviewers flagged each finding.

## Migration Plan

1. Update validation/models.py with GENERIC_PATTERNS
2. Update parser.py to import from models
3. Update context.py to import from models
4. Update orchestrator to use EnhancedValidationContext
5. Update orchestrator to use parser confidence
6. Update SeverityCalibrator to propagate reviewers
7. Update tests to match new behavior
8. Run tests to verify

**Rollback:** Revert to previous commits if issues arise.

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| EnhancedValidationContext has different API | Update orchestrator to use new return type |
| Parser confidence may be invalid enum | Use try/except with MEDIUM fallback |
| Tests may need updates | Run full test suite after changes |

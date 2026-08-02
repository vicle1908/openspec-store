# ai-review Structured Findings: Design

## Context

The current `ai-review` system publishes findings as raw strings with:
- Hardcoded `"suggestion"` severity
- No file/line context
- No deduplication across reviewers

This design addresses these gaps with a structured finding pipeline.

## Goals

1. Extract structured findings from LLM output
2. Validate findings against diff context
3. Deduplicate findings across reviewers
4. Publish in structured format for parsing

## Decisions

### Decision 1: Regex-based extraction over LLM parsing

**Chosen:** Regex patterns for extraction

**Rationale:**
- Deterministic and fast
- No additional LLM call needed
- Patterns can be refined over time
- Aligns with existing pattern matching in codebase

**Alternative considered:** LLM-based extraction
- Would add latency and cost
- Non-deterministic output
- More complex error handling

### Decision 2: Multi-pass extraction with fallback

**Chosen:** Try patterns in order: markdown list → section header → inline

**Rationale:**
- Different reviewers output in different formats
- Each pattern has different precision/recall trade-off
- Fallback ensures at least some findings extracted

### Decision 3: Levenshtein distance for fuzzy matching

**Chosen:** Levenshtein distance < 3 for message similarity

**Rationale:**
- Standard string similarity metric
- Threshold of 3 catches typos/variations
- Not too strict to miss related findings
- Fast to compute for small strings

### Decision 4: In-memory deduplication

**Chosen:** Deduplicate in-process before publication

**Rationale:**
- Reviewer outputs are small enough
- No external storage needed
- Simple implementation
- Sufficient for current scale

**Alternative considered:** Persistent deduplication store
- Would track findings across MRs
- More complex
- Premature optimization

## Implementation

### 1. Finding Parser Module

```python
# src/ai_review/validation/parser.py

import re
from dataclasses import dataclass

@dataclass
class ExtractionResult:
    findings: list[StructuredFinding]
    raw_findings: list[str]  # Unextracted lines
    confidence: float  # 0.0-1.0

class FindingParser:
    MARKDOWN_PATTERN = re.compile(
        r'-\s*\[?(critical|high|medium|low|suggestion)\]?\s+'
        r'(?:([^:\s]+):(\d+)\s+)?'  # Optional file:line
        r'[-\s]+(.+)'
    )
    
    SECTION_PATTERN = re.compile(
        r'##\s+\[?(CRITICAL|HIGH|MEDIUM|LOW)\]?\s+(.+)'
    )
    
    INLINE_PATTERN = re.compile(
        r'(CRITICAL|HIGH|MEDIUM|LOW)\s+in\s+([^\s]+)\s+'
        r'(?:line\s+)?(\d+)?:?\s*(.+)'
    )
    
    def parse(self, output: str, reviewer: str) -> ExtractionResult:
        findings = []
        raw_lines = []
        
        # Try markdown pattern first
        for line in output.splitlines():
            match = self.MARKDOWN_PATTERN.match(line.strip())
            if match:
                findings.append(self._to_structured(match, reviewer))
            elif self.SECTION_PATTERN.match(line.strip()):
                # Handle section headers...
                pass
            else:
                raw_lines.append(line)
        
        return ExtractionResult(
            findings=findings,
            raw_findings=raw_lines,
            confidence=len(findings) / max(1, len(output.splitlines()))
        )
    
    def _to_structured(self, match: re.Match, reviewer: str) -> StructuredFinding:
        severity = match.group(1).lower()
        file = match.group(2)
        line = int(match.group(3)) if match.group(3) else None
        message = match.group(4).strip()
        
        return StructuredFinding(
            severity=severity,
            file=file,
            line=line,
            message=message,
            confidence="medium",  # Default
            reviewer=reviewer,
            raw_text=match.group(0)
        )
```

### 2. Enhanced ValidationContext

```python
# src/ai_review/validation/context.py (enhanced)

from dataclasses import dataclass
from enum import StrEnum

class ValidationRule(StrEnum):
    FILE_NOT_IN_DIFF = "file_not_in_diff"
    LINE_OUT_OF_RANGE = "line_out_of_range"
    NO_IMPORT_FOR_UNUSED = "no_matching_import"
    WEAK_REFERENCE = "weak_reference_in_closure"
    GENERIC_MESSAGE = "generic_message_pattern"
    DUPLICATE = "duplicate_finding"

@dataclass
class ValidationResult:
    valid: bool
    rule: ValidationRule | None
    message: str | None
    adjustment: str | None  # e.g., "line_clamped", "confidence_downgraded"

class EnhancedValidationContext:
    GENERIC_PATTERNS = [
        r'^fix this$',
        r'^issue found$',
        r'^needs review$',
        r'^\[?(critical|high|medium|low)\]?\s*$',  # Severity only
    ]
    
    def validate(
        self, 
        finding: StructuredFinding, 
        diff_text: str,
        max_line: int | None = None
    ) -> ValidationResult:
        # Rule 1: File not in diff
        if finding.file:
            if finding.file not in diff_text:
                return ValidationResult(
                    valid=False,
                    rule=ValidationRule.FILE_NOT_IN_DIFF,
                    message=f"File {finding.file} not in diff",
                    adjustment=None
                )
        
        # Rule 2: Line out of range
        if finding.line and max_line:
            if finding.line > max_line:
                finding.line = max_line  # Adjust in-place
                return ValidationResult(
                    valid=True,
                    rule=ValidationRule.LINE_OUT_OF_RANGE,
                    message=f"Line {finding.line} clamped to {max_line}",
                    adjustment="line_clamped"
                )
        
        # Rule 3: Unused import without import
        if "unused import" in finding.message.lower():
            if "import" not in diff_text.lower():
                return ValidationResult(
                    valid=False,
                    rule=ValidationRule.NO_IMPORT_FOR_UNUSED,
                    message="No import found in diff",
                    adjustment=None
                )
        
        # Rule 4: Memory leak with weak reference
        if "memory leak" in finding.message.lower():
            if "[weak" in diff_text.lower() or "weak self" in diff_text.lower():
                finding.confidence = "low"  # Downgrade
                return ValidationResult(
                    valid=True,
                    rule=ValidationRule.WEAK_REFERENCE,
                    message="Found weak reference, downgrading confidence",
                    adjustment="confidence_downgraded"
                )
        
        # Rule 5: Generic message
        for pattern in self.GENERIC_PATTERNS:
            if re.match(pattern, finding.message, re.IGNORECASE):
                return ValidationResult(
                    valid=False,
                    rule=ValidationRule.GENERIC_MESSAGE,
                    message="Message too generic",
                    adjustment=None
                )
        
        return ValidationResult(valid=True, rule=None, message=None, adjustment=None)
```

### 3. Finding Deduplicator

```python
# src/ai_review/validation/deduplicator.py

from dataclasses import dataclass
from levenshtein import distance as levenshtein_distance

@dataclass
class DeduplicationResult:
    unique: list[StructuredFinding]
    duplicates_removed: int
    merged_reviewers: list[dict]  # Maps dedup key to merged reviewers

class FindingDeduplicator:
    FUZZY_THRESHOLD = 3  # Levenshtein distance
    
    def deduplicate(self, findings: list[StructuredFinding]) -> DeduplicationResult:
        unique = []
        duplicates_removed = 0
        merged_map: dict[str, list[StructuredFinding]] = {}
        
        for finding in findings:
            key = self._dedup_key(finding)
            
            # Find exact match
            exact = self._find_exact_match(key, unique)
            if exact:
                self._merge(exact, finding)
                duplicates_removed += 1
                continue
            
            # Find fuzzy match
            fuzzy = self._find_fuzzy_match(finding, unique)
            if fuzzy:
                self._merge(fuzzy, finding)
                duplicates_removed += 1
                continue
            
            unique.append(finding)
        
        # Merge reviewer lists
        for finding in unique:
            if finding.reviewer_count > 1:
                finding.reviewers = self._format_reviewers(finding.reviewers)
        
        return DeduplicationResult(
            unique=unique,
            duplicates_removed=duplicates_removed,
            merged_reviewers=[]
        )
    
    def _dedup_key(self, finding: StructuredFinding) -> str:
        return f"{finding.file}:{finding.line}:{finding.message.lower()}"
    
    def _find_exact_match(self, key: str, candidates: list[StructuredFinding]) -> StructuredFinding | None:
        for c in candidates:
            c_key = self._dedup_key(c)
            if key == c_key:
                return c
        return None
    
    def _find_fuzzy_match(self, finding: StructuredFinding, candidates: list[StructuredFinding]) -> StructuredFinding | None:
        for c in candidates:
            if c.file != finding.file:
                continue
            if abs((c.line or 0) - (finding.line or 0)) > 3:
                continue
            dist = levenshtein_distance(finding.message.lower(), c.message.lower())
            if dist <= self.FUZZY_THRESHOLD:
                return c
        return None
    
    def _merge(self, existing: StructuredFinding, new: StructuredFinding):
        # Keep highest severity
        if self._severity_rank(new.severity) > self._severity_rank(existing.severity):
            existing.severity = new.severity
        
        # Keep highest confidence
        if self._confidence_rank(new.confidence) > self._confidence_rank(existing.confidence):
            existing.confidence = new.confidence
        
        # Track reviewers
        if not hasattr(existing, 'reviewers'):
            existing.reviewers = [existing.reviewer]
        existing.reviewers.append(new.reviewer)
        existing.reviewer_count = len(existing.reviewers)
        
        # Keep longest message
        if len(new.message) > len(existing.message):
            existing.message = new.message
            existing.raw_text = new.raw_text
    
    def _severity_rank(self, severity: str) -> int:
        return {"critical": 4, "high": 3, "medium": 2, "low": 1, "suggestion": 0}.get(severity, 0)
    
    def _confidence_rank(self, confidence: str) -> int:
        return {"high": 2, "medium": 1, "low": 0}.get(confidence, 0)
```

### 4. Updated Orchestrator

```python
# src/ai_review/review_flow/orchestrator.py (changes)

from ai_review.validation.parser import FindingParser, ExtractionResult
from ai_review.validation.deduplicator import FindingDeduplicator

class ReviewOrchestrator:
    def __init__(self, settings: Settings) -> None:
        # ... existing init ...
        self.finding_parser = FindingParser()
        self.deduplicator = FindingDeduplicator()
    
    def _run_reviewer_once(self, ...):
        # ... existing execution ...
        message = self._extract_message(result.output)
        
        # NEW: Parse structured findings
        if message:
            extraction = self.finding_parser.parse(message, reviewer_name)
            
            for finding in extraction.findings:
                validation_result = self.validator.validate(finding, diff_text)
                calibrated = self.calibrator.calibrate(finding, validation_result)
                
                if calibrated.include:
                    execution.findings.append(calibrated)
        
        # Track raw unparsed content
        if extraction.raw_findings:
            execution.unparsed_lines = extraction.raw_findings
        
        return execution

```

### 5. Structured Publication Format

```python
# src/ai_review/gitlab/review_posting.py (enhanced)

class GitLabReviewPoster:
    def format_findings_markdown(self, findings: list[StructuredFinding]) -> str:
        if not findings:
            return "No findings."
        
        lines = []
        
        # Group by severity
        by_severity = {}
        for f in findings:
            by_severity.setdefault(f.severity, []).append(f)
        
        # Output in severity order
        for severity in ["critical", "high", "medium", "low"]:
            items = by_severity.get(severity, [])
            if not items:
                continue
            
            lines.append(f"### [{severity.upper()}] ({len(items)} issues)")
            
            for f in items:
                file_line = f"{f.file}:{f.line}" if f.file else "general"
                lines.append(f"- **{file_line}**: {f.message}")
                if f.reviewers:
                    lines.append(f"  - Reviewers: {f.reviewers}")
                if f.confidence:
                    lines.append(f"  - Confidence: {f.confidence}")
        
        return "\n".join(lines)
```

## Security Fixes

### Path Traversal Prevention

```python
# src/ai_review/review_flow/context.py (security fix)

class ReviewContextResolver:
    def _resolve_repo_path(self, payload: ReviewIntakeRequest) -> Path | None:
        # ... existing project_id lookup ...
        
        if payload.project:
            workspace_root = Path(
                os.getenv("TDT_WORKSPACE_ROOT", str(Path.home() / "Developer" / "tdt"))
            ).resolve()  # Resolve to absolute path
            
            # Sanitize project name
            safe_project = payload.project.replace("/", "_").replace("\\", "_")
            
            # Explicit path construction (no rsplit vulnerabilities)
            candidate = workspace_root / safe_project
            
            # Security: Ensure final path is within workspace
            try:
                candidate.resolve().relative_to(workspace_root.resolve())
            except ValueError:
                logger.warning("path_traversal_attempt", project=payload.project)
                return None
            
            if candidate.exists():
                return candidate
        
        return None
```

### Timing-Safe Secret Comparison

```python
# src/ai_review/api/app.py (security fix)

import hmac

async def intake_gitlab_mr(...):
    dispatch_secret = ai_review_dispatch_secret
    if dispatch_secret is None:
        raise HTTPException(status_code=401)
    
    # Timing-safe comparison
    if not hmac.compare_digest(dispatch_secret, settings.dispatch_secret):
        raise HTTPException(status_code=403)
```

## Testing Strategy

### Unit Tests

1. **FindingParser**: Test each regex pattern with valid/invalid inputs
2. **EnhancedValidationContext**: Test each validation rule
3. **FindingDeduplicator**: Test exact, fuzzy, and merge logic
4. **Security**: Test path traversal attempts are blocked

### Integration Tests

1. **Full finding pipeline**: Extract → Validate → Deduplicate → Publish
2. **Multi-reviewer deduplication**: kimi + claude → 1 finding

### Benchmark Tests

1. **Parser performance**: < 10ms for typical LLM output
2. **Deduplication performance**: < 50ms for 100 findings

### Offline Utilities (NOT wired into orchestrator)

`CoverageScanner` and `BenchmarkRunner` are **standalone utilities**
exposed via the `mr-coverage` CLI. They are not invoked by the
request-path orchestrator; they are run out-of-band. The original
spec text mentioned "coverage scanning triggers re-review" — that
was never implemented and is intentionally out of scope for the
review flow. Coverage scanning is a separate operational tool.

## Risks & Trade-offs

| Risk | Impact | Mitigation |
|------|--------|------------|
| Regex patterns miss some outputs | False negatives | Fallback to raw text as single finding |
| Levenshtein threshold too strict/loose | Over/under dedup | Tune threshold based on feedback |
| Path traversal fix breaks valid paths | Valid projects rejected | Thorough testing of edge cases |
| Finding model changes require migration | Breaking change | Version the finding model |

## Open Questions

1. **Should we version the finding model?** Yes, add `schema_version` field
2. **How to handle multi-line findings?** Capture as single finding with joined message
3. **Should findings persist in agentmemory?** Future enhancement for learning

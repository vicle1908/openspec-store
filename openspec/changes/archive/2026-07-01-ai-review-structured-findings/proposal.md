# Proposal: ai-review Structured Findings & Quality Improvements

## Why

The current `ai-review` system has significant gaps that reduce its value:

1. **No structured finding extraction** - All findings are published as raw strings with hardcoded `"suggestion"` severity and no file/line context
2. **No finding deduplication** - Multiple reviewers can report the same issue
3. **Validation is underutilized** - Only 2 hardcoded rules exist
4. **CoverageScanner & BenchmarkRunner are orphaned** - Instantiated but never called
5. **Security issues** - Path traversal risk, timing-safe comparison missing

## What Changes

1. **Structured Finding Extraction** - Parse LLM output into structured findings with severity, file, line, message
2. **Finding Deduplication** - Deduplicate findings across reviewers by content similarity
3. **Enhanced ValidationContext** - Add file existence, line bounds, severity consistency checks
4. **CoverageScanner Integration** - Wire coverage scanning into the review flow
5. **Security Fixes** - Path traversal prevention, timing-safe secret comparison

## Capabilities

### New Capabilities

- **Structured Finding Model**: `StructuredFinding` with `severity`, `file`, `line`, `message`, `confidence`
- **Finding Parser**: Extract structured findings from LLM output using regex patterns
- **Finding Deduplicator**: Cluster similar findings across reviewers
- **Enhanced Validator**: Richer validation rules for findings

### Modified Capabilities

- **ReviewOrchestrator**: Uses structured findings instead of raw messages
- **ValidationContext**: Extended validation rules
- **GitLabReviewPoster**: Updated to handle structured findings format
- **Health endpoint**: Include coverage scanner status

## Integration

- **ai-review**: Core changes in `src/ai_review/validation/`, `src/ai_review/review_flow/orchestrator.py`
- **webhook-receiver**: Timing-safe comparison fix
- **OpenSpec**: New spec documenting finding structure

## Non-Goals

- Modifying reviewer CLIs (kimi, claude, codex, pi)
- Changing prompt templates
- Adding new reviewer types

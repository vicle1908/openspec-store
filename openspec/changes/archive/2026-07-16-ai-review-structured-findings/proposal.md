# ai-review Structured Findings

## Why

The ai-review pipeline originally emitted AI findings as free-form text. A structured findings schema was added to enable programmatic consumption, findings deduplication, and consistent output formatting. All 8 implementation phases (data models → parser → validation → deduplication → orchestrator → publication → security → tests → docs) were completed and verified.

## What Changes

- Structured `Finding` dataclass with severity, category, location, and remediation fields
- `FindingParser` to parse LLM text output into structured findings
- `ValidationContext` for enhanced validation
- `FindingDeduplicator` to prevent duplicate findings across scans
- Orchestrator updates to route structured findings through the pipeline
- Publication format changes for structured output
- Security fixes applied
- Full test suite added and passing
- Documentation updated

## Metadata

- **Completed:** 2026-07-14
- **Tasks:** 108 (all done)

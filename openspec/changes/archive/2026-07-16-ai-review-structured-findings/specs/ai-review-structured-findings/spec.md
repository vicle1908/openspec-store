# ai-review Structured Findings

## ADDED Requirements

### Requirement: Structured Finding Schema

The ai-review pipeline SHALL emit findings as structured data with fields for severity, category, location, and remediation text. The structured schema enables programmatic consumption, deduplication, and consistent output formatting.

#### Scenario: Structured finding round-trip

- **WHEN** an LLM emits finding text
- **THEN** the `FindingParser` SHALL parse it into a structured `Finding` with severity, category, location, and remediation fields
- **AND** the `FindingDeduplicator` SHALL prevent duplicate findings from appearing in the final output

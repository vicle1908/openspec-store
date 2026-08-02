# mr-review-orchestration Extraction Truncation Fix Delta

## ADDED Requirements

### Requirement: Orchestrator extraction SHALL preserve all code-scan output lines

`_extract_message` SHALL detect code-scan output by checking whether any of the first two output lines starts with `"Code scan found"` (case-insensitive). When code-scan output is detected, `_extract_message` SHALL return the full joined output without applying the `lines[:6]` limit or the 800-character truncation. For non-code-scan output (LLM reviewers), the existing truncation limits remain unchanged.

#### Scenario: Degraded code-scan output preserves all findings

- **WHEN** a code-scan reviewer produces output starting with `"Code scan degraded: ..."` followed by `"Code scan found N issue(s):"` and N finding lines
- **THEN** `_extract_message` SHALL return all lines including the degradation header and all finding lines
- **AND** the finding parser SHALL extract N findings from the preserved output
- **AND** the aggregate note SHALL show the same finding count as the dedicated note

#### Scenario: Non-degraded code-scan output preserves all findings

- **WHEN** a code-scan reviewer produces output starting with `"Code scan found N issue(s):"` followed by N finding lines
- **THEN** `_extract_message` SHALL return all lines without truncation
- **AND** the aggregate and dedicated notes SHALL show identical finding counts

#### Scenario: LLM reviewer output is still truncated

- **WHEN** an LLM reviewer produces verbose output with more than 6 lines
- **THEN** `_extract_message` SHALL keep only the first 6 lines
- **AND** the result SHALL be truncated to 800 characters if longer

### Requirement: Aggregate and dedicated notes SHALL show identical code-scan finding counts

The aggregate `<!-- mr-auto-review -->` note and the dedicated `<!-- code-scan-review -->` note SHALL report the same number of code-scan findings. The aggregate note SHALL not show fewer findings than the dedicated note due to extraction truncation.

#### Scenario: Multi-finding MR shows matching counts

- **WHEN** a code-scan reviewer produces 17 findings across 12 files
- **THEN** the dedicated note SHALL list all 17 findings
- **AND** the aggregate note SHALL show `"Findings: 17"` and list all 17 findings
- **AND** no findings SHALL be silently dropped between the dedicated and aggregate notes

# Spec Delta: OmniRoute Compression and Routing

## ADDED Requirements

### Requirement: Compression Accounting Provenance
Compression accounting SHALL distinguish estimated token reduction from measured usage and billed cost, record the measurement interval and applicable pricing assumptions, and avoid lifetime-volume or minimum-reduction floors as correctness criteria.

#### Scenario: Compression does not reduce a short input
- **WHEN** an eligible input is already compact or a compressor returns unchanged content
- **THEN** accounting SHALL report zero reduction without inventing savings or treating the request as a correctness failure.

#### Scenario: Reporting estimated monetary savings
- **WHEN** a report converts token reduction into an estimated monetary amount
- **THEN** it SHALL state the model, price basis, measurement window, and limitations and SHALL NOT present the estimate as verified avoided billing.

### Requirement: Optional Compression Quality Gate
Additional compression engines SHALL remain evaluation candidates until representative coding and instruction-following cases demonstrate preserved protected content and acceptable answer, tool-call, and latency outcomes. Existing prose-preserving defaults SHALL remain unchanged during evaluation.

#### Scenario: Protected content and prompt prefixes
- **WHEN** an optional compressor is evaluated on instructions, file contents, tool arguments, identifiers, or cacheable prompt prefixes
- **THEN** the evaluation SHALL check the applicable preservation contract and downstream task correctness, and SHALL NOT accept token reduction alone as sufficient proof.

#### Scenario: Model load or compressor failure
- **WHEN** a model cannot load, execution times out, or compression expands the request
- **THEN** verification SHALL check that the supported fallback preserves the request and reports the failure or bypass without claiming successful compression.

### Requirement: Embedding Timeout Path Evidence
The semantic-cache embedding evaluation SHALL identify the effective deadline at each layer of the embedding request and SHALL distinguish it from chat-header and stream-idle deadlines. Longer timeouts SHALL require measured justification rather than blanket increases.

#### Scenario: Outer setting exceeds inner fetch deadline
- **WHEN** an outer embedding timeout is longer than a separate inner HTTP deadline
- **THEN** the report SHALL identify the limiting deadline and SHALL NOT claim that changing the outer setting alone permits a longer operation.

#### Scenario: Slow or unavailable local embedding service
- **WHEN** an embedding service is cold, slow, or unavailable during evaluation
- **THEN** evidence SHALL record elapsed time, cache-bypass behavior, request outcome, and any uncancelled work; a five-minute chat timeout SHALL NOT substitute for embedding-path verification.

### Requirement: Cache and Coordination Isolation Evaluation
Before changing cache scope or Redis eviction policy, the evaluation SHALL classify enabled cache and coordination consumers and verify request isolation, acceptable expiry behavior, and the effect of memory pressure on rate limits, quotas, and coordination state.

#### Scenario: Similar prompts with different request context
- **WHEN** similar requests differ in authorized owner, relevant system policy, tool contract, tool history, or freshness-sensitive state
- **THEN** evaluation SHALL verify that an incompatible cached response is not reused; an unsafe case SHALL remain ineligible for cache promotion until resolved.

#### Scenario: Shared Redis reaches its proposed memory budget
- **WHEN** a candidate eviction policy is evaluated against a Redis instance shared by cache and coordination consumers
- **THEN** the report SHALL identify which keys can be lost and whether enforcement weakens, and SHALL NOT assume that all expiring keys are disposable cache data or that maxmemory equals total process memory.

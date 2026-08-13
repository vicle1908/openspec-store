## Purpose
Ensures session continuity when an LLM provider becomes unreachable by automatically failing over through a configured sequence of alternative providers.

## Requirements

### Requirement: retry.fallbackChains.default
`retry.fallbackChains.default` SHALL define an ordered cross-provider fallback sequence in `config.yml`. The sequence specifies the providers to attempt in order when the primary provider fails.

#### Scenario: Default fallback chain is defined
- **WHEN** `config.yml` contains `retry.fallbackChains.default`
- **THEN** the chain SHALL be a non-empty ordered list of provider names, and the session SHALL use the first provider as primary and proceed through the list on failure

### Requirement: Automatic provider fallback
WHEN the primary provider in the active chain is unreachable or returns a transient error, the session SHALL automatically retry the request with the next provider in the chain without user intervention.

#### Scenario: Primary provider is down — automatic failover
- **WHEN** the primary provider returns a connection error, timeout, or 5xx status
- **THEN** the session SHALL transparently retry the same request against the next provider in the fallback chain, and the user SHALL see the successful response (or the next failure) without manual intervention

#### Scenario: giaoduc is down — ordered fallback
- **WHEN** `giaoduc` is the primary provider and it is unreachable
- **THEN** the session SHALL attempt `shopapikey` next, then `cockpit`, then `omniroute`, in that order

#### Scenario: All providers in the chain are down
- **WHEN** every provider in the fallback chain has been exhausted (all returned errors or were unreachable)
- **THEN** the session SHALL fail with a clear error message listing which providers were attempted and the nature of each failure, so the user can diagnose the issue

### Requirement: Non-retryable errors
Errors indicating a 4xx status (authentication failure, invalid key, permission denied) SHALL NOT be retried against the next provider in the chain, as these represent configuration issues rather than transient failures.

#### Scenario: Provider returns 4xx auth error
- **WHEN** a provider returns a 4xx status (e.g. 401 Unauthorized, 403 Forbidden)
- **THEN** the session SHALL NOT retry with the next provider and SHALL immediately surface the 4xx error to the user with the provider name and status code

#### Scenario: Provider returns 5xx then next returns 4xx
- **WHEN** the first provider returns a 5xx error and the next provider returns a 4xx error
- **THEN** the chain SHALL stop at the 4xx and report it, without attempting further providers
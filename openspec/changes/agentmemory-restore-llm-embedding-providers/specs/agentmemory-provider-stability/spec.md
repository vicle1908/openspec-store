# Spec Delta

## MODIFIED Requirements

### Requirement: Provider endpoint and model SHALL be consistent

The runtime agentmemory provider configuration SHALL use an LLM endpoint that
honors a leading `system` message, because agentmemory delivers its structured
compression, summarization, and extraction instructions in that role. The
verified endpoint SHALL be `OPENAI_BASE_URL=http://localhost:20128/v1` with an
`auto/*` combo model (currently `auto/best-coding`), and the configuration SHALL
NOT use an endpoint that discards or rewrites the `system` role.

#### Scenario: Validated provider endpoint honors the system role

- WHEN the agentmemory server starts with the configured endpoint and model
- THEN `OPENAI_BASE_URL` SHALL equal `http://localhost:20128/v1`
- AND `OPENAI_MODEL` SHALL be an `auto/*` combo that resolves to a healthy upstream
- AND a POST to `http://localhost:20128/v1/chat/completions` carrying a `system`
  instruction and a `user` observation SHALL return HTTP 200
- AND the assistant content SHALL contain the requested XML envelope contract
  (an `<observation>` element containing both `<type>` and `<title>`)

#### Scenario: System role is not discarded

- WHEN the LLM provider receives a request whose instructions are in the `system`
  role and whose payload is in the `user` role
- THEN the provider SHALL apply the `system` instruction
- AND the response SHALL NOT be conversational prose that omits the requested
  XML envelope
- AND a provider that ignores the `system` role SHALL be treated as incompatible
  and SHALL NOT be selected

#### Scenario: Validated provider endpoint

- WHEN the agentmemory server starts
- THEN `OPENAI_BASE_URL` SHALL equal `http://localhost:20128/v1`
- AND `OPENAI_MODEL` SHALL equal the configured `auto/*` combo (currently `auto/best-coding`)
- AND POST requests to `http://localhost:20128/v1/chat/completions` SHALL return HTTP 200 with a valid response shape when the configured request timeout is 120000 ms

#### Scenario: Invalid model alias rejected

- WHEN `OPENAI_MODEL` is set to a value the provider does not recognize in a disposable validation configuration
- THEN the first LLM call SHALL produce a warning or failed-provider log entry
- AND summarization SHALL degrade gracefully without blocking session completion

#### Scenario: Unavailable specific model alias rejected

- WHEN `OPENAI_MODEL` names a specific model whose upstream provider is not
  currently connected
- THEN the LLM call SHALL return an error identifying an unresolvable provider
- AND the configuration SHALL prefer an `auto/*` combo that routes to a healthy
  upstream rather than a specific model pinned to an unavailable provider
- AND summarization and compression SHALL degrade gracefully without blocking
  session completion

### Requirement: LLM request timeouts SHALL be bounded

Provider request timeouts SHALL be set to 120000 ms, and no supported runtime
configuration SHALL exceed 120000 ms.

#### Scenario: Provider timeout within acceptable bound

- WHEN the agentmemory server makes an LLM request for summarization, compression,
  or consolidation against a slow-but-healthy upstream
- THEN the configured request deadline SHALL be 120000 ms
- AND the configured timeout SHALL NOT exceed 120000 ms under any supported configuration
- AND the operation SHALL return control to the caller when that deadline expires,
  subject to transport cleanup overhead

#### Scenario: Engine invocation timeout bounded

- WHEN the iii engine processes an LLM-backed invocation
- THEN the invocation SHALL complete or timeout within the `iii-config` `default_timeout` value of 75000 ms
- AND the agentmemory server SHALL NOT hold engine resources beyond that bound

#### Scenario: Slow upstream completes within the raised bound

- WHEN an LLM-backed request takes longer than 60000 ms but less than the
  configured 120000 ms bound
- THEN the request SHALL complete successfully rather than timing out
- AND the successful result SHALL be recorded with a compression quality score
  and `retried: false` when no retry was required

### Requirement: Provider configuration SHALL be documented in runtime config

The provider settings SHALL be maintained in `~/.agentmemory/.env` with backup
files preserved for rollback, while runtime files and secrets remain outside the
OpenSpec store. The same runtime config SHALL document the embedding backend that
agentmemory depends on.

#### Scenario: Config backed up before change

- WHEN an operator modifies the agentmemory provider configuration
- THEN a timestamped backup copy of the prior configuration SHALL exist beside
  `~/.agentmemory/.env`
- AND the backup SHALL reflect the prior working configuration for rollback

#### Scenario: Session-end probe uses the hook contract

- WHEN an operator probes session completion
- THEN the request body SHALL contain only a synthetic `sessionId`
- AND the probe SHALL not include transcript contents, credentials, or real user/session identifiers
- AND the probe SHALL use a client timeout of 30000 ms or less
- AND a fire-and-forget hook implementation SHALL still be evaluated by inspecting the HTTP response and fresh server logs

#### Scenario: Config restart applies cleanly

- WHEN the agentmemory server is restarted after a configuration change
- THEN the server SHALL start within 10 seconds
- AND the configured model and endpoint SHALL match the running configuration
- AND capability verification SHALL observe real success signals (a non-zero
  LLM compression success count and zero embedding-skip events) rather than
  relying on configured-flag presence alone

## ADDED Requirements

### Requirement: LLM compression and summarization SHALL produce parseable structured output

Because agentmemory parses a fixed XML envelope from LLM replies, the selected
provider MUST return content that satisfies that contract, and failures MUST be
observable rather than silent.

#### Scenario: Compression emits the required XML envelope

- WHEN an observation is compressed by the LLM
- THEN the reply SHALL contain a `<type>` element and a `<title>` element inside
  an `<observation>` element
- AND the compression SHALL be recorded as successful with a quality score
- AND no `Failed to parse compression XML` entry SHALL be emitted for that
  observation

#### Scenario: Silent capability failure is not reported as healthy

- WHEN the configured LLM cannot satisfy the structured-output contract
- THEN repeated compression failures SHALL be observable in server logs and
  function metrics
- AND a capability SHALL NOT be reported as available solely because its provider
  is configured

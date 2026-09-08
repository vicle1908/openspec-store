# agentmemory-provider-stability Specification

## Purpose
Runtime provider settings and timeout behavior that protect summarization and consolidation under unstable LLM conditions.

## Requirements

### Requirement: Provider endpoint and model SHALL be consistent

The runtime agentmemory provider configuration SHALL use `OPENAI_BASE_URL=https://api.phanmemvip.shop/v1` and `OPENAI_MODEL=fable-5`, matching the verified shopapikey endpoint.

#### Scenario: Validated provider endpoint

- WHEN the agentmemory server starts
- THEN `OPENAI_BASE_URL` SHALL equal `https://api.phanmemvip.shop/v1`
- AND `OPENAI_MODEL` SHALL equal `fable-5`
- AND POST requests to `https://api.phanmemvip.shop/v1/chat/completions` SHALL return HTTP 200 with a valid response shape when the configured request timeout is 60000 ms

#### Scenario: Invalid model alias rejected

- WHEN `OPENAI_MODEL` is set to a value the provider does not recognize in a disposable validation configuration
- THEN the first LLM call SHALL produce a warning or failed-provider log entry
- AND summarization SHALL degrade gracefully without blocking session completion

### Requirement: LLM request timeouts SHALL be bounded

Provider request timeouts SHALL be set to 60000 ms, and no supported runtime configuration SHALL exceed 120000 ms.

#### Scenario: Provider timeout within acceptable bound

- WHEN the agentmemory server makes an LLM request for summarization or consolidation
- THEN the configured request deadline SHALL be 60000 ms
- AND the configured timeout SHALL NOT exceed 120000 ms under any supported configuration
- AND the operation SHALL return control to the caller when that deadline expires, subject to transport cleanup overhead

#### Scenario: Engine invocation timeout bounded

- WHEN the iii engine processes an LLM-backed invocation
- THEN the invocation SHALL complete or timeout within the `iii-config` `default_timeout` value of 75000 ms
- AND the agentmemory server SHALL NOT hold engine resources beyond that bound

### Requirement: LLM failure SHALL NOT block session completion

Summarization and consolidation failures due to provider instability MUST NOT prevent session observation capture or session-end processing from completing.

#### Scenario: Provider 502 during summarization

- WHEN the LLM provider returns a 502 error during session summarization
- THEN the session-end endpoint SHALL return HTTP 200 with `success=true`
- AND the summarization attempt SHALL be recorded as failed in server logs
- AND subsequent session-end requests SHALL proceed normally

#### Scenario: Provider timeout during consolidation

- WHEN the LLM provider exceeds the configured timeout during semantic consolidation
- THEN the consolidation pipeline SHALL log the timeout as an error
- AND the session-end endpoint SHALL not be blocked by the pending consolidation

### Requirement: Provider configuration SHALL be documented in runtime config

The provider settings SHALL be maintained in `~/.agentmemory/.env` with backup files preserved for rollback, while runtime files and secrets remain outside the OpenSpec store.

#### Scenario: Config backed up before change

- WHEN an operator modifies the agentmemory provider configuration
- THEN a backup copy SHALL exist at `~/.agentmemory/.env.bak`
- AND the backup SHALL reflect the prior working configuration

#### Scenario: Config restart applies cleanly

- WHEN the agentmemory server is restarted after a configuration change
- THEN the server SHALL start within 10 seconds
- AND `POST /agentmemory/session/end` with `{"sessionId":"openspec-probe-<timestamp>"}` and `Content-Type: application/json` SHALL respond with HTTP 200 and `success=true`
- AND the request SHALL include `Authorization: Bearer <AGENTMEMORY_SECRET>` only when `AGENTMEMORY_SECRET` is configured
- AND the configured model and endpoint SHALL match the running configuration

#### Scenario: Session-end probe uses the hook contract

- WHEN an operator probes session completion
- THEN the request body SHALL contain only a synthetic `sessionId`
- AND the probe SHALL not include transcript contents, credentials, or real user/session identifiers
- AND the probe SHALL use a client timeout of 30000 ms or less
- AND a fire-and-forget hook implementation SHALL still be evaluated by inspecting the HTTP response and fresh server logs

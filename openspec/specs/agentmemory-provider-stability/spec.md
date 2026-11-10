# agentmemory-provider-stability Specification

## Purpose
Runtime provider settings and timeout behavior that protect summarization and consolidation under unstable LLM conditions.

## Requirements

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
- THEN the server SHALL start within 45 seconds under operational state store volume
- AND the configured model and endpoint SHALL match the running configuration
- AND capability verification SHALL observe real success signals (a non-zero
  LLM compression success count and zero embedding-skip events) rather than
  relying on configured-flag presence alone

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

### Requirement: Healthcheck watchdog SHALL authenticate when server secret exists

The agentmemory launchd watchdog healthcheck script (`~/.hermes/scripts/agentmemory-healthcheck.sh`) SHALL authenticate against `/agentmemory/health` using the local bearer token from `~/.agentmemory/secret` when present, preventing spurious 401 restarts during normal operations.

#### Scenario: Watchdog authenticates with local bearer secret

- **WHEN** the agentmemory server runs with secret-based authentication enabled and `~/.agentmemory/secret` exists
- **THEN** `agentmemory-healthcheck.sh` SHALL supply `Authorization: Bearer <token>` on all `/agentmemory/health` calls
- **AND** the probe SHALL evaluate to HTTP 200 with status `healthy` rather than triggering unneeded `launchctl kickstart` restarts.

#### Scenario: Watchdog succeeds when secret file is absent

- **WHEN** `~/.agentmemory/secret` does not exist or server authentication is disabled
- **THEN** `agentmemory-healthcheck.sh` SHALL send an unauthenticated probe without error.

### Requirement: Managed AgentMemory LaunchAgent PATH and mesh patch parity across peers

Managed AgentMemory launchd service plists across peer workstations SHALL include `/usr/sbin:/sbin` in `PATH` and omit `AGENTMEMORY_URL` to prevent `readMacProcessExecutable()` process-identity crash loops. When upgrading pinned engine versions, running daemons SHALL be stopped before service restarts, and mesh routing fixes (#1, #2, #3) SHALL be kept in parity across all cluster peers.

#### Scenario: LaunchAgent PATH includes /usr/sbin and omits AGENTMEMORY_URL
- **WHEN** `com.agentmemory.server.plist` on `iosteam-mac-mini` or `local.shb.agentmemory.worker.plist` on `macbook-pro-m5` is loaded by launchd
- **THEN** `EnvironmentVariables.PATH` SHALL contain `/usr/sbin:/sbin` so `readMacProcessExecutable()` resolves `/usr/sbin/lsof` without `ENOENT`
- **AND** `EnvironmentVariables` SHALL omit `AGENTMEMORY_URL` so worker daemons do not crash-loop on self-directed HTTP loopback probes.

#### Scenario: AgentMemory engine pin upgrade stops running daemon before kickstart
- **WHEN** an npm global upgrade of `@agentmemory/agentmemory` bumps `IIPINNED_VERSION` (such as `0.25.0` to `0.25.1`)
- **THEN** workstation update runners SHALL invoke `agentmemory stop` or terminate existing `iii compose` daemon processes before kickstarting launchd services
- **AND** the newly pinned engine binary SHALL start cleanly without port binding collisions or stale process identity locks.

#### Scenario: Mesh routing patches 1, 2, and 3 are maintained in parity across peers
- **WHEN** `@agentmemory/agentmemory@0.9.33` executes mesh replication or peer management across `iosteam-mac-mini` and `macbook-pro-m5`
- **THEN** `dist/index.mjs` on both nodes SHALL enforce Mesh Fix #1 (`syncStartedAt`), Mesh Fix #2 (IPv6 bracket stripping in `isAllowedUrl`), and Mesh Fix #3 (`pinGraphState` in `mem::mesh-remove` and `DELETE /agentmemory/mesh/peers/:id`)
- **AND** bidirectional mesh synchronization over Tailscale L4 port `3111` SHALL operate without unhandled promise rejections or peer removal exceptions.

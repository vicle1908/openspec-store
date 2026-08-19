## Purpose

Defines intentional shared-state governance for one default Hermes profile used by local CLI/Desktop and the authorized Telegram gateway, without adding an unnecessary profile or gateway.

## ADDED Requirements

### Requirement: One default profile SHALL serve all current surfaces

The installation SHALL retain `default` as the sole active profile for CLI, Desktop, Telegram, memory, skills, sessions, cron, credentials, MCP, logs, and backups. The change SHALL NOT create, clone, activate, or install a gateway for a named Telegram profile.

#### Scenario: Profile inventory is inspected
- **WHEN** an operator inspects active profiles
- **THEN** `default` is the sole required profile and no named Telegram profile is required for the current one-user, one-bot, common-policy topology

#### Scenario: Local interface starts
- **WHEN** CLI or Desktop starts a local agent session
- **THEN** it uses `default` directly and does not require the messaging gateway as an intermediary

### Requirement: Shared profile state SHALL be intentional and observable

CLI, Desktop, and Telegram SHALL intentionally share the default profile's configuration, provider credentials, SOUL, memory, skills, cron, MCP configuration, and state database. Active conversations SHALL remain distinguishable through CLI session identities and Telegram platform/chat/topic session keys.

#### Scenario: Knowledge is learned on one surface
- **WHEN** an authorized session writes default-profile memory or skills
- **THEN** the supported shared state is available to future sessions on other default-profile surfaces

#### Scenario: Session inventory is inspected
- **WHEN** CLI and Telegram have both created sessions
- **THEN** their records remain attributable by source and Telegram chat/topic routing rather than being treated as one active conversation

#### Scenario: Shared-state risk is reviewed
- **WHEN** an operator evaluates failure blast radius
- **THEN** configuration, credential, memory, skill, cron, MCP, and state-database sharing is recorded as an accepted trade-off and not misrepresented as isolation

### Requirement: Authorized surfaces SHALL expose full available capability

The default profile SHALL expose every installed and platform-applicable configurable built-in toolset, the persisted Kanban exception, every runtime-available plugin/toolset, and every advertised operation from enabled MCP servers to authorized CLI/Desktop and Telegram sessions. GUI-only Project tools, config-only STT, and active-context-engine tools SHALL be verified only through supported surfaces. Missing credentials, binaries, providers, plugins, or platform features SHALL be reported as unavailable prerequisites rather than policy denials.

#### Scenario: Full built-in inventory is enabled
- **WHEN** an operator inspects CLI or Telegram tool inventory
- **THEN** every configurable platform-applicable target is enabled and each special capability is verified or has an exact unavailable reason

#### Scenario: Kanban exception is persisted
- **WHEN** an operator inspects stored CLI or Telegram platform toolsets
- **THEN** all configurable targets plus `kanban` are present and applicable Kanban schemas register in a fresh ordinary session

#### Scenario: MCP mutation capability is advertised
- **WHEN** an enabled MCP server advertises mutating or administrative operations
- **THEN** those operations are registered without a profile-level operation filter

### Requirement: The default working directory SHALL be deterministic

The default profile SHALL use an explicitly verified working directory that is valid for local and Telegram operations and SHALL NOT use the multi-repository TDT aggregator root for Git operations.

#### Scenario: Agent starts from its declared directory
- **WHEN** CLI or the gateway reports its terminal working directory
- **THEN** it matches `/Users/androidteam/Developer`, and each coding task enters a verified target repository before Git operations

#### Scenario: Declared directory is invalid
- **WHEN** the configured directory is missing or violates repository policy
- **THEN** activation fails with an actionable diagnostic and does not silently choose another directory

### Requirement: One existing gateway SHALL retain Telegram ownership

The existing default-profile `ai.hermes.gateway` launchd service SHALL remain the sole Telegram adapter, cron ticker, and Telegram-token owner. The change SHALL restart that service in place after validation and SHALL NOT install a second service, enable profile multiplexing, or transfer the bot token.

#### Scenario: Gateway activation occurs
- **WHEN** validated default-profile changes require gateway activation
- **THEN** the existing service is restarted in place and the same label, default profile home, sole token ownership, supervised PID, platform health, and authorized round-trip are verified

#### Scenario: Gateway activation fails
- **WHEN** the restarted default gateway fails its health or Telegram round-trip checks
- **THEN** prior default-profile state is restored as needed and the same service is restarted without creating another profile or gateway

#### Scenario: Local CLI runs during gateway downtime
- **WHEN** the Telegram gateway is stopped or restarting
- **THEN** an independent local CLI/Desktop process may still use the default profile, while Telegram and gateway-owned cron ticking are reported unavailable

### Requirement: Telegram authorization SHALL remain explicit

The Telegram gateway SHALL retain explicit allowed-user authorization. Full technical capability SHALL NOT imply public access or admission of unknown users.

#### Scenario: Authorized user is admitted
- **WHEN** a request comes from a configured Telegram user
- **THEN** it reaches the default-profile gateway session policy

#### Scenario: Unknown user is rejected
- **WHEN** a request comes from outside the authorization policy
- **THEN** it is denied or routed through supported pairing without exposing tools

### Requirement: Additional profiles SHALL remain a future isolation option

A named profile MAY be introduced by a separate reviewed change only when identity, model/provider policy, credentials, memory, skills, cron, users, or bot tokens must diverge. A profile SHALL NOT be claimed as a host filesystem sandbox while using the local backend and real OS-user home.

#### Scenario: Future isolation need arises
- **WHEN** Telegram requires distinct identity, credentials, knowledge, automation, users, or bot ownership
- **THEN** a separate profile/gateway or supported multiplexer is evaluated in a new change with explicit migration and rollback

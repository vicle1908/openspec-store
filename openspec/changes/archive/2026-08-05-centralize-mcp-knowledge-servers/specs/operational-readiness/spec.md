## MODIFIED Requirements

### Requirement: Agent configs SHALL be wired for all supported agents

The platform SHALL provide properly configured agent configuration files for all supported AI coding agents (Claude via `.claude/settings.json`, Cursor via `.cursor/mcp.json`, Codex, KiloCode, Kiro, Factory, OpenCode, Zed, Kimi, Antigravity, and Hermes where installed). Each supported MCP client SHALL use MCP Router as the single client-facing gateway for GitNexus, Graphify, and AgentMemory. Client configuration MUST NOT additionally register those same knowledge servers directly unless a documented, time-bounded compatibility exception identifies the owner, reason, expiry, and rollback. Configurations MUST remain synchronized with the platform topology and MUST NOT contain hardcoded secrets or credentials.

The running MCP Router desktop app SHALL be the authoritative adapter and live
configuration owner. The app SHALL remain on latest stable `0.6.3` until a newer
stable release is reviewed, and stdio coding-agent bridges SHALL pin latest
stable `@mcp_router/cli@0.2.0`. Provider child definitions and token-access maps
MUST be previewed, applied, and restored through MCP Router's repository/service
layer; automation MUST NOT write the app SQLite database or shared token config
directly. Each supported coding-agent token SHALL receive only the reviewed
knowledge-child access needed by that client, while unrelated server access is
preserved exactly.

Repository-owned client transactions MAY inspect router SQLite/shared-config
shape for read-only evidence, but production apply and restore MUST return a
typed app-owned refusal for those targets and MUST NOT open a write connection,
issue SQL, or replace either file.

The transaction SHALL mutate only access booleans for existing approved tokens;
it MUST NOT create, rotate, delete, export, log, journal, or back up raw token
values. It SHALL address tokens by approved client alias and app-computed
one-way fingerprint, preserve unrelated true/false/absent access entries, and
reject unknown servers plus missing, duplicate, ambiguous, or expired tokens.
Rollback SHALL retain only access-map booleans, aliases, and one-way token
fingerprints. Raw token values MUST remain in place; fingerprint drift from
rotation/deletion/creation MUST block automated restore.

The app command channel MUST accept only canonical current-owner mode-0600
regular plan/result/approval paths and digest-bound generations. Preview MAY run
without approval; apply and restore MUST reject absent, stale, mismatched, or
replayed approval and MUST serialize execution under one app-owned lock. The
channel MUST NOT introduce a network admin endpoint or token-bearing arguments.
Apply/restore authorization MUST use an app-minted single-use challenge shown in
the trusted MCP Router BrowserWindow and a short-lived MACed capability issued
only after validated renderer-origin/webContents confirmation. The MAC key MUST
remain under `safeStorage`; expiry, consumption, replay, and restart recovery
MUST fail closed. External chat approval alone MUST NOT authenticate the app
command.

Before mutation the app MUST preflight every target and atomically publish a
redacted durable recovery journal. It MUST revalidate identities before every
publication/compensation step, quiesce affected running children, reject
concurrent server/token/workspace writers, define one commit point, compensate
in reverse order, verify compensation, refresh app caches/name maps, and restart
only children that were previously running. Secret-bearing backup payloads MUST
be encrypted with `safeStorage`; unavailable encryption blocks apply/restore.

#### Scenario: MCP Router app configuration is previewed

- **WHEN** the operator supplies a declarative coding-agent adapter plan
- **THEN** MCP Router validates app/database/shared-config identities, exact
  server definitions, pinned bridge/provider selectors, client aliases, and
  token-access deltas without mutation
- **AND** missing, duplicate, floating, secret-bearing, or third-state inputs
  fail closed with redacted evidence

#### Scenario: MCP Router app configuration is applied

- **WHEN** an approved plan is applied to the running app
- **THEN** server and token mutations execute through the app-owned services,
  preserve secret storage and unrelated rows/access, and publish exact post-state
- **AND** a later failure compensates prior changes or restores the protected
  app-owned backup before reporting failure

#### Scenario: MCP Router app configuration is restored

- **WHEN** acceptance fails and current state matches the approved post-state
- **THEN** the app-owned restore returns server definitions and token access to
  the exact approved pre-state without exposing token values

#### Scenario: Claude settings reference correct MCP servers

- **WHEN** a developer opens the project with Claude Code
- **THEN** Claude's effective MCP configuration points to the authorized MCP Router endpoint or bridge
- **AND** no duplicate direct GitNexus, Graphify, or AgentMemory MCP registration is active outside an approved compatibility exception

#### Scenario: Cursor MCP config includes all required tools

- **WHEN** a developer opens the project with Cursor
- **THEN** Cursor reaches all required platform-development tools through the authorized MCP Router connection
- **AND** the effective configuration contains no duplicate direct GitNexus, Graphify, or AgentMemory server

#### Scenario: Effective client topology is audited

- **WHEN** the operator runs the MCP topology diagnostic
- **THEN** it inventories every supported client configuration, MCP Router server, bridge process, and direct GitNexus, Graphify, and AgentMemory process family
- **AND** it distinguishes the expected one bridge per active client from duplicate child knowledge-server processes
- **AND** it emits only redacted paths, server names, process identities, counts, and health states

#### Scenario: Duplicate direct knowledge server is detected

- **WHEN** a supported client config or process tree contains a direct GitNexus, Graphify, or AgentMemory MCP server in addition to MCP Router
- **THEN** readiness fails and identifies the owning client and duplicate server class without printing credentials or command-line secret values
- **AND** no automatic deletion or process termination occurs during diagnosis

#### Scenario: Live client cutover is authorized

- **WHEN** reviewed source changes, backups, synthetic migration, restore rehearsal, and an exact redacted cutover plan have passed
- **THEN** an operator may issue execution approval bound to the plan digest, client inventory, configuration fingerprints, process owners, and maintenance window
- **AND** stale or changed inputs invalidate that approval before mutation

#### Scenario: Client cutover succeeds

- **WHEN** the approved live cutover removes duplicate direct registrations and restarts affected clients
- **THEN** each required client discovers GitNexus, Graphify, and AgentMemory through MCP Router
- **AND** no duplicate child knowledge-server process family remains after old client sessions exit
- **AND** client hooks, skills, unrelated MCP servers, credentials, sessions, and local indexes remain intact

#### Scenario: Client cutover fails

- **WHEN** any required client cannot discover or call its required router-exposed knowledge tools after cutover
- **THEN** maintenance remains active and the operator restores the exact backed-up client configuration for the affected scope
- **AND** the run records the failure and rollback outcome without exposing secrets

# omniroute-agent-skills Specification Delta

## ADDED Requirements

### Requirement: Host CLI Bridge Loopback IPv4 Normalization and Ephemeral Cleanup

The host CLI bridge at `~/.local/bin/omniroute` SHALL normalize `localhost` base URLs to `127.0.0.1` to avoid macOS IPv6 dual-stack resolution delays and MUST allocate and remove a unique per-invocation temporary `DATA_DIR` (`fs.mkdtempSync` and `fs.rmSync`) on process exit.

#### Scenario: Localhost base URL is normalized to IPv4 loopback
- **WHEN** `OMNIROUTE_BASE_URL` or `OMNIROUTE_URL` is set to `http://localhost:20128` or `http://localhost:20128/v1`
- **THEN** the bridge SHALL normalize both `OMNIROUTE_BASE_URL` and `OMNIROUTE_URL` to `http://127.0.0.1:20128`

#### Scenario: Per-invocation ephemeral DATA_DIR is removed upon completion
- **WHEN** `~/.local/bin/omniroute` finishes executing any CLI subcommand
- **THEN** the unique temporary directory created via `fs.mkdtempSync` for that invocation SHALL be removed before exit
- **AND** consecutive offline fallback runs SHALL NOT share residual SQLite or `.env` state in `/tmp`

## MODIFIED Requirements

### Requirement: Ecosystem Knowledge Hub and Documentation Synchronization

The repository workspace SHALL maintain an operational reference guide in `docs/omniroute-agent-skills.md` and keep `wiki/entities/omniroute.md` synchronized with the active skills catalog, management authorization model, curl REST invocation patterns, and `omniroute` CLI bridge subcommand recipes.

#### Scenario: Operational guide provides actionable agent recipes
- **WHEN** an agent consults `docs/omniroute-agent-skills.md`
- **THEN** the document details all 22 `omni-*` REST endpoints, expected authentication headers, and copy-paste curl commands
- **AND** the document includes a complete CLI command reference covering the 21 `cli-*` skills executed via `~/.local/bin/omniroute`

#### Scenario: Wiki entity reflects active host CLI bridge governance
- **WHEN** `wiki/entities/omniroute.md` is inspected
- **THEN** it SHALL describe the 21 `cli-*` skills as actively served through `~/.local/bin/omniroute` (`2026-10-15-introduce-omniroute-cli-bridge`) rather than deferred to a future change

### Requirement: Host Database Isolation and Dependency Resolution

The bridge SHALL pin `DATA_DIR` to an ephemeral directory for each invocation so that an unreachable server cannot cause the CLI to read or mutate the stale host-side `~/.omniroute/storage.sqlite`. The bridge SHALL rely on Bun automatic dependency resolution and MUST NOT pass `--no-install`.

#### Scenario: Cold Bun cache requires registry egress
- **WHEN** the bridge runs and Bun's global cache lacks a required dependency
- **THEN** Bun performs a one-time registry fetch before the command executes
- **AND** subsequent invocations resolve from cache without network access

#### Scenario: Unreachable server cannot yield stale orphan data
- **WHEN** the OmniRoute server is unreachable
- **AND** the bridge pins `DATA_DIR` to an ephemeral directory for that invocation
- **THEN** no command reads or mutates `~/.omniroute/storage.sqlite`
- **AND** any local-database fallback resolves against the empty ephemeral directory
- **AND** the command returns an empty result set or an error, never archived orphan records

#### Scenario: Container unreachable fails closed without touching host SQLite
- **WHEN** the `omniroute` container is stopped or port `20128` is unreachable
- **THEN** running `omniroute providers list` or `omniroute keys list --output json` SHALL NOT open or modify `~/.omniroute/storage.sqlite`
- **AND** the file modification timestamp and SHA-256 digest of `~/.omniroute/storage.sqlite` SHALL remain unchanged

#### Scenario: Orphan leakage is demonstrably blocked by the DATA_DIR pin
- **WHEN** `keys list --output json` runs against an unreachable server with the default `DATA_DIR`
- **THEN** it returns records read from the stale orphan database instead of failing
- **AND** with `DATA_DIR` pinned to an empty directory the same command returns `{"keys":[]}`
- **AND** the orphan file's mtime is unchanged by the pinned invocation

#### Scenario: Server-dependent commands surface an error
- **WHEN** a command that requires the HTTP server cannot reach it
- **THEN** it exits non-zero with an error instead of reporting a successful empty dataset
- **NOTE** Verified for `cost` and `health` on this build; not every command sets the `requireServer` flag, which is why the `DATA_DIR` pin is the load-bearing mitigation.

#### Scenario: Database-branch diagnostics stay off standard output
- **WHEN** a command falls through to the local database branch
- **THEN** `[DB]` diagnostic lines are written to standard error
- **AND** standard output carries only the requested table, JSON, JSONL, or CSV payload

# OmniRoute Agent Skills

## Purpose

Define the capability, permission model, and environment contracts for adopting OmniRoute official agent skills across multi-agent coding harnesses on the local workstation.

## Requirements

### Requirement: Canonical Skill Manifest Installation and Discovery

The workstation environment SHALL maintain OmniRoute official skills installed from the local OmniRoute repository (`/Users/androidteam/Omniroute`) into the global agent skills directory (`~/.agents/skills/`), with symlinks to all configured agent discovery surfaces. Every installed skill manifest MUST conform to the standard Agent Skills schema (`SKILL.md` frontmatter with `name` and `description`).

#### Scenario: Full skill catalog is installed globally
- **WHEN** `npx skills add /Users/androidteam/Omniroute -g --all` is executed on the workstation
- **THEN** all 45 official OmniRoute skills are materialized in `~/.agents/skills/` without error
- **AND** the manifests are accessible to Claude Code, Antigravity, Cursor, and Codex agent runtimes

#### Scenario: Local repository updates propagate automatically
- **WHEN** upstream changes are pulled into `/Users/androidteam/Omniroute`
- **THEN** symlinked skill manifests in `~/.agents/skills/` reflect the latest contents immediately without requiring manual re-installation

### Requirement: Management Authorization and Scope Enforcement

The OmniRoute storage service SHALL authorize agent management requests by ensuring the agent's active API key is granted `manage` and `admin` scopes in the SQLite `api_keys` table. Management endpoints under `/api/*` MUST accept requests authenticated with this key and reject unauthenticated or unprivileged requests with standard error payloads. Scope updates SHALL take effect within the bounded 60-second in-memory key cache TTL.

#### Scenario: Agent requests management endpoint with elevated key
- **WHEN** an AI agent sends an HTTP request to `http://127.0.0.1:20128/api/monitoring/health` or `/api/models` with `Authorization: Bearer <OMNIROUTE_KEY>`
- **AND** the key possesses the `manage` scope
- **THEN** OmniRoute returns an HTTP 200 response with valid JSON payload

#### Scenario: Unauthenticated or insufficient-scope request is rejected
- **WHEN** a client sends an HTTP request to `/api/providers` without an Authorization header or with an API key lacking `manage` scope
- **THEN** OmniRoute returns an HTTP 401 or HTTP 403 error response indicating invalid management token

### Requirement: Standardized Shell Environment Contracts

The workstation user environment SHALL export canonical environment variables for OmniRoute REST access in `~/.zshenv`. `OMNIROUTE_URL` and `OMNIROUTE_BASE_URL` MUST be exported as `http://localhost:20128` without a trailing `/v1` suffix, and `OMNIROUTE_KEY` MUST be exported mirroring `$OMNIROUTE_API_KEY`. These exports MUST reside outside the protected `standardize-zshenv-shared-secrets` block.

#### Scenario: Interactive and non-interactive subshells load credentials
- **WHEN** an agent initiates a subshell or executes an inline command
- **THEN** `OMNIROUTE_URL`, `OMNIROUTE_BASE_URL`, and `OMNIROUTE_KEY` are present and non-empty in the subshell environment

#### Scenario: Base URL path normalization prevents double-v1 404s
- **WHEN** an agent skill appends `/api/monitoring/health` or `/v1/models` to `$OMNIROUTE_URL` or `$OMNIROUTE_BASE_URL`
- **THEN** the request targets the intended server endpoint without generating malformed `/v1/api/...` paths

#### Scenario: Shared secrets invariant is preserved
- **WHEN** `~/.zshenv` is updated with OmniRoute environment variables
- **THEN** lines 15–33 between `# BEGIN shared-agent-secrets` and `# END shared-agent-secrets` remain byte-identical

#### Scenario: Interactive shell startup order preserves normalized base URL
- **WHEN** an interactive zsh shell is spawned
- **THEN** `OMNIROUTE_BASE_URL` in `~/.zshrc` resolves to `http://localhost:20128` without `/v1`
- **AND** `COPILOT_PROVIDER_BASE_URL` on line 223 remains configured with `/v1` for Copilot

### Requirement: Ecosystem Knowledge Hub and Documentation Synchronization

The repository workspace SHALL maintain an operational reference guide in `docs/omniroute-agent-skills.md` and keep `wiki/entities/omniroute.md` synchronized with the active skills catalog, management authorization model, and curl invocation patterns.

#### Scenario: Operational guide provides actionable agent recipes
- **WHEN** an agent consults `docs/omniroute-agent-skills.md`
- **THEN** the document details all 22 `omni-*` REST endpoints, expected authentication headers, and copy-paste curl commands

### Requirement: Host CLI Bridge Execution and Stdout Stream Cleanliness

The system SHALL provide an executable host CLI bridge at `~/.local/bin/omniroute` that invokes the OmniRoute CLI entrypoint via the host Bun runtime. The bridge MUST normalize `OMNIROUTE_BASE_URL` to strip a trailing `/v1`, and MUST filter startup banner lines matching `📋 Loaded env from` from standard output so structured output remains parseable.

#### Scenario: Subcommand outputs pure parseable JSON
- **WHEN** a client runs `omniroute keys list --output json | jq '.keys | length'`
- **THEN** standard output contains valid JSON without startup banner noise
- **AND** `jq` extracts the count with exit code 0
- **NOTE** `omniroute health --json` is not a valid example: it emits no JSON payload on this build.

#### Scenario: Base URL trailing v1 is stripped automatically
- **WHEN** `OMNIROUTE_BASE_URL` is set to `http://localhost:20128/v1`
- **THEN** the bridge normalizes the URL to `http://localhost:20128`
- **AND** management commands execute without producing double-path 404 errors

### Requirement: Credential Resolution for the CLI Bridge

The bridge SHALL pass through `OMNIROUTE_API_KEY` or `OMNIROUTE_KEY` when already exported by the calling shell. When neither is set, it MUST fall back to the read-only helper `~/.claude/helpers/omniroute-key.sh`, which parses the value from `~/.zshenv` without sourcing or mutating it.

#### Scenario: Exported key short-circuits the helper
- **WHEN** either variable is already present in the process environment
- **THEN** the bridge forwards the existing value
- **AND** the helper is not spawned

#### Scenario: Missing key falls back to the read-only helper
- **WHEN** neither variable is exported
- **THEN** the bridge invokes the helper once and exports the returned value
- **AND** no file under `$HOME` is modified by the helper or the bridge

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

### Requirement: Interactive Zsh Function Subcommand Multiplexing

The workstation interactive shell environment in `~/.zshrc` SHALL multiplex the `omniroute()` shell function: when invoked with known CLI subcommands or informational flags (`health`, `models`, `providers`, `combo`, `combos`, `keys`, `resilience`, `doctor`, `serve`, `chat`, `repl`, `status`, `--help`, `-h`, `--version`, `-v`), it SHALL dispatch to `command omniroute "$@"`. When invoked without subcommands, it SHALL preserve the existing Claude Code launcher under the `omniroute-pm.json` profile.

#### Scenario: CLI subcommand dispatches to host binary
- **WHEN** a user enters `omniroute health` in an interactive zsh terminal
- **THEN** the shell dispatches to `command omniroute health`
- **AND** server health output is displayed in the terminal

#### Scenario: Bare invocation preserves Claude Code launcher
- **WHEN** a user enters `omniroute` or `omniroute -p "prompt"` in an interactive zsh terminal
- **THEN** Claude Code launches with profile `omniroute-pm.json` and model `gemini-3.8-flash-high`

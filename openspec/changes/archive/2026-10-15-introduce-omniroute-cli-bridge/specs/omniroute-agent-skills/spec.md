# Spec Delta

## REMOVED Requirements

### Requirement: Boundary Isolation for CLI Wrapper Deferral

The system MUST enforce that host CLI wrapper installation (`~/.local/bin/omniroute`) and `cli-*` command execution are treated as a separate change scope. Agents adopting `omni-*` REST skills SHALL interact with OmniRoute strictly via HTTP/REST endpoints rather than relying on unverified host binary execution.

## ADDED Requirements

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

#### Scenario: Container unreachable fails closed without touching host SQLite
- **WHEN** the Docker container is not answering on `http://127.0.0.1:20128`
- **THEN** the bridge pins `DATA_DIR` to an ephemeral directory for that invocation
- **AND** no command opens or mutates `~/.omniroute/storage.sqlite`
- **AND** commands requiring the server exit with code 3 and a clear offline error

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

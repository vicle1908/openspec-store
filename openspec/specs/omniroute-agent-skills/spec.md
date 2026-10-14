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

### Requirement: Boundary Isolation for CLI Wrapper Deferral

The system MUST enforce that host CLI wrapper installation (`~/.local/bin/omniroute`) and `cli-*` command execution are treated as a separate change scope. Agents adopting `omni-*` REST skills SHALL interact with OmniRoute strictly via HTTP/REST endpoints rather than relying on unverified host binary execution.

#### Scenario: REST-based skill invocation succeeds independently
- **WHEN** an agent executes an `omni-*` skill action using curl or HTTP client
- **THEN** the action executes to completion successfully without checking for or requiring a host `omniroute` binary

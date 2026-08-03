# codex-workspace-orchestration Specification

## Purpose
Provide a deterministic Codex orchestration contract for one workspace containing independent repositories, a shared OpenSpec planning store, shared MCP capabilities, and bounded multi-agent work.
## Requirements
### Requirement: Developer SHALL be the authoritative workspace orchestration root

The supported shared operating mode SHALL launch Codex with `/Users/androidteam/Developer` as its workspace root, or use the desktop workspace rooted there, and SHALL apply the workspace-owned `.codex` policy, MCP configuration, hooks, agents, and skills to that root session. Direct launches inside child Git roots MAY be used for compatibility but MUST NOT be described as inheriting the parent workspace project layer.

#### Scenario: The workspace-root session starts

- **WHEN** Codex starts with `/Users/androidteam/Developer` as the current workspace
- **THEN** the effective session SHALL report that workspace root and load its intentional workspace configuration
- **AND** delegation SHALL target child repositories from that session

#### Scenario: A child repository is opened directly

- **WHEN** Codex starts from `go-microservices`, `mcp-router`, or a Python repository's Git root
- **THEN** Codex SHALL use the closest applicable project and global instruction/configuration layers for that repository
- **AND** readiness SHALL not require the child session to have byte-for-byte identical effective configuration to the workspace-root session

### Requirement: The workspace SHALL maintain an authoritative repository map

The workspace SHALL maintain a redacted, reviewable map of every child repository and its role, language/toolchain, closest `AGENTS.md`, Git root, and focused verification commands. The map SHALL identify `openspec-store` as the planning repository and SHALL distinguish shared directories and caches from Git repositories.

#### Scenario: An agent receives a repository target

- **WHEN** work is delegated to a child repository
- **THEN** the dispatch context SHALL include the repository path, role, closest `AGENTS.md`, current Git status, toolchain entry point, and required verification commands
- **AND** the agent SHALL report the target and ownership before making changes

#### Scenario: A repository map entry is stale

- **WHEN** a mapped path is missing, no longer a Git root, or its toolchain/instructions have changed
- **THEN** readiness SHALL mark the entry stale or degraded with the exact path and repair action
- **AND** no agent SHALL silently substitute another repository

### Requirement: Child repositories SHALL retain independent ownership boundaries

Each child repository MUST retain its own Git state, toolchain, `AGENTS.md` hierarchy, repository-owned skills, generated artifacts, and lifecycle. Workspace orchestration MAY read or dispatch into these repositories but MUST NOT merge their Git histories or silently rewrite their repository-owned instruction and skill surfaces.

#### Scenario: Two child repositories are changed in one task

- **WHEN** a feature spans two or more child repositories
- **THEN** each repository SHALL receive an independent target and verification result
- **AND** Git status, commits, and rollback evidence SHALL remain attributable to the owning repository

### Requirement: OpenSpec planning SHALL resolve only to openspec-store

All workspace planning changes, specs, archives, and reports SHALL live under `/Users/androidteam/Developer/openspec-store/openspec/`. OpenSpec commands run from the workspace root or externalized child repositories SHALL resolve to registered store id `openspec-store` through explicit `--store`, the machine `defaultStore`, or an approved pointer. A child repository MUST NOT acquire a local planning root; `ai-harness-skills/openspec/schemas/` remains an explicitly documented code dependency and is not planning content.

#### Scenario: A command resolves from representative roots

- **WHEN** `openspec list --json`, `status`, `instructions`, or `validate` runs from `/Users/androidteam/Developer`, `go-microservices`, `mcp-router`, or a Python repository
- **THEN** the JSON root SHALL identify `/Users/androidteam/Developer/openspec-store` and store id `openspec-store`
- **AND** the result SHALL record the actual resolution source (`global_default`, `declared`, or explicit store) rather than relying on a path assumption

#### Scenario: A child planning directory is proposed

- **WHEN** an agent proposes creating `openspec/specs` or `openspec/changes` in a child repository
- **THEN** the orchestration policy SHALL reject the proposal as outside the workspace planning contract
- **AND** the agent SHALL use the shared store with the required `--store openspec-store` context

### Requirement: Codex execution SHALL be unrestricted at the workspace root

The workspace-root effective Codex policy SHALL set `approval_policy = "never"` and `sandbox_mode = "danger-full-access"`, expose all configured MCP Router tools without a Codex-side deny list or write-approval gate, and pass that policy to delegated agents. Existing credentials in `~/.codex` SHALL remain unchanged and SHALL NOT be printed in diagnostics; unrestricted execution SHALL NOT authorize cross-repository ownership violations.

#### Scenario: A delegated agent starts

- **WHEN** a custom agent is spawned from the authoritative workspace-root session
- **THEN** it SHALL inherit the never-approval and danger-full-access policy and the complete configured MCP Router surface
- **AND** its instructions SHALL name its target repository/worktree and write authority

#### Scenario: Router guardrails are present

- **WHEN** the live router reports its own blocked commands or allowed directory scope
- **THEN** the report SHALL distinguish those router-owned guardrails from Codex's unrestricted policy
- **AND** it SHALL not claim that the router scope is a complete OS security sandbox

### Requirement: Multi-agent execution SHALL be bounded and role-oriented

Workspace multi-agent configuration SHALL enable delegation with `max_concurrent_threads_per_session = 8`, default subagent model `gpt-5.6-terra`, and medium reasoning effort. Custom `workspace_explorer`, `reviewer`, `verifier`, and `docs_researcher` roles SHALL state authority, output contract, target context, and write ownership. Overlapping writes SHALL be rejected or serialized and one primary agent SHALL own integration and final verification.

#### Scenario: Independent read-heavy work is delegated

- **WHEN** exploration, review, documentation research, or test triage can proceed independently
- **THEN** the primary agent MAY delegate bounded work within the cap
- **AND** each worker SHALL return concise evidence with paths, commands, findings, and unresolved risks before synthesis

#### Scenario: Overlapping write work is proposed

- **WHEN** two workers would edit the same repository or overlapping files
- **THEN** the policy SHALL reject or serialize the work and retain one integration owner
- **AND** full filesystem access SHALL not be treated as permission to bypass this rule

### Requirement: Readiness SHALL require root-aware live evidence

A setup SHALL be reported ready only after evidence from the workspace-root session covers effective Codex identity and policy, MCP discovery/handshake, skill and hook behavior, repository-map integrity, OpenSpec store resolution, and enabled knowledge indexes. Configuration presence alone SHALL be classified as configured, not live or ready.

#### Scenario: Representative checks pass

- **WHEN** the workspace root, Go repository, MCP Router repository, and one Python repository pass their applicable checks
- **THEN** the report MAY mark the shared workspace ready with exact roots, versions, commands, and redacted evidence
- **AND** unrelated dirty paths and unverified checks SHALL remain separately classified

#### Scenario: A diagnostic is non-interactive

- **WHEN** `codex doctor` reports a terminal-only warning such as `TERM=dumb`
- **THEN** the report SHALL separate that environment limitation from actual configuration and MCP results
- **AND** it SHALL not classify the whole workspace as failed solely for that warning

### Requirement: Existing host credentials SHALL remain unchanged

The change SHALL treat existing provider and authentication credentials under `~/.codex` as authoritative no-touch state. Implementation MUST NOT rotate, revoke, migrate, replace, compare, print, delete, or overwrite those canonical credential values. Redundant host-owned blocks or credential copies under the workspace project layer MAY be removed after a presence-only check confirms the corresponding host setting, without reading or comparing its value.

#### Scenario: Workspace configuration is normalized

- **WHEN** an ignored non-credential host-owned block is removed from `/Users/androidteam/Developer/.codex/config.toml`
- **THEN** the existing provider/authentication configuration in `~/.codex` SHALL remain unchanged
- **AND** no credential value SHALL appear in commands, diffs, reports, or retained evidence

#### Scenario: A redundant workspace credential copy is encountered

- **WHEN** inventory identifies a credential-bearing copy under `/Users/androidteam/Developer/.codex`
- **THEN** the path MAY be removed only when it is explicitly allowlisted and a presence-only check confirms the authoritative host setting in `~/.codex`
- **AND** no value comparison, output, rotation, revocation, migration, replacement, or canonical credential update SHALL occur

### Requirement: Workspace cleanup SHALL be allowlisted and reversible

Cleanup of workspace Codex state SHALL use a dry-run preservation manifest, keep `~/.codex` and ambiguous paths outside the cleanup target, and preserve rollback evidence. Explicitly approved redundant workspace credential copies MAY be removed using presence-only confirmation; managed OpenSpec mirrors, workspace agents, hooks, skills, and unrelated repository data SHALL be preserved.

#### Scenario: Cleanup is previewed

- **WHEN** an operator requests cleanup of `/Users/androidteam/Developer/.codex`
- **THEN** the report SHALL list retained, removable, redundant-credential-copy, and ambiguous path categories plus estimated impact without printing values or deleting anything
- **AND** ambiguous ownership SHALL fail closed

#### Scenario: Cleanup is applied

- **WHEN** the allowlist contains no ambiguous removable path
- **THEN** only approved redundant workspace copies, stale state, cache, log, or session paths SHALL be removed
- **AND** workspace configuration, hooks, agents, managed mirrors, store artifacts, and unrelated Git work SHALL remain intact


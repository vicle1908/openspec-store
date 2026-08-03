## Context

`/Users/androidteam/Developer` is a workspace directory rather than a single Git repository. It contains independent child Git roots, a shared OpenSpec store, and workspace-level Codex surfaces. Official Codex guidance supports project configuration and `AGENTS.md` discovery from the detected project root down to the working directory; it does not make a parent directory's project layer an automatic parent of unrelated child Git roots. The supported operating mode is therefore a Codex session rooted at `Developer`, with explicit dispatch into child repositories.

The current live MCP Router check identifies client `mcp-router` `1.0.0`, router version `0.2.46`, `allowedDirectories = ["/Users/androidteam/Developer"]`, and router-owned blocked commands. Those facts prove routed capability, not local `mcp-router` checkout readiness and not an OS security boundary.

## Goals / Non-Goals

**Goals:**

- Make the Developer-root session predictable and authoritative for cross-repository orchestration.
- Keep child repositories independent and require target-aware dispatch.
- Keep all OpenSpec planning in `openspec-store` and make resolution observable.
- Provide unrestricted Codex execution and complete Router exposure while keeping the existing `~/.codex` credential unchanged and retaining redacted reporting and repository ownership.
- Establish bounded, role-oriented multi-agent delegation and root-aware readiness evidence.
- Preserve managed skill ownership and provide reversible cleanup planning.

**Non-Goals:**

- Changing application or MCP Router source code.
- Making direct child-repository Codex launches inherit the workspace project layer.
- Replacing the shared OpenSpec store or syncing its main specs before implementation.
- Rotating, revoking, migrating, replacing, or otherwise updating the existing credential configuration in `~/.codex`.
- Treating Desktop Commander/MCP Router allowlists or blocked commands as a complete security boundary.
- Enabling concurrent implementation writes in the same repository or worktree.

## Architecture

| Layer | Owns | Does not own |
| --- | --- | --- |
| Host `~/.codex` | Provider/auth/profile, notification, host runtime, and other user-home settings | Workspace MCP/agent behavior or child-repository policy |
| Workspace `/Users/androidteam/Developer/.codex` | `approval_policy = "never"`, `sandbox_mode = "danger-full-access"`, workspace MCP Router and AgentMemory hooks, multi-agent defaults, custom agents, and root-scoped guidance | Child Git history, repository toolchains, or generated repository skill sources |
| Workspace `/Users/androidteam/Developer/.agents/skills` | Reusable cross-repository skills, including the workspace OpenSpec surface | Repository-specific domain skills and generator ownership |
| Child repository | Its `.git`, closest `AGENTS.md`, local `.codex/`, `.agents/skills`, manifests, toolchain, tests, and lifecycle | Shared planning ownership and unrelated child repositories |
| `openspec-store` | All shared specs, active changes, archives, and reports | Application source code and per-repository implementation state |

The workspace session is the integration owner. Every delegated job carries a target repository/worktree, closest `AGENTS.md`, Git status, toolchain, verification commands, and allowed write scope. Child repositories are never treated as one merged Git tree.

## Decisions

### 1. Launch at Developer and dispatch explicitly

Use the Codex app workspace rooted at `/Users/androidteam/Developer`, or launch the CLI with that directory as its working root. Do not manipulate `project_root_markers` merely to make unrelated child repositories appear to be one Git project. Direct child launches are supported for focused work but are verified independently and are not the source of cross-repository orchestration truth.

### 2. Keep host-owned settings in the Codex home and workspace behavior in Developer

Host provider/auth/profile/notification settings already present in `~/.codex` remain authoritative and unchanged. Workspace execution, MCP, hooks, agents, and multi-agent policy remain under `Developer/.codex`. Ignored `model_provider`, `model_providers`, `notify`, and `profiles` blocks may be removed from workspace project configuration after a presence-only check confirms the host-owned setting exists. Redundant workspace credential copies may be removed through the approved allowlist, but the implementation does not update, compare, print, rotate, or replace the canonical `~/.codex` credential value.

### 3. Apply full execution access with bounded orchestration

The workspace-root effective policy is `approval_policy = "never"` and `sandbox_mode = "danger-full-access"`. Multi-agent tools are enabled with `max_concurrent_threads_per_session = 8`, default subagents `gpt-5.6-terra`, and medium reasoning. Full access is intentional, but one writer per repository/worktree, explicit ownership, bounded delegation, and primary-agent integration remain mandatory.

### 4. Preserve the complete Router surface but distinguish router guardrails

The Codex-side deny list and write approval gate are not used. All configured MCP Router tools remain exposed. The live Router's own `allowedDirectories` and blocked-command list are recorded as router behavior, not represented as a complete security sandbox and not silently altered by this change.

### 5. Use the shared store as the only planning home

Every change proposal, spec, design, task list, archive, and report is written to `/Users/androidteam/Developer/openspec-store/openspec/`. Verify resolution from workspace, Go, MCP Router, and representative Python roots using JSON root metadata. Do not create child planning folders; the `ai-harness-skills/openspec/schemas/` directory is a code dependency exception only.

### 6. Keep skills manifest-owned

Preserve the 12 canonical OpenSpec skills and the Go repository's `.agents/skills`/`.codex/skills` byte-for-byte mirrors. Refresh workspace copies through the existing owning workflow. Do not run destructive migration or hand-edit generated files.

### 7. Clean up only through a credential-preserving allowlist

Inventory workspace `.codex` paths into retained, redundant credential copy, runtime/cache, generated, or ambiguous classes. Preview all removals, keep `~/.codex` and ambiguous paths outside the cleanup target, preserve rollback evidence, and remove only explicitly approved workspace copies or clearly owned runtime/cache state without comparing credential values.

## Verification Matrix

1. Confirm the workspace root, all child Git roots, repository map, closest instructions, dirty state, and toolchains.
2. Run `codex doctor --json`, effective policy, feature, MCP, agent, hook, and skill checks from the workspace-root session; direct child probes are compatibility evidence only.
3. Verify MCP Router identity, allowed directory, tool discovery, and a harmless routed search; inspect local checkout readiness separately.
4. Verify `openspec-store` resolution and strict validation from workspace, Go, MCP Router, and Python roots; classify `global_default`, `declared`, or explicit store source.
5. Run managed skill parity, Graphify/GitNexus probes, redacted-output checks, and credential-preserving cleanup dry-run checks.
6. Record exact commands, versions, redacted outputs, unrelated dirty paths, and unresolved risks. `TERM=dumb` or other non-TTY warnings are not configuration failures.

## Risks / Trade-offs

- **Root-session trade-off:** direct child launches may not see workspace MCP/agent behavior. → Keep the supported cross-repo workflow rooted at Developer and verify compatibility launches separately.
- **Blast radius:** unrestricted Codex and complete Router exposure increase accidental or prompt-injection impact. → Keep explicit target ownership, concurrency cap, redacted evidence, and OS/account isolation as operator responsibilities.
- **Credential preservation:** workspace normalization could accidentally modify the existing host credential. → Keep `~/.codex` outside the write scope, use presence-only checks, redact diagnostic output, and restrict any duplicate removal to explicitly approved workspace paths.
- **Stale indexes:** configured knowledge tools may remain unavailable. → Separate configured, indexed, live, degraded, and ready states.

## Migration Plan

1. Capture workspace-root and child-root inventories, current effective configuration, Git state, live MCP identity, store resolution, and skill manifests.
2. Record `~/.codex` provider/auth credentials as authoritative no-touch state without printing or comparing values.
3. Remove redundant host-owned workspace blocks through a presence-only, allowlisted check; do not compare or modify the existing `~/.codex` credential, profile, provider, or notification values. Keep workspace execution/MCP/hooks/agents under `Developer/.codex`.
4. Set and verify unrestricted policy and bounded multi-agent defaults in the workspace-root session.
5. Create target-aware custom agent definitions and run read-only plus disposable full-access delegation smoke checks.
6. Verify Router surface and directory scope, then reconcile OpenSpec skills through their manifests while preserving Go mirrors.
7. Verify `openspec-store` from every representative root and reject accidental child planning roots.
8. Refresh knowledge indexes only through their owning workflows, then preview/apply the cleanup allowlist while keeping `~/.codex` and ambiguous paths untouched.
9. Run strict targeted and full-store validation, classify unrelated failures, and retain rollback evidence.

Rollback restores the captured workspace configuration, hooks, agents, and manifest-owned skill copies, and disables the new unrestricted policy if explicitly requested. Credential state in `~/.codex` is unchanged in both forward and rollback paths.

## Why

The workspace now has several agent skill surfaces, including `.agents/skills`
and `.claude/skills`, plus generated Graphify and GitNexus content. The current
layout contains broken per-skill links, while the `npx skills` CLI can create
additional links by default. This makes a clean clone, cloud synchronization,
and rollback less predictable.

Graphify supports both generic `.agents/skills` and native Claude installation,
whereas GitNexus 1.6.9 generates project skills under `.claude/skills`. A
directory-level `.claude/skills -> ../.agents/skills` link therefore cannot be
assumed to preserve both tools' native contracts.

## What Changes

- Define `.agents/skills` as the canonical project-scoped shared skill tree for
  the outer repository and the independent `mcp-router` repository.
- Preserve `.claude/skills` as a real directory for Claude/OpenSpec and
  GitNexus-native project skills.
- Add a reproducible `npx skills` synchronization contract using
  `skills-lock.json`, explicit agent selection, and `--copy` for generated
  surfaces that must survive cloud sync and fresh clones.
- Repair and detect broken skill links without deleting hand-authored skills.
- Keep Graphify and GitNexus official CLIs as the source of truth for their
  installation, hooks, MCP configuration, and platform-specific skill bundles.
- Add a disposable fixture gate before any optional root `.claude/skills`
  directory symlink is enabled.
- Apply the same ownership and verification rules independently to both Git
  roots, preserving the nested repository boundary.

## Capabilities

### New Capabilities

- `agent-skill-distribution`: Canonical, reproducible, multi-agent skill
  surfaces and safe synchronization for Graphify, GitNexus, Agentmemory, and
  repository-owned skills.

### Modified Capabilities

- `developer-code-intelligence`: Clarify that Graphify/GitNexus native
  platform layouts take precedence over a shared directory symlink.

## Impact

- New or updated tooling under `scripts/`, `tools/`, and the root `Makefile`.
- `.agents/skills`, `.claude/skills`, `skills-lock.json`, agent guidance, and
  configuration snapshots in both Git roots.
- No Go services, production manifests, runtime APIs, credentials, or graph
  index data are changed.
- The implementation must preserve Agentmemory hooks and all unrelated dirty
  changes in `mcp-router/`.

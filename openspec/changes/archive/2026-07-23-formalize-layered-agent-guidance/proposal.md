## Why

The workspace now has layered `AGENTS.md` guidance for distinct development
domains, but OpenSpec does not define the behavior, ownership, or validation of
that instruction hierarchy. Without a normative capability, guides can drift
from repository commands, disappear from a required scope, contradict generated
agent surfaces, or fail to load at a nested Git boundary without a release gate
detecting the regression.

## What Changes

- Establish a layered agent-instruction contract with one concise root guide
  and scoped guides for services, platform, deployment, OpenSpec, scripts, and
  the independent MCP Router repository.
- Define deterministic precedence: explicit user instructions override project
  guides, and the closest applicable project guide refines broader guidance.
- Require every guide to identify its scope, authoritative commands,
  architecture or safety constraints, and focused verification expectations.
- Separate hand-authored repository guidance from generated agentmemory wiring,
  mirrored OpenSpec skills, validation evidence, and other generated surfaces.
- Add validation that checks required guides, discovery chains, referenced
  paths and commands, generated-file ownership language, and nested-repository
  coverage.
- Preserve existing runtime APIs, service contracts, deployment topology, MCP
  authentication, and agentmemory behavior; this change governs contributor
  instructions rather than those systems.
- Roll out as a documentation and validation change. Rollback removes the
  validation gate and scoped guides together, restoring the prior root-only
  behavior without data or runtime migration.

## Capabilities

### New Capabilities

- `agent-instruction-governance`: Defines layered `AGENTS.md` discovery,
  required workspace scopes, content ownership, generated-surface boundaries,
  and verification behavior.

### Modified Capabilities

None.

## Impact

The change affects repository instruction documents, OpenSpec artifacts, and
the repository validation surface. It spans the outer Go monorepo and the
nested `mcp-router/` Git repository but does not change service ownership,
Protobuf or REST contracts, database schemas, deployment resources, external
dependencies, or production state. Existing dirty worktrees remain
user-owned and must not be rewritten while introducing or validating guides.

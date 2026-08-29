## Context

The live provider and tooling state has advanced, but selected canonical docs and specs still describe stale values. The Prime Agent tooling row still reports version 0.7.1 and no MCP Router configuration, while the installed Prime Agent is 0.8.1-beta.564.1.d60fab8 and has an MCP Router stdio entry. Claude Code canonical specs still describe the removed `fable[1m]` selector. The generic consumer-CLI OmniRoute requirement does not account for the reviewed Prime Agent allowlist.

## Goals / Non-Goals

**Goals:**

- Update documentation to the verified Prime Agent version and MCP Router state.
- Sync Claude Code profile and routing specifications to `Claude-Fable[1m]`.
- Preserve the general consumer-CLI OmniRoute requirement while documenting the reviewed Prime Agent allowlist exception.
- Add the canonical OmniRoute routing requirement for the applied Prime Agent provider registration.
- Keep all changes limited to documentation and canonical specification text.

**Non-Goals:**

- Do not modify runtime provider, model, CLI, or MCP configuration.
- Do not perform live provider inference.
- Do not broaden any OmniRoute allowlist.
- Do not update historical archived evidence.
- Do not touch the unrelated NTU keynote change.

## Decisions

1. Update `docs/cli-agent-tooling-contract.md` using the verified installed Prime Agent version and the observed `mcp-router` stdio entry.
2. Use MODIFIED requirements for the two Claude Code capabilities and preserve their existing requirement and scenario names.
3. Keep the generic consumer-CLI OmniRoute requirement but add an explicit Prime Agent exception scenario. This avoids changing other CLI registrations while documenting the reviewed Prime Agent allowlist.
4. Generate the OmniRoute routing delta from `~/.prime/agent/models.json` so the provider values and model IDs are copied verbatim from the authoritative source.
5. Do not directly rewrite historical archived evidence; only canonical docs and active specs are synchronized.

## Risks / Trade-offs

- The Prime Agent row is verified only for Graphify, GitNexus, Agentmemory, and MCP Router compatibility; no unverified capability is claimed.
- The generic OmniRoute requirement now has an explicit exception, so future CLIs must either follow the generic pair or record a reviewed exception.
- Documentation updates are intentionally limited to stale live-state fields.

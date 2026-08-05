# Dependency Amendment: optimize-hermes-agent-configuration

## Status

Independently reviewed as a compatible boundary; not yet integrated into the shared store and not a live-mutation authorization. Task 1.5 remains blocked until this artifact is committed and integrated with its invariant preserved.

## Existing constraint

The active `optimize-hermes-agent-configuration` change treats Hermes's
`mcp_servers.mcp-router` definition as immutable. Its design explicitly
preserves the command, package reference, arguments, environment, credential
references, timeout, connect policy, transport, tool filters, resource filters,
prompt filters, sampling, elicitation, reload behavior, and server identity.
The only permitted Hermes-side mutation is the separate
`mcp_servers.mcp-router.supports_parallel_tool_calls=true` declaration; no
other Hermes Router field may change.

## Compatible boundary

`centralize-mcp-knowledge-servers` owns mutation only for the named GitNexus,
Graphify, and AgentMemory router-child definitions and their provider-specific
registry/proxy/adapter/engine state. The exact package lock, read-only client
bridge inventory, and fixture-safe transactions are verification evidence, not
router mutation ownership. This change does not own or mutate the MCP Router
core, bridge or authentication/token state, transport/listener, router-wide
policy, unrelated child providers, or any Hermes-side bridge field.

`optimize-hermes-agent-configuration` owns Hermes-side configuration and may
change only its explicitly approved parallel-call declaration. Neither change
may rewrite the other's surface.

The shared invariant is:

```text
Hermes client -> existing authenticated MCP Router bridge -> router-owned
GitNexus / Graphify adapter / AgentMemory boundaries
```

A valid combined plan SHALL preserve the Hermes bridge fingerprint while
changing only router-owned provider-child inputs after provider eligibility,
rollback, and readiness evidence pass.

## Release condition

Task 1.5 remains blocked until the active Hermes change is either completed and
archived with its MCP Router invariant preserved, or an explicitly reviewed
amendment records this compatible boundary in the shared store. This artifact
alone does not release live mutation. A separate immutable prerequisite plan and
operator `GO` remain required for package installation, native refresh, engine
restoration, client/router configuration, process restart, or cutover.

## Verification

The combined review SHALL compare:

- Hermes-side MCP Router command/args/environment/filters before and after.
- Router-owned provider-child plan and exact package-lock/evidence digest.
- Client topology inventory showing one bridge per active client and no direct
  provider registrations.
- AgentMemory engine-backed health and native tool identity.
- Graphify native package and adapter project identity.
- Apply/restore manifest plus third-state and canary checks.

No credential value, memory payload, authenticated URL, or router token belongs
in this amendment or its evidence.

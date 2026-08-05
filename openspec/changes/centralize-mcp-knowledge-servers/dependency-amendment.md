# Dependency Amendment: optimize-hermes-agent-configuration

## Status

The original provider-child boundary was independently reviewed and integrated
at shared-store revision `104da6b`; that completed historical task 1.5 but did
not authorize live mutation. The access-map-only MCP Router app extension was
independently approved and integrated at shared-store revision `6013b85`,
completing task 1.5a without authorizing live mutation.

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

`centralize-mcp-knowledge-servers` owns the named GitNexus, Graphify, and
AgentMemory router-child definitions, their provider-specific
registry/proxy/adapter/engine state, and only the existing coding-agent tokens'
server-access maps through the bounded MCP Router app transaction. It does not
own raw token values or token creation, rotation, deletion, export, or restore.
The exact package lock, read-only client bridge inventory, and fixture-safe
transactions are verification evidence, not router mutation ownership. This
change does not own or mutate the MCP Router core, client bridge,
transport/listener, router-wide policy, unrelated child providers, or any
Hermes-side bridge field.

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

## Dependency reconciliation condition

The original provider-child boundary was integrated at `104da6b`, and the
existing-token access-map extension was integrated at `6013b85`. Neither
reconciliation releases live mutation. Separate immutable prerequisite and cutover generations,
the app-minted in-UI capability, and the corresponding operator approvals remain
required for package/app installation, native refresh, engine restoration,
client/router configuration, process restart, or cutover.

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

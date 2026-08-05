## Context

Pi is intentionally minimal, while this machine loads seven third-party packages and one custom global memory extension. Configuration evaluation therefore must separate Pi core guarantees from extension behavior and must inspect the effective composition rather than the core CLI alone.

The prior verification used `--tools mcp__mcp_router__brave_web_search`, which is a Hermes-style name, not Pi's adapter-generated name. With the adapter's default `toolPrefix: "server"`, server `mcp-router` and original tool `brave_web_search` resolve to `mcp_router_brave_web_search`.

## Goals / Non-Goals

**Goals:**

- Produce a source-grounded capability and risk assessment.
- Correct false orchestration guidance with live evidence.
- Identify high-value features already supported but underconfigured.
- Keep credentials redacted and configuration unchanged.

**Non-Goals:**

- Rotating credentials or changing Pi settings in this change.
- Installing, updating, or removing packages.
- Treating package catalog claims as equivalent to installed-version evidence.
- Claiming model context limits are verified when they are manually configured.

## Decisions

### Decision: Installed source is authoritative for extension behavior

Exact package behavior is taken from installed manifests and READMEs; web sources provide discovery and cross-checks. This avoids stale registry-index conclusions.

### Decision: Correct MCP guidance using generated names

Pi's core allowlist applies to extension/custom tools. Direct MCP tools are extension tools and are filterable by their generated Pi names. Adapter-level `directTools`, `includeTools`, and `excludeTools` remain the durable way to control prompt exposure.

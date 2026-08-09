# Proposal: Prime Agent Three-Provider Integration

## Why

The workspace has three existing model gateways—`shopapikey`, `giaoduc`, and `cockpit`—but Prime Agent is not yet configured or natively validated against them. A configuration-only integration can add Prime Agent as an optional developer CLI without forking its provider implementation or changing Hermes/application routing.

## What Changes

- Pin the evaluated Prime Agent release to stable `v0.7.1`.
- Document the supported installation path and the safe Node.js prerequisite (`>=22.8.0`).
- Add a credential-free `models.json` template for the existing gateways and model IDs.
- Map `shopapikey` and `cockpit` to Prime Agent `openai-responses`.
- Map `giaoduc` to Prime Agent `anthropic-messages`.
- Keep credentials outside tracked files, using existing environment-variable references or a supported secret command.
- Define isolated model-list, native inference, streaming, reasoning, tool-call, error, and rollback acceptance gates.
- Require real wire evidence before deciding whether any gateway needs Codex-specific handling, an extension, or a core provider change.
- Record dependency-audit findings and Prime Agent's same-user execution boundary as rollout risks.

## Protocol Boundary

Hermes currently labels two gateways with a `codex_responses` mode. That label does not prove that they implement Prime Agent's specialized `openai-codex-responses` protocol. Prime Agent SHALL initially use standard `openai-responses` and SHALL reject production enablement until native requests confirm whether each endpoint implements ordinary `/v1/responses` or Codex-specific endpoint, JWT account-ID, and header behavior.

## Scope

### In scope

- Prime Agent `v0.7.1` installation and user-level configuration.
- `~/.prime/agent/models.json` template and setup documentation.
- Five aliases: `shopapikey/fable-5`, `giaoduc/Advance`, `cockpit/gpt-5.6-sol`, `cockpit/gpt-5.6-luna`, and `cockpit/gpt-5.6-terra`.
- Isolated native validation and a reversible live-configuration transaction after approval.

### Out of scope

- Modifying `/Users/androidteam/Developer/prime-agent` source or `packages/ai/src/providers`.
- Adding a new application provider to `agent-core` or changing Hermes provider configuration.
- Committing API keys, OAuth tokens, raw authorization headers, request bodies, binaries, or user runtime state.
- Making Prime Agent mandatory in review orchestration.
- Enabling production or default traffic before all named acceptance gates pass.

## Ownership Boundaries

- **OpenSpec store:** proposal, design, tasks, sanitized evidence, and lifecycle state.
- **Prime Agent repository:** upstream source evidence only; no implementation ownership in this change.
- **User runtime:** `~/.prime/agent/`, installer-created paths, and shell files; mutated only during an approved apply phase.
- **Protected surfaces:** `~/.hermes/config.yaml`, `~/.tdt/config.yaml`, gateway services, and unrelated repositories remain unchanged.

## Success Criteria

The change is complete only when the pinned CLI loads all intended aliases, each gateway passes native inference through its intended protocol, streaming/reasoning/tool-call/error behavior is verified, no credential leaks into tracked or retained artifacts, and rollback restores the pre-change user state.

## Spec Impact

This change uses `skip_specs: true` because it adds an optional developer CLI and user-level configuration only. It does not modify an application capability, public API, or existing behavioral specification. Any later Prime Agent source/provider adapter or application-routing change requires a separate OpenSpec change with delta specs.

## Approval Gate

This proposal does not install Prime Agent, modify `~/.prime/agent`, or enable any provider. Static/review readiness is separate from live authorization: implementation and live configuration require explicit operator approval after review of `design.md`, `tasks.md`, and `review-findings.md`.

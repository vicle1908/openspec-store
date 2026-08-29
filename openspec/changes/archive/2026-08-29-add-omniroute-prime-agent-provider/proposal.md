# Proposal: Add OmniRoute Provider to Prime Agent

## Why

Prime Agent already supports codex-compatible gateways, but OmniRoute is not represented as a named provider in the Prime Agent configuration. This prevents selecting the local OmniRoute `sh/*` model namespace through a stable provider alias and leaves model capability, authentication, and fallback behavior undocumented.

## What Changes

- Add a credential-free Prime Agent `models.json` provider configuration named `omniroute`.
- Route the provider through OmniRoute's local codex-compatible Responses endpoint at `http://localhost:20128/v1`.
- Resolve the API key from the existing `OMNIROUTE_API_KEY` environment variable; never store its value in tracked files or evidence.
- Support the OmniRoute `sh/*` model namespace, with `sh/codex` as the initial default model and explicit metadata for each approved model.
- Use Prime Agent's standard `openai-responses` API initially; do not assume OmniRoute's Codex-specific routes are required.
- Add setup, model-selection, health-check, and rollback documentation plus isolated native acceptance evidence.
- Keep the integration opt-in and separate from existing `phanmemvip`, `shopapikey`, and `cockpit` providers.

## Capabilities

### New Capabilities

None. This is a user-level configuration and documentation change, not a new Prime Agent runtime contract.

### Modified Capabilities

None.

The change sets `skip_specs: true` in `.openspec.yaml` because it does not alter an application capability or public API requirement.

## Impact

- **Prime Agent user state:** `~/.prime/agent/models.json` receives an additive provider entry during apply; existing providers and credentials remain unchanged.
- **OmniRoute:** the local service must be healthy at `http://localhost:20128`, expose `/v1/models` and `/v1/responses`, and accept the configured Bearer API key.
- **Prime Agent source:** no `packages/ai` provider implementation is planned initially because `openai-responses` already supplies the required transport.
- **Model selection:** `sh/codex` is the initial canary; additional `sh/*` entries are enabled only after native capability probes pass.
- **Security:** API key values, request bodies, authorization headers, sessions, and raw provider responses are excluded from retained evidence.

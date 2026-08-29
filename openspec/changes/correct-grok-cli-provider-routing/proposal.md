## Why

Grok CLI custom-provider routing currently declares protocol and endpoint settings that do not match the live gateways, causing strict Messages/Responses decoding failures even when credentials and connectivity are valid. The configuration needs a documented, verified routing contract so all supported providers use the protocol they actually serve and OmniRoute uses its canonical local endpoint.

## What Changes

- Correct Grok CLI custom-provider registrations to use the streaming Chat Completions backend where the live gateway returns Chat Completions events.
- Configure OmniRoute through its canonical documented base URL `http://localhost:20128/v1` and `OMNIROUTE_API_KEY` environment indirection.
- Register validated OmniRoute `sh/*` model IDs and preserve existing providers, defaults, and credentials.
- Add sanitized real-call evidence covering text responses and tool calls for each supported provider.
- Document known non-working protocol combinations, including malformed Messages/Responses response shapes, without treating them as authentication failures.

## Capabilities

### New Capabilities

- `grok-cli-provider-routing`: Defines provider endpoint, protocol, credential-indirection, model-registration, fallback, and verification requirements for Grok CLI custom providers.

### Modified Capabilities

- None.

## Impact

- User-level Grok CLI configuration at `~/.grok/config.toml`.
- Local OmniRoute deployment at `~/Omniroute`, using its documented port 20128 API surface.
- Remote provider gateways at `api.phanmemvip.shop`.
- Cockpit local gateway at `localhost:51006`.
- OpenSpec evidence and verification artifacts in this change; no provider source code, credentials, Docker data, or archived OpenSpec changes are modified.

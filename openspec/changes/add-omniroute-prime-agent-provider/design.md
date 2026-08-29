# Design: OmniRoute Provider for Prime Agent

## Context

See `proposal.md` for motivation. Prime Agent's `ModelRegistry` already loads user-defined providers from `~/.prime/agent/models.json`, and its OpenAI Responses implementation can target a custom base URL. OmniRoute is running locally in Docker at `http://localhost:20128`, exposes compatible `/v1/models`, `/v1/chat/completions`, and `/v1/responses` routes, and has route-specific authentication behavior in the current deployment: `/v1/models` rejects requests without Bearer authentication, while isolated `/v1/responses` probes completed with missing and deliberately invalid credentials.

The refreshed live OmniRoute catalog returned 971 models, including 14 `sh/*` models. The requested `sh/*` namespace currently includes routed aliases such as `sh/codex`, `sh/gpt-5.6-sol`, `sh/gpt-5.6`, `sh/o3`, and `sh/default`. Catalog metadata identifies `sh/gpt-5.6-sol` as a reasoning-capable, text-and-image model with a 1,050,000-token context window and 128,000-token output limit.

## Goals / Non-Goals

**Goals:**

- Expose OmniRoute as a distinct `omniroute` provider in Prime Agent.
- Use standard `openai-responses` transport against the local `/v1` base URL.
- Keep the API key external through `OMNIROUTE_API_KEY`.
- Select models with the canonical `omniroute/<sh-model-id>` reference while forwarding the exact `sh/...` ID to OmniRoute.
- Make `sh/codex` the primary canary and allow additional `sh/*` entries only with reviewed metadata and passing probes.
- Preserve existing Prime Agent providers and provide an atomic, reversible user-level configuration transaction.

**Non-Goals:**

- No new provider implementation under `packages/ai/src/providers`.
- No modification to the OmniRoute source checkout, Docker deployment, database, credentials, or routing policy.
- No automatic exposure of all 971 catalog entries.
- No use of OmniRoute tokenized URL aliases when standard Bearer header authentication is available.
- No switch to Prime Agent's specialized `openai-codex-responses` API without independent wire evidence and a new reviewed design.
- No change to Prime Agent's global default provider unless explicitly approved during apply.

## Decisions

### 1. Use `models.json` instead of a built-in source provider

The existing custom-provider contract already supports a provider name, base URL, API type, API-key environment reference, model metadata, and compatibility flags. A configuration-only integration minimizes blast radius and avoids duplicating an codex-compatible transport that Prime Agent already maintains.

**Alternative rejected:** Adding a native provider to `packages/ai` would require API/type registration, lazy provider registration, credential detection, model-generation changes, generated catalog changes, coding-agent defaults, and a larger test matrix. That is justified only if OmniRoute needs behavior that standard codex Responses cannot provide.

### 2. Use the standard Responses API

Configure `api: "openai-responses"` and `baseUrl: "http://localhost:20128/v1"`. Prime Agent should therefore issue requests to the standard `/v1/responses` route, which OmniRoute documents and implements as a codex-compatible route. The specialized Codex transport is not selected because it carries different protocol and authentication assumptions.

**Alternative rejected:** `openai-completions` is a fallback compatibility option, not the first choice, because Responses preserves reasoning events and the existing Prime Agent gateway configurations already use it. `openai-codex-responses` is deferred until a standard Responses failure is classified and evidence proves Codex-only requirements.

### 3. Keep a reviewed static allowlist of `sh/*` models

The configuration will contain explicit model entries rather than copying the entire dynamic `/v1/models` response. The initial entry is `sh/codex`; `sh/gpt-5.6-sol`, `sh/gpt-5.6`, and other requested `sh/*` aliases may be added in the same reviewed configuration only when their context, output, reasoning, image, and tool capabilities are documented from the live catalog and native probes.

Model IDs retain the `sh/` prefix. This prevents collisions with existing providers and lets Prime Agent's canonical selector use `omniroute/sh/codex` while the request body preserves `sh/codex`.

**Alternative rejected:** Dynamic model discovery at Prime Agent startup would make availability and metadata depend on OmniRoute health, expose unreviewed providers, and require a source-level model registry feature. Static entries give deterministic startup and rollback.

### 4. Use header authentication through an environment reference

Set `apiKey` to the environment variable name `OMNIROUTE_API_KEY`. The codex Responses client supplies the Bearer header; `authHeader` is not set. No key value is written to `models.json`, OpenSpec artifacts, logs, process arguments, or evidence.

The local deployment returns `401` for unauthenticated `GET /v1/models` and accepts the configured key for that route. Isolated Prime Agent probes against `/v1/responses` completed successfully with the environment variable absent and with a deliberately invalid dummy credential. This route-specific behavior is accepted for the current localhost-only deployment as an explicit caveat, not as proof of authentication enforcement. The real-apply gate must still verify key presence without printing or retaining its value and present this caveat for operator approval.

### 5. Treat the local endpoint as an operator prerequisite

The provider is considered configured only when the local OmniRoute service is healthy and `/v1/models` can list the approved model with the configured key. A stopped service or unavailable model is a clear provider error. In the current localhost-only deployment, `/v1/models` rejects unauthenticated requests while `/v1/responses` may accept missing or invalid Bearer values; this is an accepted local-loopback caveat rather than a hard inference error. Prime Agent must not silently fall back to another provider or change the model ID.

## Risks / Trade-offs

- **[Local service dependency]** Prime Agent inference fails when Docker or OmniRoute is stopped -> document the health prerequisite and run a bounded `/v1/models` preflight before native inference.
- **[Dynamic catalog drift]** `sh/*` capabilities can change without a Prime Agent release -> keep an explicit allowlist, refresh metadata during a deliberate apply, and remove or downgrade entries when probes disagree.
- **[Responses compatibility]** OmniRoute may accept `/v1/responses` but return a shape Prime Agent cannot parse -> retain sanitized method/path/status/content-type/event metadata, classify the failure, and stop before trying another API.
- **[Model ID routing]** A slash-containing ID may be normalized or rewritten by either client -> assert the exact request model and final upstream model in redacted wire evidence.
- **[Credential exposure]** API keys can enter shell history, sessions, or diagnostics -> use environment presence checks, minimal child environments, redacted logs, and secret-pattern scans.
- **[Configuration overwrite]** Replacing `models.json` could remove existing providers -> snapshot the file, merge only the `omniroute` key, publish atomically, and verify an exact rollback path.
- **[Unsupported capabilities]** Catalog metadata may overstate tools, images, or reasoning -> start with conservative declarations and promote each capability only after a native probe.

## Migration Plan

1. Capture the pre-apply state of `~/.prime/agent/models.json`, provider list, auth state, daemon/session state, and protected configuration paths without retaining secrets.
2. Revalidate OmniRoute health, API-key presence, `/v1/models` access, and the approved `sh/*` model metadata.
3. Build an isolated Prime Agent configuration and run model-list, standard Responses wire, text, reasoning, streaming, tool, and structured-error probes.
4. After explicit apply approval, merge the reviewed provider entry into the real `models.json` atomically without changing the default provider.
5. Run one bounded native canary through `omniroute/sh/codex` and verify existing providers still resolve.
6. Roll back automatically on any failed apply canary by restoring the exact pre-apply file and verifying its hash; otherwise retain the post-apply manifest.
7. If the OmniRoute daemon is stale, restart only after active Prime Agent sessions are idle; service restart is not part of the configuration transaction.

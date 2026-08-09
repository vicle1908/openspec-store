# Design: Prime Agent Three-Provider Integration

## Architecture and ownership

Prime Agent SHALL remain an optional developer CLI consuming existing gateways through its user-level configuration. This change does not modify Prime Agent source, `agent-core`, Hermes provider configuration, gateway services, or production request paths.

```text
Prime Agent v0.7.1
  |
  +-- shopapikey/fable-5  -> https://api.phanmemvip.shop/v1 -> openai-responses
  +-- giaoduc/Advance     -> https://api.giaoduc.online    -> anthropic-messages
  +-- cockpit/gpt-5.6-sol -> http://localhost:51006/v1     -> openai-responses
  +-- cockpit/gpt-5.6-luna -> same cockpit endpoint        -> openai-responses
  `-- cockpit/gpt-5.6-terra -> same cockpit endpoint       -> openai-responses
```

The existing Hermes label `codex_responses` is not sufficient evidence for Prime Agent's specialized `openai-codex-responses` implementation. That backend has different URL, JWT account-ID, and header behavior. The initial configuration SHALL use ordinary `openai-responses`; production enablement SHALL wait for redacted native wire evidence.

## Version and installation

- Evaluated release: `v0.7.1`, commit `95afd319a78ae017a41241d50b013d656a0685ce`.
- The source checkout at `a18809e00ea30638584d87b3afea7285a9d7296c` is newer than the stable tag and is not the production evaluation target.
- Safe runtime prerequisite: Node.js `>=22.8.0`, despite the installer accepting an older preflight minimum.
- The official installer performs SHA-256 verification, but the artifact and checksum manifest originate from the same HTTPS release origin; this is integrity evidence, not an independent publisher signature.

## Configuration contract

Prime Agent SHALL use `~/.prime/agent/models.json`. The tracked template SHALL contain provider names, endpoint URLs, protocol identifiers, model IDs, and capability metadata only. Credential values SHALL remain external.

```json
{
  "providers": {
    "shopapikey": {
      "baseUrl": "https://api.phanmemvip.shop/v1",
      "api": "openai-responses",
      "apiKey": "HERMES_CUSTOM_SHOPAPIKEY_API_KEY",
      "models": [{"id": "fable-5", "reasoning": true, "contextWindow": 1000000, "maxTokens": 32000}]
    },
    "giaoduc": {
      "baseUrl": "https://api.giaoduc.online",
      "api": "anthropic-messages",
      "apiKey": "HERMES_CUSTOM_GIAODUC_API_KEY",
      "compat": {"supportsEagerToolInputStreaming": false},
      "models": [{"id": "Advance", "reasoning": true, "contextWindow": 1000000, "maxTokens": 32000}]
    },
    "cockpit": {
      "baseUrl": "http://localhost:51006/v1",
      "api": "openai-responses",
      "apiKey": "HERMES_CUSTOM_COCKPIT_API_KEY",
      "models": [
        {"id": "gpt-5.6-sol", "reasoning": true, "contextWindow": 1000000, "maxTokens": 32000},
        {"id": "gpt-5.6-luna", "reasoning": true, "contextWindow": 1000000, "maxTokens": 32000},
        {"id": "gpt-5.6-terra", "reasoning": true, "contextWindow": 1000000, "maxTokens": 32000}
      ]
    }
  }
}
```

`authHeader` SHALL not be used initially for the two OpenAI Responses providers because the OpenAI SDK supplies Bearer authentication. It SHALL not be used initially for Giaoduc because the Anthropic SDK supplies `X-Api-Key`; if the gateway requires Bearer-only authentication, configuration alone may be insufficient.

Initial capability limits are deliberate: text input, reasoning enabled, and `maxTokens: 32000` pending evidence for larger output or images. Giaoduc eager tool input streaming is disabled initially and may be enabled only after a native tool probe passes.

## Isolation and rollback

Before any live apply:

1. Use a disposable HOME or an explicit `PRIME_AGENT_CODING_AGENT_DIR` and isolated session directory for evaluation.
2. Use an explicit daemon socket when testing multiple Prime Agent profiles concurrently.
3. Inspect project-local `.prime/agent` resources, `AGENTS.md`, and `CLAUDE.md` before startup; do not trust arbitrary repositories.
4. Record existence, mode, ownership, hash, and symlink targets for `~/.prime/agent`, `models.json`, shell startup files, and installer-created paths.
5. Back up pre-existing user state with restrictive permissions.
6. Apply only the reviewed configuration.
7. On rollback, stop only processes created by this change, restore the exact backup or remove only change-owned blocks, verify hashes/modes, and confirm protected Hermes/TDT configuration is unchanged.

Rollback SHALL first be rehearsed in an isolated HOME. A newer Prime Agent state is not assumed to be backward-compatible with `v0.7.1`.

## Evidence classes and gates

Evidence is separated into:

1. Official source conformance.
2. Metadata-only gateway compatibility.
3. Redacted native wire observation.
4. Native Prime Agent inference.
5. Workspace/tool integration.
6. Rollback/reapply.

A successful `/models` request or source inspection SHALL NOT satisfy native inference, streaming, tool-call, or rollback gates.

## Native acceptance

For each alias, run a serial, one-turn, no-tool exact-sentinel probe and retain only redacted command, exit status, selected alias/model, usage metadata, and clean termination. Then test:

- text streaming and terminal completion;
- reasoning events separated from assistant text;
- tool-call argument reconstruction;
- usage and context behavior;
- invalid credentials, unsupported model, timeout, rate limit, malformed stream, and context overflow;
- cross-provider session handoff.

If the standard Responses path fails, capture method/path/model/header names without values and classify the failure before considering an extension or source change.

## Failure classification and amendment protocol

| Class | Evidence | Required action |
|---|---|---|
| Endpoint joining/routing | DNS/connect failure, unexpected final path, or gateway 404 for the intended path | Stop; correct only from pinned-source plus redacted wire evidence; update design and re-review before retry |
| Authentication mismatch | 401/403 with the expected path | Stop; compare accepted header names/schemes without values; do not add `authHeader`, inline headers, or alternate protocols without design amendment and re-review |
| Request-shape incompatibility | 400/422 with a structured provider rejection | Stop; retain only status/error category and schema metadata; amend compatibility fields or create a separate adapter change |
| Rate limit/transient service | 429 or bounded 5xx | Record Retry-After/category, retry only under the explicit bounded policy; persistent failure blocks the provider |
| Streaming parser incompatibility | malformed/unknown/dropped events, missing terminal event, or issue #995 behavior | Stop; do not accept sentinel-only success; use a deterministic fixture to classify and create a separate source-fix change if needed |
| Codex-only semantics | standard `/v1/responses` rejected while independent evidence proves `/codex/responses` plus required account/header contract | Stop; amend proposal/design and obtain review/operator approval before testing `openai-codex-responses` |
| Model/capability mismatch | model unavailable, unsupported reasoning/tools/images, or effective limit differs | Remove or downgrade the capability declaration from the final catalog; re-run affected gates |
| Unknown | evidence does not fit a named class | Fail closed and request review; never silently switch endpoint, auth, model, or protocol |

No single 4xx response authorizes a protocol switch. An amendment that adds a provider adapter or Prime Agent source change is outside this config-only change and requires a separate OpenSpec change with delta specs where applicable.

## Giaoduc authentication decision

Before native inference, `WIRE-MSG-01` SHALL separately test direct Messages compatibility with `X-Api-Key` plus the required version header and, only when needed, Bearer authentication. Evidence retains status, content type, header names/schemes, and response-event categories only. Native Prime Agent behavior is accepted only when its emitted authentication form is supported. If Bearer-only behavior is required, execution stops for amendment/re-review; `authHeader: true` is not assumed to suppress the SDK's native `X-Api-Key` header.

## Output-token semantics

`maxTokens: 32000` is catalog metadata and an upper bound, not proof that each request sends 32,000. The Anthropic provider may derive a smaller request default when no explicit per-run maximum is supplied. `STREAM-01` SHALL record the effective request/output limit from native evidence, and documentation SHALL state the observed value rather than the catalog value.

## Gate traceability

`tasks.md` defines stable IDs and exact evidence roots. All execution evidence is retained beneath `evidence/<gate-id>/`. The first live mutation gate is `LIVE-01`; all preceding gateway calls use isolated state and remain subject to `APPLY-GO`. Protocol changes re-open `PLAN-05` review and operator approval.

## Security risks

- Prime Agent executes model-generated Python and project commands with the invoking user's OS permissions; workers and kernels are not a sandbox.
- `auth.json`, sessions, logs, and diagnostics may contain sensitive data.
- Project-local capability packages and extensions can execute code.
- Dependency audit findings remain a rollout risk and SHALL be recorded rather than repaired blindly with `npm audit fix`.
- Ambient environment variables SHALL be minimized during native runs so unrelated credentials do not reach the agent.

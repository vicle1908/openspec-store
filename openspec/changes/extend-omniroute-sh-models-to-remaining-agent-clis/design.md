# Design: Extend OmniRoute `sh/*` Routing to Remaining Agent CLIs

## Principles

1. **Official mechanisms only.** Use each CLI's documented provider/model surface; no framework source or adapter changes.
2. **Registration is not default selection.** Adding provider/model entries SHALL NOT change an existing default.
3. **Clean-break `sh/*` namespace.** Only live `sh/*` IDs are registered; retired `dlg/*` routes are never added.
4. **Credential indirection.** Configs reference `OMNIROUTE_API_KEY` through the CLI's environment mechanism; literal values are prohibited.
5. **One writer per file.** Each file is backed up, atomically replaced, parsed, and sentinel-tested before the next.

## Live OmniRoute baseline

At planning time (2026-08-28), `GET http://localhost:20128/v1/models` returned 968 models. The two approved IDs are present:

```text
sh/gpt-5.6-sol
sh/Claude-Fable
```

## Configuration surfaces and decision rules

| Surface | Mechanism (observed schema) | Mutation allowed only if |
|---|---|---|
| OpenCode | provider map entry: npm `@ai-sdk/openai`, options.baseURL, options.apiKey `{env:...}`, models map with name/api/limit | schema accepts endpoint + env apiKey and real `sh/*` sentinel passes |
| Droid | `customModels` array; entry keys apiKey, baseUrl, displayName, id, index, maxOutputTokens, model, noImageSupport, provider; apiKey `${VAR}` interpolation | official BYOK schema accepts entry and real sentinel passes |
| Grok | `model_providers` table (base_url, env_key, api_backend; existing backends: messages, responses) plus `model.*` aliases | provider + aliases parse and real sentinel passes |
| Codex | `model_providers` table (base_url, wire_api, env_key) | official provider entry maps to OmniRoute and real read-only sentinel passes |

## Dialect choices

- OpenCode: model entries use the chat endpoint (matches the existing phanmemvip entry shape), avoiding the Responses heartbeat defect.
- Droid: provider type `openai` (chat-completions family), matching the archived Kimi resolution.
- Grok: use the `messages` backend for OmniRoute. Its initial Responses sentinel failed with the native CLI error `serialization error: missing field sequence_number`; raw SSE capture showed a bare `response.in_progress` event without the required fields. After the evidence-based backend switch, both aliases passed the official headless sentinel.
- Codex: wire_api `responses` (the only wire_api observed in its config); the final explicit sentinels passed despite the server heartbeat defect.

## Verification contract

For each mutated CLI:

1. capture a mode-600 backup and SHA-256 hash;
2. write atomically using the CLI's official surface;
3. parse/lint the resulting file;
4. run one isolated, read-only, one-turn sentinel in a disposable directory;
5. require exact sentinel output, exit 0, and no authentication/reconnect error;
6. verify the selected route and endpoint without printing credentials;
7. roll back that file immediately if any gate fails;
8. record value-blind evidence.

Final verification SHALL include a literal-credential sweep, provider/default preservation check, exact `sh/*` namespace check, and an OpenSpec `detect_changes` gate before commit.

## Rollback

Rollback is per file: restore the mode-600 backup atomically, parse-check, and rerun the baseline sentinel for that CLI. A failed CLI SHALL NOT block verification of independent CLIs but SHALL remain unconfigured and be reported as a blocker.

## Out of scope

- provider-side credential rotation;
- framework source changes;
- changes to the five configured baselines or to any excluded CLI;
- changing defaults without explicit per-CLI approval;
- fixing the dormant Goose selected-model inconsistency (documented follow-up);
- modifications to unrelated OpenSpec changes or canonical specs.

# Tasks: OmniRoute Provider for Prime Agent

All live installation, configuration, and inference tasks are approval-gated. Retain only sanitized evidence under the change directory; never write API-key values, authorization headers, request bodies, or raw provider responses.

## 1. Research and isolation

- [x] 1.1 Record the Prime Agent checkout identity, installed version, and current `models.json` provider inventory; verify the repository status and protected user configuration remain unchanged.
- [x] 1.2 Verify OmniRoute is healthy at `http://localhost:20128`, confirm `/v1/models` requires the expected Bearer authentication, and record only model IDs, capability metadata, status codes, and endpoint paths.
- [x] 1.3 Query the OmniRoute catalog and create a reviewed `sh/*` allowlist; verify the selected `sh/codex` canary and any additional models have documented context, output, reasoning, image, and tool metadata.
- [x] 1.4 Create an isolated HOME, Prime Agent agent directory, session directory, daemon socket, and minimal child environment; verify no real `~/.prime/agent` state or unrelated credentials are touched.

## 2. Credential-free configuration

- [x] 2.1 Add the reviewed `omniroute` provider to the isolated `models.json` with base URL `http://localhost:20128/v1`, API `openai-responses`, API-key reference `OMNIROUTE_API_KEY`, and the approved `sh/*` model entries; verify JSON schema validation succeeds and no credential value is present.
- [x] 2.2 Verify `prime-agent model list` exposes `omniroute/sh/codex` and approved aliases while preserving all existing providers; retain only the sanitized model-list output.
- [x] 2.3 Record missing-key and invalid-key behavior in the isolated environment, including whether `/v1/responses` enforces authentication; verify the observed behavior does not alter configuration, sessions, or logs with secret values.

## 3. Native protocol and capability gates

- [x] 3.1 Capture sanitized request metadata for a standard Responses canary; verify Prime Agent uses `/v1/responses`, sends the expected Bearer header scheme without retaining its value, and forwards the exact `sh/...` model ID.
- [x] 3.2 Run a bounded no-tool sentinel probe through `omniroute/sh/codex`; verify exit status, exact sentinel, usage reporting by the route and preservation by Prime Agent (the `sh/codex` route currently forwards zero aggregate usage; recorded as a catalog discrepancy, with nonzero usage proven on `sh/gpt-5.6-sol`), clean terminal event, and absence of embedded provider errors.
- [x] 3.3 Verify streaming text, reasoning separation, usage accounting, and interruption behavior; retain only event types, statuses, and aggregate metadata.
- [x] 3.4 Verify tool-call argument reconstruction and tool-result replay in a disposable worktree; assert the expected marker artifact and zero outside-root mutation.
- [x] 3.5 Verify unsupported-model, timeout, rate-limit, malformed-stream, and context-overflow handling with bounded live or deterministic fixture probes; classify each failure without changing protocol, endpoint, auth, or model silently.
- [x] 3.6 Repeat the no-tool and capability probes for each additional approved `sh/*` model; remove or downgrade any model capability whose native behavior disagrees with the catalog.

## 4. Reviewed live apply and rollback

- [x] 4.1 Obtain explicit operator approval after review of proposal, design, tasks, and isolated evidence; verify the pre-apply manifest covers `models.json`, auth, sessions, logs, daemon state, and protected files without secret values.
- [x] 4.2 Merge only the reviewed `omniroute` entry into the real `~/.prime/agent/models.json` atomically; verify existing provider entries and the default provider are byte-equivalent and the new file has restrictive ownership and mode.
- [x] 4.3 Run one bounded live canary with `omniroute/sh/codex`; verify the local OmniRoute route, model ID, response completion, and no secret leakage before declaring the provider enabled.
- [x] 4.4 Rehearse and execute rollback by restoring the exact pre-apply file; verify the original hash, provider inventory, default provider, protected paths, and running service state are restored.
- [x] 4.5 Reapply the reviewed configuration after rollback, if the provider is retained; verify the final manifest and canary match the approved evidence.

## 5. Documentation and closure

- [x] 5.1 Document OmniRoute startup, API-key environment setup, `sh/*` model selection, `/v1/models` health verification, common failures, and rollback without embedding secrets.
- [x] 5.2 Run `git diff --check`, OpenSpec validation, scoped secret scans, and staged-byte verification; confirm only this change's planning artifacts are staged and commit the OpenSpec store change.

# OmniRoute Provider for Prime Agent — Operator Guide

Status: operator-approved apply, live canary, rollback, and final reapply completed on 2026-08-29. The reviewed `omniroute` provider is retained in the real Prime Agent configuration. This guide documents startup, API-key setup, model selection, health verification, common failures, and rollback. It contains no secrets.

## 1. Starting OmniRoute

OmniRoute runs locally in Docker and must be healthy before Prime Agent can use it:

```bash
docker ps --filter name=omniroute --format '{{.Names}} {{.Status}}'
# expect: omniroute Up ... (healthy)  and  omniroute-redis Up ... (healthy)
```

If it is not running, start the OmniRoute deployment (see the OmniRoute repository's own startup procedure; the Docker named volume must not be replaced by a bind mount). The provider is considered configured only when the service is healthy.

## 2. API key environment setup

- The provider resolves its credential from the environment variable `OMNIROUTE_API_KEY`.
- The managed export lives in the shared-agent-secrets block of `~/.zshenv` (mode 600). Never copy the value into `models.json`, OpenSpec artifacts, logs, or shell history.
- Value-blind presence check (prints only length, never the value):

```bash
/bin/zsh -c 'if [[ -n "${OMNIROUTE_API_KEY:-}" ]]; then print "present (length ${#OMNIROUTE_API_KEY})"; else print "ABSENT"; fi'
```

Known behavior: when the variable is unset in Prime Agent's process environment, the config-value resolver falls back to the literal variable name as the Bearer value, so stale-environment failures masquerade as bad-key errors. Relaunch Prime Agent from a fresh login shell after changing credentials.

Local-loopback caveat (accepted by operator, 2026-08-29): `/v1/models` rejects unauthenticated requests (`401`), but `/v1/responses` in the current local deployment accepts missing and invalid Bearer values. Authentication on the inference route is therefore not enforced; this is accepted only because the endpoint is localhost-only and is documented in `design.md` Decision 4/5 and `evidence/2.3-auth-behavior.md`.

## 3. Provider and model selection

The provider entry in `~/.prime/agent/models.json` (additive only; never edit other providers):

- name: `omniroute`
- `api`: `openai-responses`
- `baseUrl`: `http://localhost:20128/v1`
- `apiKey`: `OMNIROUTE_API_KEY` (environment reference, not a value)
- models: reviewed allowlist only — `sh/codex` and `sh/gpt-5.6-sol`

Select models by canonical reference: `omniroute/sh/codex`, `omniroute/sh/gpt-5.6-sol`. The exact `sh/...` ID is forwarded to OmniRoute unchanged (verified in evidence 3.1). The `sh/*` allowlist is deliberately static; do not add models without a new reviewed change. Catalog drift check:

```bash
curl -s -H "Authorization: Bearer ${OMNIROUTE_API_KEY}" http://localhost:20128/v1/models
```

Current refresh (2026-08-29): 971 catalog models, 14 `sh/*` models; both allowlist entries present.

## 4. Health verification

Preflight before inference:

1. Container health: `docker ps --filter name=omniroute` shows `healthy`.
2. `GET /v1/models` with the configured key returns `200` and lists the allowlist models; without a key it returns `401`.
3. Bounded canary (no tools, no session):

```bash
prime-agent -p --provider omniroute --model sh/codex --no-tools --no-session 'Reply with exactly CANARY-OK'
```

Expected: exit `0`, exact sentinel echoed, clean terminal event, no embedded provider error. Note that `sh/codex` currently forwards zero aggregate usage (route-specific discrepancy, evidence 3.2); `sh/gpt-5.6-sol` reports nonzero usage.

## 5. Common failures and classification

Verified classifications (evidence 3.5):

| Failure | Signal | Notes |
|---|---|---|
| OmniRoute stopped | connection refused | start Docker deployment; Prime Agent shows error stop reason, may auto-retry |
| Unsupported model | `404 model_not_found` | error stop reason; check model ID is in the reviewed allowlist |
| Rate limit | `429 rate_limit_error` | Prime Agent auto-retries with the same provider/model/path |
| Malformed stream | `200` + unparseable SSE | error stop reason after retries; do not switch API on first occurrence |
| Context overflow | `400 context_length_exceeded` | Prime Agent emits compaction events |
| Stale env key | provider "invalid key" errors in long-running sessions | relaunch from a fresh login shell |

Operational warning: several provider-failure paths still exit the CLI process with status `0`. Do not treat process status alone as success evidence — check stop reasons/event types.

## 6. Apply and rollback

Applied procedure (completed 2026-08-29 after explicit operator approval):

1. Snapshot `~/.prime/agent/models.json` and record its SHA-256.
2. Atomically merge only the `omniroute` provider entry: write and `fsync` a mode-600 temp file in the same directory, then `os.replace` over the target and `fsync` the directory.
3. Verify other providers and non-provider state are byte-equivalent, the file is valid JSON and mode 600, and `settings.json` remains unchanged.
4. Run one bounded live canary (section 4).
5. Restore the exact snapshot atomically, verify its hash/provider inventory/service state, then reapply the reviewed final configuration and repeat the canary.

Rollback procedure:

1. Read the approved `models.json.bak-omniroute-<timestamp>` snapshot bytes.
2. Write and `fsync` a mode-600 temp file in `~/.prime/agent/`.
3. Atomically replace `models.json` with `os.replace`, then `fsync` the directory.
4. Verify the restored SHA-256 matches the pre-apply hash, provider inventory is `phanmemvip`, `shopapikey`, `cockpit` only, and `prime-agent model list` no longer shows `omniroute`.

Existing `.bak-pre-*` files in `~/.prime/agent/` are unrelated historical backups; do not remove them.

## 7. Security notes

- No API-key values, Authorization values, request bodies, or raw provider responses are retained in evidence or artifacts.
- Evidence files record only model IDs, event types, statuses, sentinel matches, and aggregate usage.
- `models.json` must remain mode `600` and owned by the user.
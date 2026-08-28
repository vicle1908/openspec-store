# Evidence Manifest: research-goose-responses-decoder-blocker

All evidence value-blind. Captured 2026-08-28 (local time +07:00).

## 1. Two-part goose decoder diagnosis

goose 1.45.0, strict Rust decoder at
`crates/goose-provider-types/src/formats/openai_responses.rs`.

### Part 1 — OmniRoute heartbeat (via `custom_omniroute`)

```
Network error: Stream decode error: Failed to parse Responses stream event:
missing field `sequence_number`: "{\"type\":\"response.in_progress\"}"
```

- Bare event timing (per-event timestamps): t≈13.3s, 14.5s, 17.0s — matches the
  15s build-inlined heartbeat tick offset by request-setup latency.
- Fast prompts (<2s first token): no bare event, stream completes.
- Emitter: `node_modules/@omniroute/open-sse/utils/sseHeartbeat.ts`,
  `OPENAI_RESPONSES_IN_PROGRESS` shape → `data: {"type":"response.in_progress"}\n\n`.
- Build-inlining: 6 chunks under `/app/.build/next/server/chunks/` contain both the
  frame literal and `"SSE_HEARTBEAT_INTERVAL_MS",15e3`.
- Env-var test: `SSE_HEARTBEAT_INTERVAL_MS=0` and `=600000` set in container env
  (verified via `/proc/1/environ` and `node -e`); bare event still fired. Ineffective.

### Part 2 — upstream `response.created` shape (direct, OmniRoute bypassed)

```
Network error: Stream decode error: Failed to parse Responses stream event:
missing field `model`: "{\"type\": \"response.created\", \"response\": {\"id\":
\"resp_…\", \"object\": \"response\", \"created_at\": …, \"status\": \"in_progress\",
\"background\": false, \"error\": null, \"output\": []}, \"sequence_number\": 1}"
```

- Reproduced with `goose run --provider custom_phanmemvip --model gpt-5.6-sol`
  (direct `https://api.phanmemvip.shop/v1`, no OmniRoute hop).
- Proves the blocker is not solely OmniRoute's; goose would reject this upstream
  even with a perfect gateway.

## 2. Clean path confirmation

- Streaming `/v1/chat/completions` via OmniRoute, slow prompt: first data @11.7s,
  160 chunks, **0** malformed heartbeat events.
- Direct upstream `chat/completions`: HTTP 200, streaming 18 chunks + `[DONE]`,
  non-streaming 619B JSON — both healthy.

## 3. Rejected bundle hotfix (reverted)

- Script replaced the malformed `data:` frame with `: omniroute-keepalive\n\n`
  across 6 chunks; backups written to `/app/data/patch-backup/`.
- Post-apply: bare events eliminated (0), replaced by SSE comments.
- Rejected for: vendor-artifact mutation, non-durability (lost on compose recreate
  or image pull), inability to address Part 2, stream-corruption risk.
- Revert verified: 6 chunks restored from backup, restart, `--check` reports
  6 occurrences (original state). Backup dir removed; patch script removed from
  host (`~/Omniroute/scripts/`) and container `/tmp`.
- `docker-compose.override.yml`: 0 `SSE_HEARTBEAT` references (clean).

## 4. Post-revert system health

| CLI | Model | Result |
|---|---|---|
| omp | omniroute/sh/gpt-5.6-sol | PASS (pong) |
| omp | omniroute/sh/Claude-Fable | PASS (pong) |
| pi | omniroute/sh/gpt-5.6-sol | PASS (pong) |
| pi | omniroute/sh/Claude-Fable | PASS (pong) |
| kimi | or-gpt-5-6-sol | PASS (pong) |
| kimi | or-claude-fable | PASS (pong) |
| goose | custom_omniroute sh/* | BLOCKED (Part 1) — registration valid |
| goose | custom_phanmemvip gpt-5.6-sol | BLOCKED (Part 2) — pre-existing |

## 5. Resolution path (deferred, not executed)

- OmniRoute upstream: well-formed heartbeat (include `response` + `sequence_number`)
  or runtime-honored `SSE_HEARTBEAT_INTERVAL_MS`.
- goose upstream: tolerate keepalive events and `response.created` without `model`,
  or add a chat/completions-only mode for custom OpenAI providers.
- No local workaround satisfies "official mechanisms only" + durability.

## 6. Security

- No credential values in this manifest.
- No configuration files mutated by this change.
- Prior `OMNIROUTE_API_KEY` transcript exposure (R7) remains a pending user rotation.

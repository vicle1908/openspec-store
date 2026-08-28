# Tasks: Research goose Responses-API Decoder Blocker

## 1. Reproduce and isolate

- [x] 1.1 Reproduce goose failure via OmniRoute: `missing field sequence_number` on bare `{"type":"response.in_progress"}`.
- [x] 1.2 Reproduce goose failure bypassing OmniRoute (direct `custom_phanmemvip`): `missing field model` on `response.created` — proves two-part diagnosis.
- [x] 1.3 Locate heartbeat emitter: `node_modules/@omniroute/open-sse/utils/sseHeartbeat.ts` (`OPENAI_RESPONSES_IN_PROGRESS` shape).
- [x] 1.4 Confirm build-inlining: 6 bundle chunks contain the frame literal and `"SSE_HEARTBEAT_INTERVAL_MS",15e3`.
- [x] 1.5 Test `SSE_HEARTBEAT_INTERVAL_MS=0` and `=600000` with per-event timestamps: bare event still fires at t≈13-17s. Env var ineffective.
- [x] 1.6 Confirm streaming `/v1/chat/completions` path is clean (0 bare events, 160 chunks on slow prompt).

## 2. Attempt and reject bundle hotfix

- [x] 2.1 Build reversible patch script (replace malformed `data:` frame with SSE comment).
- [x] 2.2 Apply to 6 chunks, restart, verify bare event eliminated.
- [x] 2.3 Evaluate against deployment principles: vendor-artifact mutation, non-durable across recreate/pull, cannot fix part 2 → REJECTED.
- [x] 2.4 Revert fully: restore 6 chunks from backup, restart, confirm original state (6 occurrences present).
- [x] 2.5 Clean up: remove patch script from host and container, remove backup dir, confirm compose override has no `SSE_HEARTBEAT` entry.

## 3. Confirm system health post-revert

- [x] 3.1 Sentinel battery: omp/pi/kimi × `sh/gpt-5.6-sol`/`sh/Claude-Fable` — all 6 PASS.
- [x] 3.2 Direct upstream `chat/completions` healthy (streaming + non-streaming).
- [x] 3.3 goose remains registered (valid catalog) but runtime-blocked — expected.

## 4. Record and sync

- [x] 4.1 Write refined two-part diagnosis in proposal.md.
- [x] 4.2 Write MODIFIED delta for `omniroute-agent-cli-routing` blocker requirement.
- [x] 4.3 Write value-blind evidence manifest.
- [ ] 4.4 Strict validation + secret scan.
- [ ] 4.5 Commit, archive, sync canonical spec.

## Scope locks

- No configuration mutations in this change.
- No vendor build artifacts left modified.
- No credential rotation.
- Unrelated changes/specs untouched.

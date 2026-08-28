# Proposal: Research goose Responses-API Decoder Blocker

## Why

After `configure-omniroute-sh-models-across-agent-clis` registered `sh/gpt-5.6-sol`
and `sh/Claude-Fable` across the agent CLIs, goose remained the only CLI unable to
route through OmniRoute at runtime. The archived change documented this as a single
server-side heartbeat defect. Follow-up research shows the picture is more precise:
goose's strict Responses-API stream decoder rejects well-formed-looking events from
**two independent sources**, and one attempted local fix (a bundle hotfix) was tried,
found to violate deployment principles, and reverted. This change records the refined
diagnosis, the rejected approach, and the correct resolution path so future work does
not repeat the dead ends.

## What Changes

This is a **research and documentation change**. It makes no configuration or code
mutations. It SHALL:

- refine the goose blocker from "one server defect" to a two-part diagnosis;
- record the rejected bundle-patch attempt and why it was reverted;
- confirm the six primary CLIs (omp, pi, kimi × both models) remain healthy;
- update the canonical `omniroute-agent-cli-routing` blocker requirement with the
  refined diagnosis (MODIFIED delta);
- leave goose registered but runtime-blocked, pending an upstream goose or OmniRoute fix.

This change SHALL NOT:

- hotfix vendor build artifacts inside the OmniRoute container;
- change any CLI configuration;
- rotate credentials;
- modify unrelated changes or specs.

## Refined diagnosis (evidence-backed)

goose 1.45.0 uses a strict Rust `ResponsesStreamEvent` decoder
(`crates/goose-provider-types/src/formats/openai_responses.rs`). It fails on:

1. **OmniRoute heartbeat frame** — during slow first-token phases (>~13s), OmniRoute
   emits `data: {"type":"response.in_progress"}` with no `response` object and no
   `sequence_number`. goose error: `missing field sequence_number`.
   - Root cause: the frame and its 15s interval are **build-inlined** into 6 Next.js
     bundle chunks (`"SSE_HEARTBEAT_INTERVAL_MS",15e3`). The documented
     `SSE_HEARTBEAT_INTERVAL_MS` env var is **ignored** by this build (tested 0 and
     600000 — no effect).
   - The streaming `/v1/chat/completions` path is clean (0 bare events); only the
     `/v1/responses` slow path emits the frame.

2. **Upstream `response.created` shape** — even bypassing OmniRoute (direct
   `custom_phanmemvip` → `api.phanmemvip.shop`), goose rejects the upstream's
   `response.created` event because it lacks a `model` field. goose error:
   `missing field model`. This proves the blocker is not solely OmniRoute's.

## Rejected approach: bundle hotfix

A deployment-owned script replaced the malformed `data:` frame with an SSE comment
(`: omniroute-keepalive`) across the 6 bundle chunks. It eliminated the bare event
but is rejected because:

- it mutates vendor build artifacts (violates "official mechanisms only");
- it is non-durable (lost on `docker compose up -d` recreate or image pull);
- it cannot address diagnosis part 2 (upstream `response.created` shape);
- it risks silent stream corruption.

The patch was fully reverted; container and compose override restored to original.

## Resolution path (not executed here)

- Upstream OmniRoute issue: emit a well-formed heartbeat (include `response` +
  `sequence_number`) or honor `SSE_HEARTBEAT_INTERVAL_MS` at runtime.
- goose issue: relax the strict decoder to tolerate keepalive/heartbeat events and
  `response.created` without `model`, or add a chat/completions-only mode for
  custom OpenAI providers.
- Until either lands, goose stays registered (valid catalog) but runtime-blocked.

## Capabilities

### Modified Capabilities

- `omniroute-agent-cli-routing` — refine the heartbeat-blocker requirement into a
  two-part strict-decoder diagnosis and record the rejected hotfix.

## Impact

- No live configuration changes.
- Canonical spec gains a more accurate blocker description.
- Future agents avoid re-attempting the bundle hotfix dead end.

# Design

## Context

See `proposal.md` - Why. The operational facts that shape the approach:

- agentmemory's LLM provider abstraction always sends instructions as a
  `{role: "system"}` message ahead of a `{role: "user"}` payload, then parses a
  fixed XML envelope from the reply. It appends `/chat/completions` to
  `OPENAI_BASE_URL`, so the base URL must be bare (no method path).
- The prior endpoint `api.phanmemvip.shop` (the `shopapikey` / `phanmemvip`
  providers in `~/.pi/agent/models.json`) returned 200 but ignored the `system`
  role. Observed evidence: a system instruction "answer exactly PONG" produced
  conversational prose; the same instruction placed in the user turn was obeyed.
- OmniRoute (`127.0.0.1:20128`, OpenAI dialect) honors the `system` role and
  emitted the exact XML envelope in verification.
- OmniRoute routes `auto/*` combos across healthy upstreams. A specific alias
  (`Claude-Fable.8-flash-high`) is catalogued but pinned to the `agy` upstream,
  which is currently disconnected and returns a provider-resolution 400.
- The embedding backend is Ollama on `127.0.0.1:11434` serving
  `nomic-embed-text` (768 dims); models persist under `~/.ollama/models`.
- The agentmemory server runs under launchd (`com.agentmemory.server`), which
  injects only `PATH`, `HOME`, `CI`, and `AGENTMEMORY_URL`; all provider settings
  and secrets must therefore live in `~/.agentmemory/.env`.

## Goals / Non-Goals

**Goals:**

- Select an LLM endpoint whose behavior matches agentmemory's system-role output
  contract, with a routing strategy resilient to a single upstream being down.
- Supervise the embedding backend so it is available after login without manual
  start, using the same managed-service pattern already used on this machine.
- Make capability health observable through real success signals.

**Non-Goals:**

- Changing OmniRoute, its upstream providers, or the embedding model/dimensions.
- Introducing a model-download step or new credentials.
- Reworking agentmemory's provider abstraction or its XML contract.

## Decisions

**1. Use OmniRoute (`http://localhost:20128/v1`) as the LLM endpoint.**
Rationale: it honors the `system` role, which is the exact defect being fixed.
Alternative considered: keep `api.phanmemvip.shop` and move instructions into the
user turn — rejected because it requires modifying agentmemory internals and does
not fix other consumers of that gateway.

**2. Select an `auto/*` combo (`auto/best-coding`) rather than a specific alias.**
Rationale: a combo routes to a healthy upstream and survives a single provider
being disconnected. Alternative considered: the requested specific alias
`Claude-Fable.8-flash-high` — rejected as the primary while its `agy` upstream is
unavailable (intermittent provider-resolution 400). The specific alias can be
adopted later once its upstream is verified stable; the spec is written to prefer
a resolving combo, so this is not a blocking decision.

**3. Raise the LLM timeout bound to 120000 ms.**
Rationale: OmniRoute is measurably slow under load (one request exceeded 60000 ms
and was cut off). The upper bound is unchanged at 120000 ms, so this stays within
the documented ceiling while removing the observed timeout.

**4. Supervise Ollama as a `brew services` managed service.**
Rationale: the Ollama formula already ships a service definition
(`RunAtLoad`, `keep_alive true`, tuned env, log path), producing
`~/Library/LaunchAgents/sh.brew.ollama.plist` — the same mechanism already used
for `homebrew.mxcl.herdr` on this machine. Alternative considered: a hand-written
LaunchAgent or `nohup` — rejected as non-standard and unmanaged.

**5. Verify through function metrics and log signals.**
Rationale: `agentmemory status` reports configuration presence, not capability;
it reported "healthy/embeddings" while `mem::compress` was at 0 successes.
Verification therefore asserts non-zero compression successes, a compression
quality score, and zero embedding-skip events.

## Transaction Boundaries

- Config change: edit `~/.agentmemory/.env` (with a timestamped backup), then
  restart the launchd unit — the new provider is adopted atomically at boot.
- Supervision change: `brew services start ollama` writes the plist and loads it;
  reverting is `brew services stop ollama` plus restoring the `.env` backup.

## Risks / Trade-offs

- [OmniRoute upstream flakiness] → Prefer `auto/*` combos that route around a
  disconnected provider; keep the specific alias out of the primary path until
  its upstream is verified.
- [OmniRoute latency under load] → Raise the request bound to 120000 ms; monitor
  for timeouts and treat sustained timeouts as a provider-health finding.
- [Embedding dimension mismatch on the persisted index] → The runtime already has
  `AGENTMEMORY_DROP_STALE_INDEX=true`; both old and new embedding providers are
  768-dim, so a plain rebuild is expected to be consistent.
- [Secrets in config] → The OmniRoute key is copied into the runtime `.env`
  (outside the OpenSpec store); no secret is added to the store or to version
  control.

## Migration Plan

1. Confirm the embedding service is running and answers on `127.0.0.1:11434`.
2. Back up `~/.agentmemory/.env`; set the LLM endpoint/model/key and timeouts.
3. Restart `com.agentmemory.server`; confirm it starts and reports healthy.
4. Verify: drive a real observation (LLM compression) and a memory write
   (embeddings); confirm compression success with a quality score and zero
   embedding-skip events.
5. Rollback: restore the `.env` backup and restart; stop the Ollama service if
   reverting supervision is required.

## Open Questions

- Whether to switch the primary model to the specific `Claude-Fable.8-flash-high`
  alias once its `agy` upstream is verified stable. Deferrable: does not change
  the specs, approach, or tasks.

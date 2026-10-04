# Proposal

## Why

The agentmemory runtime's LLM-backed features were effectively disabled: its
configured provider endpoint (`api.phanmemvip.shop`) silently drops the `system`
role that agentmemory uses to deliver its structured-output contract, so
`mem::compress` recorded 0 successes against 349 failures and graph extraction,
consolidation, and summarization errored continuously; separately the local
Ollama embedding service was not running, so every vector write was skipped
(1697 `embed failed` events). Both defects are silent — `agentmemory status`
still reported the capabilities as enabled — so the degradation went unnoticed.

## What Changes

- **BREAKING (provider identity)**: Point the agentmemory LLM at a provider that
  honors the `system` role (OmniRoute at `http://localhost:20128/v1`) using a
  resilient `auto/*` combo instead of the shopapikey endpoint.
- Record that the LLM provider MUST honor a leading `system` message, because
  agentmemory delivers compression/summary/extraction instructions there and
  parses an XML envelope from the reply.
- Raise the bounded LLM request timeout to 120000 ms so a slow-but-healthy
  upstream is not cut off mid-request.
- Require the local Ollama embedding service to run as a login-starting,
  crash-restarting managed service rather than an ad-hoc process.
- Require capability verification to assert real success signals (compression
  success counts, zero embedding-skip events), not just configured-flag presence.

## Capabilities

### New Capabilities

- `agentmemory-embedding-service`: availability and supervision requirements for
  the local embedding backend that agentmemory depends on for vector writes and
  semantic recall.

### Modified Capabilities

- `agentmemory-provider-stability`: the endpoint/model requirement changes from
  the shopapikey gateway to the OmniRoute combo; the timeout bound changes from
  60000 ms to 120000 ms; a system-role contract requirement is added; and the
  documented runtime-config requirement is extended to cover the embedding service.

## Impact

- Runtime configuration `~/.agentmemory/.env` (LLM endpoint/model/key, timeouts)
  and the launchd-supervised Ollama service (`sh.brew.ollama`).
- Affects `mem::compress`, `mem::summarize`, graph extraction, semantic
  consolidation, and vector-backed semantic recall.
- Depends on OmniRoute (`127.0.0.1:20128`) and the local Ollama embedding
  endpoint (`127.0.0.1:11434`); no change is made to those systems themselves.
- No new credentials are introduced; the OmniRoute key is already present in the
  operator environment and is copied into the runtime `.env`.

## Non-Goals

- Changing, upgrading, or reconfiguring OmniRoute or its upstream providers.
- Downloading, retraining, or changing the embedding model or its dimensions.
- Making the specific `Claude-Fable.8-flash-high` alias authoritative while its
  upstream provider is unavailable.
- Editing archived changes, or modifying the unrelated active changes
  `govern-tool-version-authority-and-drift` and `agent-core-integrate-jev-system-one`.
- Adding secrets, credentials, or runtime files to the OpenSpec store.

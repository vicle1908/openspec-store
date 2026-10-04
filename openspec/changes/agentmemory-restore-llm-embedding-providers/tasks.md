# Tasks

## 1. Embedding Service Supervision

- [x] 1.1 Start the local embedding service as a managed login service and verify a plist exists under `~/Library/LaunchAgents/` with `RunAtLoad` true and `KeepAlive` true, and that the service appears loaded in `launchctl list`
- [x] 1.2 Verify the embedding endpoint answers: POST `{"model":"nomic-embed-text","input":"ping"}` to `http://localhost:11434/v1/embeddings` returns HTTP 200 with a 768-length embedding vector
- [x] 1.3 Verify model persistence across a restart: restart the embedding service and confirm the configured model still answers without re-download and the on-disk model store is preserved
- [x] 1.4 Document the embedding service name, endpoint, model, dimensions, and restart command in `docs/` and verify the documented restart command runs as written

## 2. LLM Provider Endpoint and Model

- [x] 2.1 Back up the runtime provider config to a timestamped file beside `~/.agentmemory/.env` and verify the backup reflects the prior working configuration
- [x] 2.2 Set the LLM base URL to `http://localhost:20128/v1` and the model to an `auto/*` combo in `~/.agentmemory/.env` and verify the file parses and both keys hold the intended values
- [x] 2.3 Verify the configured endpoint honors the `system` role: a request with a `system` instruction and a `user` payload returns HTTP 200 whose assistant content contains an `<observation>` element with both `<type>` and `<title>`
- [x] 2.4 Verify an unresolvable specific model alias is not selected: confirm a request naming an alias whose upstream provider is disconnected returns a provider-resolution error, and record why an `auto/*` combo is used instead

## 3. LLM Timeout Bound

- [x] 3.1 Raise `OPENAI_TIMEOUT_MS` and `AGENTMEMORY_LLM_TIMEOUT_MS` to 120000 in `~/.agentmemory/.env` and verify neither exceeds 120000 ms
- [x] 3.2 Verify a slow-but-healthy request completes within the raised bound: an LLM-backed request taking longer than 60000 ms but less than 120000 ms completes successfully rather than timing out

## 4. Capability Verification Signals

- [ ] 4.1 Restart the agentmemory server and verify it reaches a healthy state within 10 seconds and the running configuration matches `~/.agentmemory/.env` — **PARTIAL**: configuration match verified; startup measured 10.1s/15.9s/34.8s, exceeding the 10s bound (see evidence.md finding F1; deferred to a follow-up)
- [x] 4.2 Verify LLM compression produces parseable structured output: drive a real observation through the tool-use hook and confirm the log records a successful compression with a quality score and `retried: false`, and that no `Failed to parse compression XML` entry is emitted for it
- [x] 4.3 Verify vector indexing succeeds: write a memory and confirm it is saved with no `vector-index add: embed failed — skipping` entry for that write
- [x] 4.4 Verify configured-but-unreachable is distinguished from working: with the embedding endpoint made unreachable in a disposable check, confirm a single `embed failed` warning is emitted while memory persistence still succeeds
- [x] 4.5 Document the capability verification procedure (health metrics, log signals, success criteria) in `docs/` and verify the documented procedure reproduces a passing result

## 5. Integration Verification

- [x] 5.1 Run the documented verification end to end on the final configuration and confirm: `mem::compress` reports a positive success count, compression succeeds at quality score with `retried: false`, and the embedding-skip count remains zero for new writes
- [x] 5.2 Record the verification evidence (baseline vs. post-change function metrics and log signals) in a single `evidence.md` inside the change directory

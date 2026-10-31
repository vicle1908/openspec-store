# Design: Evidence-Gated OmniRoute Capability Maximization

## Context

See proposal.md for motivation and ownership. The research baseline is the observed v3.8.52 Docker deployment; source contracts and modern external documentation are not interchangeable with runtime verification.

| Evidence class | Baseline and limitation |
| --- | --- |
| Observed | Deployed package version 3.8.52, Node v26.12.0, image ID sha256:fababa40ede0927ecb9d95b8c7255247fe2da16d0df1bd75a6e390a7fa224a65, loopback-published application ports, and healthz HTTP 200. Record a fresh identity when evaluating another build. |
| Observed | Stored memory settings use hybrid retrieval, qdrant, and Voyage reranking (`voyage-ai/voyage-code-3` + `voyage-ai/rerank-2.5`). All six optional ML/browser package entry points and sqlite-vec (`v0.1.9`) resolve. `tinybert` ONNX weights (`atjsh/llmlingua-2-js-tinybert-meetingbank`, 57,837,086 bytes) are downloaded in `/app/data/models/llmlingua` and verified in isolation (1,256.81 ms cold, 41.87 ms warm, fail-open on timeout/missing weights), while the default Playwright Chromium executable is absent (`runner-base`) and superseded by active native OAuth/API providers (`agy` 15 active accounts across `gemini-3.8-flash-high`, `gemini-4-argon*`, `claude-opus-5.5`, `claude-sonnet-5.5`; `github` 2 active OAuth accounts; `muse-code`; `voyage-ai`; `jina-ai`; `openrouter`). |
| Observed | Redis reports maxmemory 0 and noeviction. Host Ollama (`ollama-local`) returns HTTP 500 (`llama-server binary not found`), failing open on Layer-2 embeddings while `voyage-ai` (`368-419 ms`), `jina-ai` (`710 ms`), and `openrouter` (`1,990 ms`) pass `POST /api/settings/cache-config/test-embedding`. The compatibility script inventory has 21 required markers across eight asserted chunk files plus 39 chunk/route replacements (15 files) and three non-chunk patches; rules R1-R8, dual chunks 87878.js/99834.js, and the non-chunk patches are currently unasserted, and lines 254-256 skip markers whose fileMatch chunk is absent. Atomic host replacement of the single-file mounted script also detaches the running container's mount inode until recreation. |
| Source-derived | Supported memory enums, local hybrid implementation, relay-only Bifrost integration, indexed pack lifecycle, browser-ready build target, worker fallback behavior, and operator rollback procedure are documented below. |
| Exercised & Deferred | Isolated side-by-side `sqlite-vec` vs Qdrant hybrid retrieval (1.00 MRR@5 on both; expiry filter gap on `vec_memories`/Qdrant), TinyBERT ONNX worker compression (corrupts unprotected identifiers; deferred), semantic-cache inner 3,000 ms deadline and `excludeSystemPrompt` system-policy collision, `/api/v1/relay/chat/completions` (`ts` mode vs `503` unconfigured Bifrost), and `/api/internal/codex-responses-ws` (`503 codex_credentials_unavailable` vs native `/v1/responses` HTTP `200`). No candidate is promoted by this plan. |

## Goals / Non-Goals

**Goals:** preserve useful native features; make optional extensions independently testable; prefer supported configuration and packaging; expose compatibility debt and recovery limits; define evidence before activation.

**Non-Goals:** changing the deployment, disabling existing capabilities, running unapproved provider calls, bypassing owner isolation, weakening safety stops, or treating syntax validation as runtime acceptance. No fixed model-size or RAM estimate is assumed for all ML implementations.

## Decisions

### 1. Preserve the native baseline; evaluate extensions independently

Native account-aware routing, existing hybrid memory/reranking, exact versus semantic cache behavior, and the current prose-preserving compression baseline stay in place. Existing main-spec contracts remain controlling; experiments use approved isolation rather than silently overriding those contracts.

Optional local-vector evaluation, model-based compression, browser providers, Codex app-server, and relay Bifrost each need a concrete use case, prerequisites, supported activation path, security boundary, resource budget, acceptance criteria, and promote/defer decision. Adding one does not require adding the others. Native multimodal, MCP/A2A, budgets, and telemetry are evaluated for the actual workload before new brokers or infrastructure are proposed.

### 2. Separate retrieval strategy, vector backend, and evaluation quality

Source: `src/shared/schemas/memory.ts:33-56`, `src/lib/memory/vectorStore.ts:285-368,426-466`, and `src/lib/memory/retrieval.ts:492-542` under the OmniRoute checkout.

- strategy: recent, semantic, hybrid.
- vectorStore: sqlite-vec, qdrant, auto.
- primaryBackend: separate backend setting; the current default is sqlite. This does not make sqlite a valid strategy or vectorStore enum.
- Local sqlite-vec plus FTS5 hybrid search is implemented; dependency presence alone does not prove extension loading, indexed vectors, or schema compatibility on the running database.

Retain current Qdrant-backed hybrid retrieval. Compare the local alternative on identical authorized corpus/query sets, embedding models, candidate limits, and reranking policy. Include identifiers, paraphrases, conflicting facts, ownership, deletion/expiry, empty results, and backend failure. Record relevance, cold/warm end-to-end latency, embedding calls, resource use, and the actual fallback tier. Define metrics and pass criteria before evaluation. A raw keyword SQL loop versus an HTTP request with a dummy vector is not semantic-search equivalence.

Qdrant supports multi-stage and fusion queries, but adopting newer server features requires both deployed-version and OmniRoute-client compatibility. `docs/architecture/cluster-decisions.md:9,34` is marked proposal; its scale guideline is not an automatic activation threshold. Do not remove Qdrant or reindex/delete live data from this planning update.

### 3. Verify runtime assets before adding packages

Source: `bin/cli/commands/packs.mjs:67-166`, `scripts/packs/optionalPackInstaller.mjs`, `Dockerfile:318-361`, and `open-sse/services/compression/engines/llmlingua/worker.ts:1-28`.

The packs CLI has list/install/verify/remove verbs. Installation consumes indexed local release archives or staged trees; it is not an npm registry installer. Distinguish the desktop/host DATA_DIR from the container DATA_DIR. Document persistent asset paths and recreate behavior instead of installing ad hoc into an ephemeral running layer.

The current image resolves the optional packages. Evaluate selected model ID/revision, worker entrypoint, model files, load success, warm/cold deadlines, and CPU/native-memory use before proposing extra packages. OmniRoute's Node ONNX implementation is not automatically the same model or footprint as Microsoft's Python examples. Its worker can return original text on failure; that is graceful bypass, not proof of successful ML compression.

For browser-backed providers, evaluate the upstream runner-web image/build target, which includes browser binaries and OS dependencies. Confirm the exact published flavor/digest or supported reproducible build before activation. Browser launch, session recovery, credential handling, provider access limits, and per-browser resource use are separate gates; Playwright presence does not guarantee CAPTCHA completion. Codex app-server is a separate provider transport, not a prerequisite for ordinary host Codex use.

### 4. Treat Bifrost as a bounded relay extension

Source: `docs/architecture/ROUTER_BACKENDS.md:110-130` and `src/app/api/v1/relay/chat/completions/route.ts:74-203,346-390`.

The integration selects a backend on the relay path, not ordinary native chat/Responses/Messages traffic. Forwarding to Bifrost bypasses the native handleChat branch; native combos, managed credentials, compression, and cache behavior must not be assumed to execute there. Any equivalent behavior needs separate evidence.

In auto mode, eligible pre-response transport exceptions can fall through to native handling; forced bifrost mode returns an error. Upstream non-OK HTTP responses and failures after streaming output begins are distinct cases, not universal transparent fallback. Evaluation covers route attribution, capability eligibility, credentials, cancellation, error shape, and partial-output behavior. Environment-file edits must not be described as live switches unless the running configuration mechanism proves that behavior.

### 5. Preserve compression and cache correctness before optimizing

Source: existing main spec `omniroute-compression-and-routing` and `open-sse/services/cache/embeddingClient.ts:105-135,199-213`.

Keep existing prose-preserving defaults. Optional LLMLingua/Caveman evaluations check code, identifiers, instructions, file/tool content, prefix caching, answer quality, tool-call correctness, and net latency. Inflation guards and fallback prevent some failures but do not prove semantic equivalence. Label token/pricing calculations as estimates with time window, model, and assumptions; do not require a lifetime token floor.

Trace each embedding deadline. The semantic-cache outer timeout is distinct from the default generator's inner 3000 ms safeOutboundFetch deadline and from local chat-header deadlines. Do not claim that raising an outer setting alone fixes cold embeddings. Record warm/cold readiness and failed-cache bypass before recommending any configuration change or implementation prerequisite.

Before altering cache scope or eviction, verify owner, relevant policy, tool-contract/history, and freshness isolation. Redis may support rate limits, quota enforcement, coordination, and disposable cache; neither allkeys nor volatile eviction is automatically safe for a shared workload. Classify enabled consumers, then test the proposed pressure policy in approved isolation. Separate instances only if justified by incompatible retention requirements. maxmemory does not include every byte of process/replication overhead.

### 6. Keep deployment and patch recovery explicit

Source: `docker-compose.override.yml:12-15,32-33`, `docker-compose.selfhost.yml:51-65`, `scripts/container-entrypoint-compat.sh:1-281`, and `scripts/update.sh:82-88,236-243,497-501`.

Retain the existing named volume and validated backup process. It avoids the known host-sharing risk for this deployment, not all possible database failures. A clean source checkout is not an unmodified runtime: the script performs textual/regex changes in the container's writable filesystem, not in-memory AST transformation.

Build a ledger per modification: target version and file/context, purpose, configuration alternative, assertion and behavioral check, upstream issue/release, removal condition, and rollback. The Gemini turn, lockout, and attempt-timing fixes are only part of the ledger; account for unasserted rules (R1-R8, dual-compiled 87878.js/99834.js, and non-chunk patches) and ensure missing or renamed target chunks fail closed instead of being skipped at lines 254-256. Do not publish invented minified-source diffs or unexecuted tests as ready PRs. Retire a modification only after its replacement works on a clean candidate image and unrelated changes remain covered.

Restart preserves the container writable layer and does not rebind a single-file bind mount (`container-entrypoint-compat.sh`) whose host inode changed after atomic replacement. Recreation from a selected known image is required both to rebind single-file host mounts and to discard filesystem patches, though the mounted entrypoint will reapply active rules on start; recreation alone is not a complete patch rollback. Record the image, patch/config version, and data-compatibility decision together. update.sh currently tags a recovery image and exits on failure; it does not implement automatic zero-downtime rollback.

## Evaluation and Future Cutover Boundaries

This update changes planning text only. Future stateful evaluation belongs in an explicitly approved disposable environment with isolated data and credentials, bounded calls, and no production ownership crossover. Each capability receives its own pass/defer decision; dependencies being installed or CLI planning status being complete do not close execution gates.

No database transaction or image switch is executed here. A future backend/image cutover must separately define admission/drain, snapshot consistency, all affected configuration/index changes, verification, and compensation/rollback boundaries. Multiple API writes, filesystem/image selection, and vector reindexing must not be treated as one atomic transaction. Do not restore an old snapshot over newer accepted writes without an explicit data-loss decision.

## Risks / Trade-offs

- More capability adds model, browser, native-memory, and provider costs; measure under the agreed concurrent workload, not a fixed enterprise bundle estimate.
- Local vectors can reduce a service dependency, while Qdrant can provide shared vector state; relevance, isolation, operational fit, and migrations decide the choice.
- Documentation and supported feature lists can lag runtime behavior; use versioned source plus exercised evidence and preserve failed checks as open gates.
- Existing main specs contain historical requirements beyond these additions. Do not silently rewrite their unrelated policy choices; document conflicts and seek a separate scoped revision when one is required.

## Primary References

- [Docker volumes](https://docs.docker.com/engine/storage/volumes/)
- [Docker version/digest pinning](https://docs.docker.com/build/building/best-practices/#pin-base-image-versions)
- [SQLite WAL constraints](https://sqlite.org/wal.html)
- [Qdrant hybrid queries](https://qdrant.tech/documentation/search/hybrid-queries/)
- [Redis eviction guidance](https://redis.io/docs/latest/develop/reference/eviction/)
- [Microsoft LLMLingua](https://github.com/microsoft/LLMLingua)
- [Bifrost deployment guidance](https://docs.getbifrost.ai/quickstart/gateway/setting-up)

# optimize-agentmemory-runtime-config

Bound AgentMemory LLM load and make optional runtime flags explicit while preserving the tested default provider and local embeddings.

## Completion status

- OpenSpec tasks: 12/12 complete
- Delta specs: skipped by design (`skip_specs: true`)
- Runtime: AgentMemory 0.9.29 healthy with a closed circuit
- Effective timeout: 90,000 ms at both AgentMemory/OpenAI timeout layers
- Explicit disabled paths: automatic compression, Agent SDK fallback, slots, and reflection
- Preserved paths: default LLM route, local embeddings, graph extraction, consolidation, context injection, snapshots, lesson decay, shared scope, viewer, and all-tool visibility
- Rollback: rehearsed successfully; persistent store and the pre-existing `.env.bak` were preserved

## Evidence and review

- Final redacted ledger: `evidence/4.2-final-ledger.md`
- Baseline/candidate latency comparison: `evidence/3.3-latency-load-comparison.md`
- Rollback rehearsal: `evidence/4.1-rollback.md`
- Review synthesis: `review-synthesis.md`
- Preflight findings and their disposition: `preflight-review.md`

The final archive review recaptured the six intended non-secret configuration
values, live worker/iii process liveness, CLI status, official doctor output,
and the supported liveness endpoint. No credential values were read into or
written from the evidence bundle.

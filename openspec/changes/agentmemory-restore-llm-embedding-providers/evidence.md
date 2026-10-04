# Evidence — agentmemory-restore-llm-embedding-providers

Verification performed 2026-10-04 while applying this change. Runtime state is
outside the OpenSpec store; this file records the observed results.

## Configuration applied

`~/.agentmemory/.env` (backup: `.env.pre-omniroute-20261004T132315Z`):

| Setting | Before (backup) | After |
|---|---|---|
| `OPENAI_BASE_URL` | `https://api.phanmemvip.shop/v1` | `http://localhost:20128/v1` |
| `OPENAI_MODEL` | `claude-fable` | `auto/best-coding` |
| `OPENAI_TIMEOUT_MS` | `60000` | `120000` |
| `AGENTMEMORY_LLM_TIMEOUT_MS` | `60000` | `120000` |

Embedding backend unchanged (`http://localhost:11434/v1`, `nomic-embed-text`, 768)
and now supervised by `sh.brew.ollama`.

## Baseline vs. post-change (function metrics, `/agentmemory/health`)

| Metric | Baseline | Post-change |
|---|---|---|
| `mem::compress` successes | **0** (of 349) | **12** (and rising) |
| Compression quality | n/a (all failed) | 90–100, `retried:false` |
| `vector-index add: embed failed` after last save | every write | **0** |
| Circuit breaker | flapping / "critical" | `closed` |

## Task verification results

| Task | Result | Evidence |
|---|---|---|
| 1.1 Service managed, RunAtLoad+KeepAlive, loaded | PASS | `sh.brew.ollama.plist` `RunAtLoad=True` `KeepAlive=True`; `launchctl list` pid 24384 |
| 1.2 Endpoint answers 768-dim | PASS | POST `/v1/embeddings` → dims 768 |
| 1.3 Persistence across restart | PASS | model store 641M unchanged; model answered after restart |
| 1.4 Documented restart runs | PASS | `brew services restart ollama` → reachable, dims 768 |
| 2.1 Timestamped backup holds prior config | PASS | backup shows `api.phanmemvip.shop` / `claude-fable` |
| 2.2 Endpoint/model set | PASS | `.env` = `localhost:20128/v1` / `auto/best-coding` |
| 2.3 System role honored + XML envelope | PASS | HTTP 200; reply contains `<type>` and `<title>` |
| 2.4 Unresolvable alias not selected | PASS | `agy/Claude-Fable.8-flash-high` → "not available in the active live catalog"; bare name → "Unable to determine provider" |
| 3.1 Timeouts raised, ≤120000 | PASS | both = 120000 |
| 3.2 Slow-but-healthy completes | PASS | 51KB payload compressed, quality 90, no timeout |
| 4.1 Restart healthy within 10s | **PARTIAL / FAIL** | measured 10.1s, 15.9s, 34.8s across three restarts — **exceeds the 10s bound** (see finding) |
| 4.2 Compression parseable | PASS | `Observation compressed type=file_write qualityScore=100 retried=false`; no parse failure |
| 4.3 Vector indexing succeeds | PASS | memory saved; 0 embed-skip events for the write |
| 4.4 Unreachable distinguished | PASS | historical log: `embed failed — skipping` warnings while `Memory saved` still succeeded |
| 4.5 Procedure reproduces pass | PASS | runbook commands executed as written; dims 768 + XML envelope |
| 5.1 End-to-end integration | PASS | compress success count positive; zero embed failures after last save (last failure line 67385 < last save line 67452) |
| 5.2 Evidence recorded | PASS | this file |

## Finding F1 — startup time exceeds the 10s bound (not met)

The spec requires the server to start within 10 seconds. Measured cold starts:
**10.1s, 15.9s, 34.8s**. The delay is dominated by loading the ~2.8 GB state
store (`~/.agentmemory/data/state_store.db`) at boot, not by the provider change.

- Impact: restart latency only; no functional or correctness impact on the
  provider behavior this change targets.
- Disposition: recorded as an unmet requirement. Options for a follow-up change:
  (a) revise the startup-time bound to reflect realistic data volume, or
  (b) address store growth/pruning (see `agentmemory-graph-persistence-backpressure`).
- Not addressed in this change (out of its scope: provider selection + timeout
  bound + embedding supervision).

## Open item (deferrable)

Switch the primary model to the specific `Claude-Fable.8-flash-high` alias once
its `agy` upstream is verified stable. Does not affect the specs or approach.

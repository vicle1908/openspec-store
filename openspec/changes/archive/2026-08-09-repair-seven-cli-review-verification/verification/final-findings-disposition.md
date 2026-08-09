# Final Findings Disposition — Rounds 6 and 7

Rounds 6 and 7 are the authoritative final verification runs. Both used fixture SHA-256 `a5a8551417c662a4dfda064bd885d5cfd1d1729c3daa08685b1e2f50cc45b472` and runner SHA-256 `c59819c09dd99ef37ffb22f95dfaa2657bbd038dc1be63a6c5fbefd59f973793`.

No final finding requires changing the verified CLI invocation, runner behavior, Pi configuration, or canonical skill content. Therefore Rounds 6 and 7 remain valid and no replacement rounds are required.

## Disposition table

| Round / reviewer | Finding | Severity | Disposition | Rationale / affected surface |
|---|---|---:|---|---|
| R6 Claude | No findings | — | Accepted | `APPROVE`; no action. |
| R6 Codex | `CONNECTION_OK` case/token matching not stated in fixture | Low | Accepted non-blocking | Runner behavior is deterministic and proven: `classify_smoke()` checks exact case-sensitive substring in combined retained output. Documentation refinement does not affect CLI capability. Affected: `verification/run_cli_reviews.py`. |
| R6 Codex | Raw-vs-redacted output hash semantics not stated in fixture | Low | Accepted non-blocking | Metadata records both raw and retained stream lengths/hashes. No runtime or integrity defect was found. Affected: per-probe metadata. |
| R6 Codex | `FINDINGS: none` should map to `PASS` | Low | Fixed before final rounds | Parser explicitly recognizes `NONE`, `NO FINDINGS`, and `NO ISSUES`; R6/R7 demonstrate `PASS`. Affected: `verification/run_cli_reviews.py`. |
| R6 Agy | Smoke `PASS` and review `PASS` terminology could be distinguished | Low | Accepted non-blocking | Probe type is explicit in each metadata file and summary fields are separately named `smoke_status` and `review_status`; no ambiguity in evidence. |
| R6 Agy | Skill durability is separate from CLI execution | Info | Out of scope for runtime, required for task completion | Durable canonical sources were an explicit user/OpenSpec requirement because installed `~/.hermes` files are not tracked. Affected: `.hermes/skills/`, `sync_skills.py`. |
| R6 Kimi | No contradictions | — | Accepted | `APPROVE`; no action. |
| R6 OpenCode | No findings | — | Accepted | `APPROVE`; no action. |
| R6 Pi | Per-CLI smoke frequency not explicit in fixture | Low | Accepted non-blocking | Runner executes one smoke per selected CLI in `run_cli()`; all evidence contains exactly one smoke record per CLI. No setup change required. |
| R6 Pi | Post-round fixture hash mismatch action not explicit | Low | Fixed before final rounds | Runner raises `SystemExit("fixture mutated during round")`, making the round non-passing. Affected: `run_cli_reviews.py`. |
| R6 Pi | Positive semantic gate could be linked more directly to return-code rule | Low | Duplicate / implemented | `review_status()` is always applied after process classification; exit 0 with malformed content is `SEMANTIC_FAILURE`. |
| R6 Pi | Pi section mentions exit 0 despite semantic gate | Info | Accepted non-blocking | The section describes the repaired process-lifecycle proof; authoritative summary also records substantive review status. No contradiction in actual evidence. |
| R6 Pi | Invocation-list order differs from batch order | Info | Accepted non-blocking | Lists serve different purposes; batch order is explicit in runner and summaries. |
| R6 Goose | Smoke prompt/evidence not fully described in fixture | Low | Fixed in implementation and evidence | Exact smoke prompt is constant in runner; stdout, stderr, and metadata are retained for every CLI. No invocation change required. |
| R6 Goose | Non-empty findings vs `FINDINGS: none` wording | Low | Duplicate / implemented | `none` is non-empty text and intentionally maps to `PASS`. |
| R7 Claude | Exact smoke prompt absent from bounded review fixture | Low | Accepted non-blocking | Exact prompt is immutable in `run_cli_reviews.py` and retained by prompt hash. Capability evidence is complete. |
| R7 Claude | `APPROVE_WITH_CONDITIONS` mapping not stated in shortened fixture | Low | Implemented | Parser maps it to `PASS_WITH_FINDINGS`; both final summaries prove the mapping. |
| R7 Claude | Goose `-q` not described | Info | Accepted non-blocking | `-q` is a lifecycle/output control verified by real execution; it does not override model/provider. Canonical guides document the full invocation. |
| R7 Claude | Non-passing statuses not enumerated in shortened fixture | Low | Implemented elsewhere | Runner and canonical workflow/troubleshooting references define distinct statuses; evidence is not ambiguous. |
| R7 Codex | `FINDINGS: none` sentinel mapping | Low | Duplicate / implemented | Explicitly handled in parser and demonstrated by final `PASS` results. |
| R7 Codex | Smoke matching stream/surrounding-output semantics | Low | Accepted non-blocking | Runner checks exact token in combined retained stdout/stderr and permits surrounding text. This is deterministic and tested by seven CLIs twice. |
| R7 Agy | No findings | — | Accepted | `APPROVE`; no action. |
| R7 Kimi | No findings | — | Accepted | `APPROVE`; no action. |
| R7 OpenCode | Pi repair wording conflates setup fix and ongoing bounded invocation | Info | Accepted non-blocking | The ongoing invocation is deliberately the verified safe default for no-tool reviews. Canonical Pi guide explains both cause and steady state. |
| R7 OpenCode | Smoke contract, fixture mismatch action, and malformed-review mapping need more prose | Low | Duplicate / implemented | All are deterministic in runner and retained evidence. No runtime defect. |
| R7 OpenCode | Pi isolation rationale not in shortened fixture | Info | Accepted non-blocking | Pi runs serially due to historically expensive MCP/extension startup and the user’s maximum-three-reviewer governance; canonical guides state this. |
| R7 OpenCode | Default-resolution failure behavior | Low | Implemented | Smoke/review classify nonzero auth/provider/model/connection diagnostics as `CONFIG_ERROR`; no alternate model fallback occurs. |
| R7 Pi | No findings | — | Accepted | `APPROVE`; no action. |
| R7 Goose | Scope of smoke failure and smoke-status mapping could be clearer | Low | Implemented | Only the failing CLI’s review is skipped; siblings/later batches continue. Summary acceptance still fails. Runner behavior and Round 1 evidence demonstrate this. |

## Gate conclusion

- No Critical or High findings remain.
- No final finding changes an invocation, configured default, Pi repair, runner acceptance behavior, or canonical skill source.
- Low/Informational documentation observations are either already implemented, duplicates, accepted non-blocking, or outside the bounded CLI-capability verification scope.
- Rounds 6 and 7 remain the authoritative consecutive clean rounds.

# SUPERSEDED — do not apply

This change was superseded on 2026-08-25 by `replace-giaoduc-with-phanmemvip`
before any live application (2/14 tasks complete; planning only).

Its premise — restoring `task: giaoduc/Advance:xhigh` and treating the
giaoduc `401 invalid_api_key` as a credential bug to repair — was invalidated
by the decision to retire the giaoduc provider entirely and replace it with
phanmemvip (Codex Responses API).

**Its delta specs MUST NOT be synced to main specs** (they would re-mandate
giaoduc routing). Archived manually without `openspec archive` to prevent
delta application. Reusable patterns (isolated-profile smoke-test gate,
atomic-rename rollout, md5-baseline rollback) were folded into
`replace-giaoduc-with-phanmemvip/tasks.md`.

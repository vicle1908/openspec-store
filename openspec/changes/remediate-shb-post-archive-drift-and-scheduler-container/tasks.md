# Tasks: Remediate SHB Post-Archive Drift, Stale Scheduler Container, and Archive Evidence Gaps

## 1. Rebuild and Verify `shb-schedule-scheduler-1` Container (`D1`)

- [ ] 1.1 Rebuild and recreate `shb-schedule-scheduler-1` from `/Users/androidteam/Developer/shb/shb-schedule` `main` (`7ed905d`+) via `docker compose -f /Users/androidteam/Developer/shb/shb-schedule/compose.yaml up -d --build scheduler` and verify `docker inspect shb-schedule-scheduler-1` reports a fresh image digest and `healthy` status.
- [ ] 1.2 Verify `curl -s http://127.0.0.1:9110/scheduler/schedules/workstation-daily-update` returns JSON containing `"execution_target": "host"` and `"persisted": false`, and `curl -s -o /dev/null -w "%{http_code}" -X POST http://127.0.0.1:9110/scheduler/schedules/workstation-daily-update/trigger` returns `409`.

## 2. Verify, Commit, and Re-Index Post-Archive SHB Jev Repositories (`D9`)

- [ ] 2.1 Run `uv run pytest`, `uv run ruff check`, and `uv run mypy --strict` across the 8 modified `/Users/androidteam/Developer/shb/shb-*` repositories (`shb-core`, `shb-agent-core`, `shb-agent-harness`, `shb-ai-harness-skills`, `shb-agent-skills`, `shb-observability`, `shb-ai-review`, `shb-mcp-servers`), then commit the 24 modified source/test files with `GRAPHIFY_SKIP_HOOK=1` so `git status --short` is empty across all 13 `shb/shb-*` repositories.
- [ ] 2.2 Clean or reconcile the 8 index/ignore working-tree files in `/Users/androidteam/Developer/tdt/agent-core` without modifying Python source/test files (confirming `git rev-parse HEAD` remains `5085b45` or index-only and `git status --short` is empty).
- [ ] 2.3 Refresh GitNexus and Graphify indexes across all stale `/Users/androidteam/Developer/shb/shb-*` repositories (`shb-core`, `shb-agent-core`, `shb-agent-harness`, `shb-ai-harness-skills`, `shb-agent-skills`, `shb-observability`, `shb-ai-review`, `shb-mcp-servers`, `shb-tools`, `shb-schedule`, `shb-webhook-receiver`, `shb-browser-cli`, `shb-jira-tools`) and verify `bash /Users/androidteam/Developer/scripts/knowledge-refresh/knowledge-status.sh` reports `FRESH` across all 13 SHB repositories.

## 3. Forward-Remediate Archive Range Readiness & Immutability Verification (`D7` & `D10`)

- [ ] 3.1 Update `/Users/androidteam/Developer/platform/openspec-store/scripts/validate-archive-readiness.py` (with unit tests in `scripts/test-validate-archive-readiness.py` or `tests/`) so `--range` mode enforces post-archive immutability on pre-existing `openspec/changes/archive/` directories while honoring documented forward-remediated archive entries (`2026-10-20-reconcile-dev-tooling-and-hermes-runtime` @ `804a8968` and `2026-10-20-upgrade-omniroute-to-v3-8-52` @ `a3eb1fda`) without editing `openspec/changes/archive/`.
- [ ] 3.2 Author `evidence.md` recording the live verification ledger for `2026-10-20-reconcile-dev-tooling-and-hermes-runtime`, the post-archive immutability audit record for `a3eb1fda`, the 8 SHB repository commit SHAs, and the rebuilt `shb-schedule-scheduler-1` container verification, and verify `python3 /Users/androidteam/Developer/platform/openspec-store/scripts/validate-archive-readiness.py --range HEAD~35..HEAD --store /Users/androidteam/Developer/platform/openspec-store --strict` exits `0`.

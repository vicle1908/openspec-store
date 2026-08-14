# Deployable Env Loading Tasks

## Status legend

- `[ ]` pending
- `[x]` done
- `[~]` in progress

## Tasks

- [x] **T1**: Repair corrupted `~/.tdt/.env` line 54 (SHEET_LINKS
  had ~50 duplicated `,Jira Catalog|...` entries). Strip down to
  clean comma-separated URL list.

- [x] **T2**: Update `ai-review/scripts/deploy.sh` heredoc template
  to drop bash `source ~/.tdt/.env`. New launcher just `exec`s
  uvicorn. Add comment explaining the env-loading strategy.

- [x] **T3**: Update `webhook-receiver/scripts/deploy.sh` heredoc
  template the same way, with `JIRA_GUARD_POLICIES_PATH` set inline.

- [x] **T4**: Update runtime `deployments/ai-review/bin/ai-review-launcher.sh`
  to match the new template.

- [x] **T5**: Update runtime `deployments/webhook-receiver/bin/webhook-receiver-launcher.sh`
  to match the new template.

- [x] **T6**: Verify `bash scripts/deploy.sh` exits 0 and both
  services are running.

- [x] **T7**: Verify `curl /health` returns 200 on both 8090 and
  8080.

- [x] **T8**: Verify full test suite passes (`pytest` in
  `ai-review/` and `webhook-receiver/`).

- [x] **T9**: Commit `ai-review` deploy.sh fix.

- [x] **T10**: Commit `webhook-receiver` deploy.sh fix.

- [x] **T11**: Update `ai-review-structured-findings` design.md to
  clarify that `CoverageScanner` and `BenchmarkRunner` are
  standalone CLI utilities, NOT wired into the orchestrator.

- [x] **T12**: Remove dead `CoverageScanner` and `BenchmarkRunner`
  instantiation from `ai-review/review_flow/orchestrator.py`.

- [x] **T13**: Drop the misleading "DBOS scheduler" mention from
  `ai-review/coverage/cli.py` help text.

- [x] **T14**: Commit the orchestrator cleanup.

- [x] **T15**: Create this OpenSpec change
  (`openspec/changes/deployable-env-loading/`) and commit.
- [x] **T16**: Update `webhook-receiver/scripts/check_uv_alignment.sh` to
  match the new env-loading contract. Replace the stale assertions that
  required `source $HOME/.tdt/.env` in deploy.sh and the launcher-level
  `export PATH=...` with negative checks that the launcher MUST NOT source
  the env and MUST NOT export PATH (those are now in the plist). Update
  the `$PLIST_PATH` assertion to `$INSTALLED_PLIST_PATH` to match the
  actual call site. Tighten the legacy-paths regex to stop flagging
  `~/Library/LaunchAgents` (the canonical macOS launchd path) and instead
  flag only `~/.tdt-webhook-receiver` / `~/.tdt-ai-review` / `~/bin/...`.
  `bash scripts/check_uv_alignment.sh` exits 0.
- [x] **T17**: Update `tdt-meta/openspec/specs/uv-runtime-management/spec.md`
  "Launchd environment loading" scenario to match the new contract:
  launcher scripts SHALL NOT `source $HOME/.tdt/.env`; the launchd plist
  provides PATH/SSL/service env vars; the Python app loads `.env` via
  `tdt_core.env.load_tdt_env()`.

## Deferred (NOT in this change)

- [x] [historical] Remove DBOS from `webhook-receiver` (selftest, dlq_reaper,
  report_freshness). Larger refactor; tracked as a follow-up.
- [x] [historical] Add automated test that injects a malformed `.env` line and
  verifies the service still starts.


---

> **Historical record:** This change was archived with 2 incomplete task(s) (17/19 completed). The remaining tasks were not implemented or were superseded by subsequent changes.

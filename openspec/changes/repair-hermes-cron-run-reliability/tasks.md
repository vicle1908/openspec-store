# Tasks: Repair Hermes Cron Job Run Reliability

## Track 1: Deterministic Watchdog

- [ ] 1.1 BLOCKED on ownership acceptance — Create `ops-automation-suite/scripts/hermes-cron/mcp-router-watchdog.sh` — deterministic wrapper
- [ ] 1.2 Unit test: healthy state → empty stdout, exit 0
- [ ] 1.3 Unit test: degraded state (critical_missing non-empty) → alert output, `--escalate` invoked
- [ ] 1.4 Unit test: state unchanged → empty stdout (no duplicate alerts)
- [ ] 1.5 Unit test: malformed JSON → error output, exit nonzero, no recovery action
- [ ] 1.6 Unit test: missing state file → treated as unknown previous, proceed normally
- [ ] 1.7 Unit test: cooldown active (last_restart <5min) → skip escalation
- [ ] 1.8 Unit test: crash_count_24h >=3 → alert includes pattern warning
- [ ] 1.9 Backup current jobs.json, convert mcp-router-watchdog to `--script` + `--no-agent` via `hermes cron edit`
- [ ] 1.10 Acceptance: manual tick → verify silent healthy output, verify state file updated
- [ ] 1.11 Rollback: revert each modified field with `hermes cron edit` (never restore jobs.json directly)

## Track 2: Read-Only Freshness Reporter

- [ ] 2.1 BLOCKED on ownership acceptance — Create `ops-automation-suite/scripts/hermes-cron/weekly-freshness-report.sh` — reads knowledge-status.sh --json
- [ ] 2.2 Test: produces clean report from current status output
- [ ] 2.3 Test: exits nonzero when canonical script missing
- [ ] 2.4 Test: exits nonzero when inventory rejected
- [ ] 2.5 Backup jobs.json, convert weekly-graphify-freshness to script + `--no-agent`
- [ ] 2.6 Acceptance: manual tick → clean report, no mutations
- [ ] 2.7 Rollback: revert each modified field with `hermes cron edit` (never restore jobs.json directly)

## Track 3: Wiki Lint Corrections

- [x] 3.1 Add `status: active` to 17 pages missing it (source: wiki-lint report 2026-08-24). The current lint contract checks `title`, `tags`, `created`, `updated`, and `status` — `type` is NOT part of the current audit.
- [x] 3.2 Set `created: 2026-08-23` + `date: 2026-08-20` on references page; update SCHEMA.md to document optional `date` field
- [x] 3.3 Fix 16 broken relative links (source: wiki-lint 2026-08-24):
  - `comparisons/knowledge-tools.md`: 7 links → `../entities/...` or `../concepts/...`
  - `concepts/mcp-transport-layer.md`: 5 links → `../entities/...`
  - `entities/mcp-router.md`: 4 links — cross-directory concept link needs `../concepts/...`, same-directory entity links stay as bare filenames
- [x] 3.4 Update `SCHEMA.md` frontmatter template to include `status: active|draft|archived`
- [x] 3.5 Commit wiki fixes in wiki repo (scoped commit: "fix: wiki frontmatter and link integrity")
- [ ] 3.6 BLOCKED on ownership acceptance — Create `wiki/scripts/wiki-lint.py` — deterministic validator (no-agent mode, zero-byte stdout when clean)
^- [ ] 3.7 BLOCKED on 3.6 — Acceptance: lint tick produces valid report (exit 0 = report generated; findings are success, not failure)

## Closure

- [ ] 4.1 `openspec validate repair-hermes-cron-run-reliability --strict --store openspec-store`
- [ ] 4.2 Verify 3 affected jobs run after changes (watchdog, freshness, wiki-lint) and confirm 2 unchanged jobs (go-microservices-monthly, weekly-skills-update) have identical definitions
- [ ] 4.3 Evidence log: before/after execution status, state files, acceptance output

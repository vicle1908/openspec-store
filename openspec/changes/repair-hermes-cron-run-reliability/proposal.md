# Proposal: Repair Hermes Cron Job Run Reliability

## Why

Three Hermes cron jobs have application-level defects that reduce reliability and produce misleading reports.

### Defect 1: mcp-router-watchdog depends on model auth
The watchdog runs `mcp-router-health.sh --json` through an LLM agent every 10 minutes. During the Aug 17–23 model-auth outage, 961 completed / 36 failed / 3 unknown (aggregate: `SELECT job_id,status,COUNT(*) FROM executions GROUP BY 1,2`) belonged to this job. HTTP 401/502 "no auth available" errors cascaded into watchdog silence. A deterministic shell health check must not depend on the thing it guards against. Current status: healthy (verified 2026-08-24 ~09:17 UTC+7; gateway PID/ticker are transient).

### Defect 2: weekly-graphify-freshness has contract drift
The job runs a hardcoded 18-repo loop with direct `graphify update` mutations, duplicating the canonical LaunchAgent refresh (`com.developer.index-refresh`, 02:30 daily). The reviewed inventory has 20 repos. The spec pins Graphify 0.9.42; installed is 0.9.46; upstream is 0.9.48. The job reports "4 rebuilt" when the canonical nightly log shows 7 repos refreshed — the weekly job overrides rather than reports.

### Defect 3: weekly-wiki-lint reports FAIL due to schema drift
17 pages missing `status` field, 1 missing `created` (git says added 2026-08-23), 16 broken relative links in 3 pages, and `SCHEMA.md`'s own template omits `status` — the systematic root cause. The lint prompt also instructs "commit intentional wiki changes" which violates read-only lint semantics.

## What Changes

### Track 1: Deterministic watchdog wrapper (no-agent)
Create a shell wrapper that reads the health script's JSON stdout and state file, performs bounded recovery, and emits output only on state change. Convert the cron job to `--script` + `--no-agent` mode. No LLM inference required.

### Track 2: Read-only freshness reporter
Convert the weekly freshness job to a script-only reporter that consumes `knowledge-status.sh --json` from the approved inventory. No `graphify update` or `gitnexus analyze` invocations. The canonical LaunchAgent remains the sole mutation owner.

### Track 3: Wiki lint corrections and deterministic validation
Add `status: active` to 17 pages. Set `created: 2026-08-23` + `date: 2026-08-20`. Fix broken relative links with `../` prefixes. Update `SCHEMA.md` template. Convert wiki lint to a deterministic no-agent validator: zero-byte stdout when clean; report findings with exit 0; emit diagnostics and exit nonzero only when the validator itself fails.

## Out of Scope
- Graphify 0.9.42→0.9.48 version pin upgrade (separate compatibility review)
- GitNexus timeout increase for go-microservices/jira-skill
- Auto-cleaning or committing unrelated dirty repos (agent-core, ai-harness-skills, ai-review, webhook-receiver)
- Historical failed execution row cleanup (audit evidence)

# Baseline Evidence: Hermes Cron Job Run Issues

## 1. Scheduler Transport Health

```
Gateway: running (PID 3049), ticker 17s ago
5 active jobs, next run: 2026-08-24T09:27:53+07:00
Execution history: 961 completed / 36 failed / 3 unknown
All 39 non-completed executions: mcp-router-watchdog (job 8bbeeb961037), Aug 17–23
Root cause: model-auth outage (HTTP 401/502 "no auth available", 1 timeout, 1 invalid tool call)
Current watchdog runs: healthy (OK output since Aug 24 09:17)
```

## 2. Job Definitions (jobs.json)

| Job | ID | Schedule | Mode | Script | Deliver |
|-----|-----|---------|------|--------|---------|
| weekly-graphify-freshness | 13ca08f6f0fd | cron 0 8 * * 1 | agent | none | origin |
| weekly-wiki-lint | 589262cf00d4 | cron 0 9 * * 1 | agent | none | origin |
| go-microservices-monthly | 5db3be894605 | cron 0 9 1 * * | agent | none | origin |
| mcp-router-watchdog | 8bbeeb961037 | interval 10m | agent | none | local |
| weekly-skills-update | 230d06bbd148 | cron 0 3 * * 1 | no_agent | skills-weekly-update.sh | local |

## 3. Wiki Lint Findings (2026-08-24)

- 17 pages missing `status` field
- 1 page missing `created` (`references/agent-ecosystem-evaluation-2026-08.md` — has `date: 2026-08-20`)
- 16 broken relative links in 3 pages (root-relative paths from subdirectories)
- `SCHEMA.md` template omits `status` — systematic root cause
- Git status: clean, HEAD=0ef5e98

## 4. Canonical Refresh State (2026-08-23 nightly log)

- 20 targets in approved inventory (SHA-256: 66189ba5...)
- 7 refreshed, 13 skipped (dirty-tree), 0 failed
- GitNexus timeouts: jira-skill (348s), go-microservices (347s)
- Graphify: all successful, code-only AST refresh
- Installed: Graphify 0.9.46, GitNexus 1.6.9
- Spec pin: Graphify 0.9.42 (from developer-code-intelligence spec)

## 5. Version Mismatches

| Tool | Installed | Spec Pin | Upstream |
|------|-----------|----------|----------|
| Graphify | 0.9.46 | 0.9.42 | 0.9.48 |
| GitNexus | 1.6.9 | 1.6.9 | 1.6.9 |

## 6. Provider CLI Verification (2026-08-24)

| CLI | Version | Status |
|-----|---------|--------|
| codex | 0.149.1 | verified |
| claude | 2.1.241 | verified |
| agy | 1.1.19 | verified |
| pi | 0.84.2 | verified |
| omp | 18.0.3 | verified |
| prime-agent | 0.8.0-beta.543.1 | verified |
| kimi | 0.38.0 | verified |

## 7. Corrections Already Discovered

- `graphify-out/` changes in 4 repos (agent-core, ai-harness-skills, ai-review, webhook-receiver) are clean rebuild outputs from the weekly job — NOT blockers for nightly refresh (the canonical script filters `graphify-out/` from its dirty gate)
- `ai-harness-skills` AGENTS.md/CLAUDE.md diffs are GitNexus-injected symbol counts — not task-owned changes
- References page `date: 2026-08-20` is the real evaluation date — rename to `created`, don't overwrite
- No `state_changed` field in health script stdout — only in state file on disk

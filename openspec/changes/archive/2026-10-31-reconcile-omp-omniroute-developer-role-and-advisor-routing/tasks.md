# Tasks

## 1. Live Config & Spec Alignment

- [x] 1.1 Update `providers.omniroute.compat` in `/Users/androidteam/.omp/agent/models.yml` (`mode 0600`) to `{ supportsReasoningEffort: true, supportsDeveloperRole: false }` and verify with `omp models --json` that all 5 `omniroute/*gemini-4-argon*` models report `thinking: ["low", "medium", "high"]` and single-turn `omp -p` advisor review completes with `**SILENT**` in 1 turn.
- [x] 1.2 Update `modelRoles.advisor` in `/Users/androidteam/.omp/agent/config.yml` (`mode 0600`) to `google-antigravity/gemini-3.8-flash:high` with `retry.fallbackChains.advisor: [omniroute/gemini-3.8-flash-high:high, google-antigravity/gemini-4-argon:high]`, and verify a multi-turn `read` tool + advisor `omp -p` session exits `0` (`rc=0`, `advisor_entries=7`, `omniroute_memory_injections=0`).
- [x] 1.3 Update `/Users/androidteam/Developer/wiki/entities/omp.md` and sync Notion (`sync-notion-knowledge.sh --section entities` and `--section specs`).

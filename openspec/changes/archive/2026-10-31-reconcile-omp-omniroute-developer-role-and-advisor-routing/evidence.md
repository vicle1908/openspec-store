# Verification Evidence: `reconcile-omp-omniroute-developer-role-and-advisor-routing`

- **`models.yml` (`Task 1.1`)**:
  - Updated `providers.omniroute.compat` to `{ supportsReasoningEffort: true, supportsDeveloperRole: false }` (`mode 0600`).
  - `omp models --json` verified `thinking: ["low", "medium", "high"]` on all 5 `omniroute/*gemini-4-argon*` models.
  - Single-turn `omp --session-dir /tmp/omp-adv-fixed2 --no-prewalk --no-skills --no-tools --mode json -p "reply only: pong"` exited `rc=0` in `24.93s`; `__advisor.jsonl` recorded `input: 2050, cacheRead: 18559, output: 51` (`**SILENT**`) confirming `systemInstruction` was preserved on OmniRoute.
- **`config.yml` (`Task 1.2`)**:
  - Updated `modelRoles.advisor` to `google-antigravity/gemini-3.8-flash:high` and `retry.fallbackChains.advisor` to `['omniroute/gemini-3.8-flash-high:high', 'google-antigravity/gemini-4-argon:high']` (`mode 0600`).
  - Multi-turn tool + advisor E2E session (`Use the read tool to read /Users/androidteam/.omp/agent/lsp.json and reply with the exact python.version value.`) exited `rc=0` in `49.73s` with final reply `` `3.15` ``, `advisor_entries=7` (both Turn 1 `advise` and Turn 2 review completed cleanly), and `omniroute_memory_injections=0`.

# ECC Harness Alignment — Tasks

Total estimate: **~12 hours**, fits comfortably in 2 sessions. Each chunk is 10 min – 3 h.

## §1 Discovery (~95 min)

- [x] **1.1** Enumerate all 262 ECC skills into a CSV (name, description, category). ~30 min
  - Source: `~/.claude/plugins/cache/everything-claude-code/ecc/2.0.0/skills/`
  - Output: `audit/raw-skills.csv` (263 lines = 1 header + 262 skills)
- [x] **1.2** Enumerate 84 commands into a CSV. ~15 min
  - Source: `~/.claude/plugins/cache/everything-claude-code/ecc/2.0.0/commands/`
  - Output: `audit/raw-commands.csv` (85 lines = 1 header + 84 commands)
- [x] **1.3** Enumerate 64 agents into a CSV (language, tags). ~15 min
  - Source: `~/.claude/plugins/cache/everything-claude-code/ecc/2.0.0/agents/`
  - Output: `audit/raw-agents.csv` (65 lines = 1 header + 64 agents)
- [x] **1.4** Enumerate hooks from `hooks/hooks.json` + parse the disabled-by-default list. ~15 min
  - Source: `~/.claude/plugins/cache/everything-claude-code/ecc/2.0.0/hooks/hooks.json`
  - Output: `audit/raw-hooks.csv` (19 lines = 1 header + 18 hooks; spec said 30+ but actual is 18)
- [x] **1.5** Enumerate rules dirs and classify by language. ~10 min
  - Source: `~/.claude/plugins/cache/everything-claude-code/ecc/2.0.0/rules/`
  - Output: `audit/raw-rules.csv` (20 lines = 1 header + 19 dirs; spec said 22 but actual is 19)
- [x] **1.6** Diff marketplace clone vs installed ECC; capture SHA to `marketplace-baseline.txt`. ~10 min
  - Source: `~/.claude/plugins/marketplaces/ecc` (`git rev-parse HEAD`)
  - Output: `audit/marketplace-baseline.txt` (marketplace SHA: ec92b528471df708c2384ebbcc82b390b60f535a; installed version: 2.0.0)

## §2 Static-diff classification (Phase 1 of playbook) (~285 min)

- [x] **2.1** For each skill: apply the 4-question rubric, mark classification, link TDT equivalent if any. ~2 h
  - Output: `audit/skills-disposition.md`
  - Result: 4 redundant-to-tdt-skill, 16 keep-optional, 44 disabled-default:stack-irrelevant, 32 disabled-default:domain-irrelevant, 166 investigate (resolved in §3)
- [x] **2.2** Same for commands. ~1 h
  - Output: `audit/commands-disposition.md`
  - Result: 4 redundant-to-tdt-skill, 80 keep-optional
- [x] **2.3** Same for agents, using language-bucket logic. ~45 min
  - Output: `audit/agents-disposition.md`
  - Result: 50 keep-default, 4 keep-optional, 8 disabled-default:domain-irrelevant, 2 disabled-default:stack-irrelevant
- [x] **2.4** Same for hooks, producing canonical `ECC_DISABLED_HOOKS` value. ~30 min
  - Output: `audit/hooks-policy.md` with canonical string at the top
  - Result: 15 disabled-default, 2 coexist, 1 keep-default, 0 investigate
  - Canonical value: `post:bash:dispatcher,post:ecc-context-monitor,post:ecc-metrics-bridge,post:edit:accumulator,post:edit:console-warn,post:edit:design-quality-check,post:mcp-health-check,post:session-activity-tracker,pre:bash:dispatcher,session:end:marker,stop:check-console-log,stop:cost-tracker,stop:desktop-notify,stop:format-typecheck,stop:session-end`
- [x] **2.5** Same for rules dirs. ~15 min
  - Output: `audit/rules-policy.md`
  - Result: 5 surface (python, swift, kotlin, typescript, react), 1 surface:common, 13 disabled-default:stack-irrelevant

## §3 Usage-evidence pass (Phase 2 of playbook) (~105 min + variable)

- [x] **3.1** Grep `cost-tracker.log` and `~/.claude/projects/` sessions for every `investigate` entry. ~1 h
  - Tool: `rg` on session JSONL files for skill/command/agent names
  - Result: 4 skills had real `tool_use Skill` invocations (design-system 222x, dotnet-patterns 7x, security-review 6x, git-workflow 3x); 162 had zero real invocations (most prior hits were false positives from skill listings in system prompt)
- [x] **3.2** For new-since-last-audit entries: 2-day trial or description-only classification. varies
  - Marketplace HEAD SHA `ec92b52...` only contains sponsor docs change; no new skills/commands/agents/hooks since v2.0.0 install
- [x] **3.3** Resolve all `investigate` entries to one of the final classifications. ~30 min
  - Final disposition table has zero `investigate` rows
  - 4 with hits → keep-optional; 23 general-utility → keep-optional; 139 zero-hit → disabled-default:no-evidence

## §4 Adoption decisions (Phase 3) (~105 min)

- [x] **4.1** List candidate v2.0 features worth adopting. ~30 min
  - Candidates evaluated: orch-build-mvp, orch-pipeline, hookify-rules, context-budget, strategic-compact, verification-loop, repo-scan, skill-stocktake, ecc-tools-cost-audit, continuous-learning-v2, healthcare-reviewer, loop, babysit
- [x] **4.2** For each, write a 1-paragraph integration plan. ~1 h
  - Output: `audit/adoption.md`
  - 11 keep-optional, 2 redundant-to-tdt-skill (hookify-rules, continuous-learning-v2)
- [x] **4.3** Decide version-pin policy. ~15 min
  - Decision: Pin v2.0.0 with quarterly review
  - Rationale: Prevents silent surface area expansion; next review due 2026-09-27
  - autoUpdate will be set to false in Task 6.2
- [x] **4.4** For each `orch-*` skill, decide adoption status. ~15 min
  - Result: All 6 orch-* skills promoted to keep-optional (orch-add-feature, orch-build-mvp, orch-change-feature, orch-fix-defect, orch-pipeline, orch-refine-code)

## §5 Author OpenSpec artifacts (~285 min)

- [x] **5.1** Write `proposal.md` + `design.md`. ~1 h (already drafted in this change)
- [x] **5.2** Write the seven `specs/*.md` files. ~3 h
  - All 7 specs written with `## ADDED Requirements` headers; validated with `openspec validate --strict` → "is valid"
- [x] **5.3** Write `tasks.md` from this section. ~30 min (this file)
- [x] **5.4** Copy the `audit/` CSV snapshots into the change dir. ~15 min
  - All 5 raw CSVs in `audit/` (raw-skills, raw-commands, raw-agents, raw-hooks, raw-rules)
  - All 5 disposition markdown files in `audit/` (skills, commands, agents, hooks, rules)
  - Plus `adoption.md`, `marketplace-baseline.txt`, `session-hits.json`

## §6 Apply (settings + scripts) (~45 min)

- [x] **6.1** Backup `~/.claude/settings.json` (`settings.json.bak`) then update `ECC_DISABLED_HOOKS` to canonical value. ~10 min
  - Backup created at `~/.claude/settings.json.bak`
  - Updated: 15 hooks disabled (was 14 stale hooks from prior version)
- [x] **6.2** If version-pin decision flipped: update `extraKnownMarketplaces.everything-claude-code.autoUpdate`. ~5 min
  - Old: `autoUpdate: true`
  - New: `autoUpdate: false` (pin v2.0.0 with quarterly review)
- [x] **6.3** Run `/opsx:verify` — fix any spec gaps. ~30 min
  - `openspec validate ecc-harness-alignment --strict` → "Change is valid"

## §7 Document the playbook (~40 min)

- [x] **7.1** Move the methodology into `tdt-meta/docs/ecc-harness/playbook.md`. ~30 min
  - This is the durable artifact; future ECC releases run this playbook end-to-end
  - Includes classification enum, TDT repo language map, TDT overlay priorities, audit log
- [x] **7.2** Cross-link from `tdt-meta/AGENTS.md` "Skills" section. ~10 min
  - Added "ECC Harness Alignment" section between Skills and OpenSpec

## §8 Archive (~15 min)

- [x] **8.1** `/opsx:archive` the change. ~5 min
- [x] **8.2** Add a "How to run the next audit" note to the change's archived body. ~10 min
  - Pointer to `docs/ecc-harness/playbook.md`
  - Reminder to update `audit/marketplace-baseline.txt` on next audit

## Verification

After §6.3 and §8.1, run these checks:

- [x] All `disabled-default` hook entries in canonical `ECC_DISABLED_HOOKS` string match `~/.claude/settings.json` value
- [x] All `redundant-to-tdt-skill:<x>` entries point to real files under `tdt-meta/.agents/skills/`
  - 4 redundant entries: scrape, exa-cli, jira-integration, handoff — all verified present
- [x] Zero `investigate` rows in final disposition tables
- [x] `/opsx:verify` passes
- [x] `docs/ecc-harness/playbook.md` exists and references this OpenSpec change
- [x] `audit/marketplace-baseline.txt` matches `~/.claude/plugins/marketplaces/ecc` HEAD
  - Both: `ec92b528471df708c2384ebbcc82b390b60f535a`
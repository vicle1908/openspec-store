# Jira-GitLab Integration v3.0.0 — Spec Alignment Synthesis

**Date:** 2026-05-15T12:00:00Z  
**Reviewers:** 4 parallel review agents  
**Reports analyzed:**

- `openspec/reports/review-jira-daily-reports-overlap.md`
- `openspec/reports/review-kanban-board-overlap.md`
- `openspec/reports/review-enhance-acli-overlap.md`
- `webhook-receiver/docs/specs/mr-re-review-system-spec.md` (ai-review-system)
- `openspec/changes/ai-review-system/design.md`

---

## Executive Summary

**7 existing OpenSpec changes** were analyzed for overlaps with `jira-gitlab-integration-v3`. Of 6 implementation phases, **5 have pre-existing work** in other specs that makes naive re-implementation wasteful or destructive.

| Phase   | Topic                     | Overlap Status                                                  | Action Required                   |
| ------- | ------------------------- | --------------------------------------------------------------- | --------------------------------- |
| Phase 1 | Documentation             | ✅ Complete                                                     | None                              |
| Phase 2 | Automation Rules          | ✅ No overlap                                                   | Proceed as-is                     |
| Phase 3 | Sprint Reports            | ❌ **DUPLICATE** jira-daily-reports-skill                       | Rewrite as deployment + reference |
| Phase 4 | GitLab for Jira Cloud App | ✅ No overlap                                                   | Proceed as-is                     |
| Phase 5 | Cross-Project Boards      | ❌ **DUPLICATE** kanban-board-from-spreadsheet                  | Rewrite as integration layer      |
| Phase 6 | MR Re-Review              | ❌ **ALREADY IMPLEMENTED** in ai-review-system/webhook-receiver | Mark complete, document reference |

---

## Detailed Findings

### Phase 2: Automation Rules — ✅ No Overlap

**Review:** enhance-acli-skill  
**Verdict:** Clean separation

`enhance-acli-skill` modifies `.agents/skills/acli/` (CLI reference, flag tables). `jira-gitlab-integration-v3` Phase 2 configures **Jira Automation rules** (UI-based, no CLI). Different tools, different directories, different purposes.

**No changes needed.** Proceed as-is.

---

### Phase 3: Sprint Reports — ❌ DUPLICATE with jira-daily-reports-skill

**Review:** jira-daily-reports-overlap  
**Verdict:** Phase 3 tasks 3.1-3.3 would be 100% duplicative

The `jira-daily-reports-skill` is already **fully implemented and development-ready** (v1.1, 9 report scripts, cron configs, email/Slack patterns; now archived at `openspec/changes/archive/jira-daily-reports-skill/`). Phase 3 proposes re-creating the same thing.

**Conflicts found:**

1. **JQL scope mismatch** — `jira-daily-reports` uses `filter = 15113`; Best Practices Guide uses `project in (11 projects) AND sprint in openSprints()`. Results differ.
2. **Report count mismatch** — Best Practices Guide only documents 4 of 9 reports.
3. **Phase 3 tasks 3.1-3.3** fully duplicate existing jira-daily-reports setup.

**Action:**

- Rewrite Phase 3 tasks as deployment references to jira-daily-reports
- Add scope note in Best Practices Guide §8
- Add full report-to-script mapping table

---

### Phase 4: GitLab for Jira Cloud App — ✅ No Overlap

**Review:** All reports  
**Verdict:** Clean — no other spec covers this

No existing spec addresses OAuth setup, Marketplace installation, or Cloud App configuration.

**No changes needed.** Proceed as-is.

---

### Phase 5: Cross-Project Boards — ❌ DUPLICATE with kanban-board-from-spreadsheet

**Review:** kanban-board-overlap  
**Verdict:** Phase 5 would be 100% duplicative or worse (destructive)

The `kanban-board-from-spreadsheet` spec already has a **production-ready cross-project board** (Board #1067, Filter #15113) with a documented **MULTI_SPACE_ARCHITECTURE** model.

**Critical conflicts:**

1. **JQL strategy mismatch** — kanban-board uses `key in (...)` (exact match, ~65 issues); Phase 5 proposes `project in (...)` (would show ~5,376 issues — 80x too many)
2. **Board #1067 already exists** — creating another board creates infrastructure sprawl
3. **Filter #15113 already exists** — creating another filter creates dual scope definitions
4. **MULTI_SPACE_ARCHITECTURE model** — Phase 5 is unaware of the space registry, switching functions, and configuration model

**Action:**

- Rewrite Phase 5 as a thin integration layer (0.5 days)
- Reference Filter #15113 and Board #1067
- Adopt `key in (...)` JQL pattern
- Integrate with MULTI_SPACE_ARCHITECTURE.md

---

### Phase 6: MR Re-Review System — ❌ ALREADY IMPLEMENTED

**Review:** ai-review-system design + mr-re-review-system-spec.md  
**Verdict:** Already completed (v2.1, 304/304 tests, 95/100 validation)

The MR re-review system is **fully implemented** in `webhook-receiver/`:

- ✅ Review on MR updates
- ✅ Update existing review comment
- ✅ 30-second debounce
- ✅ Smart skip conditions (drafts, docs-only, trivial changes)
- ✅ Cost increase: +50% (with optimizations), not the target +40%
- ✅ 304/304 tests passing
- ✅ Validation score: 95/100

**Action:**

- Mark Phase 6 as complete in tasks.md
- Add reference to `webhook-receiver/docs/specs/mr-re-review-system-spec.md`
- No implementation needed

---

## Files Requiring Updates

### High Priority (Fix Now)

1. **`openspec/changes/jira-gitlab-integration-v3/tasks.md`**
   - Phase 3: Rewrite tasks 3.1-3.3 as deployment references to jira-daily-reports
   - Phase 5: Rewrite all tasks as integration layer referencing existing Board #1067/Filter #15113
   - Phase 6: Mark all tasks as complete with reference to mr-re-review-system-spec.md

2. **`openspec/changes/jira-gitlab-integration-v3/spec.md`**
   - Phase 3: Update to say "deploy existing jira-daily-reports skill"
   - Phase 5: Update to reference Board #1067, Filter #15113, key-in JQL
   - Phase 6: Update to reference existing mr-re-review implementation
   - Add cross-references to related specs in dependencies section

3. **`openspec/changes/jira-gitlab-integration-v3/design.md`**
   - Phase 5: Add reference to kanban-board-from-spreadsheet and MULTI_SPACE_ARCHITECTURE.md

### Medium Priority (Documentation Fixes)

4. **`docs/jira-gitlab-integration/JIRA-GITLAB-AGILE-BEST-PRACTICES.md` (§8)**
   - Add scope note: "Automated reports use filter #15113"
   - Add full 9-report mapping table with script paths

### Low Priority (Cross-References)

5. **`.agents/skills/jira-integration/SKILL.md`**
   - Add cross-reference to kanban-board-from-spreadsheet skill
   - Reference acli commands docs in enhance-acli-skill (already done)

6. **`openspec/changes/archive/kanban-board-from-spreadsheet/MULTI_SPACE_ARCHITECTURE.md`**
   - Ensure all 11 projects from jira-gitlab-integration-v3 are registered

---

## Dependency Graph

```
jira-gitlab-integration-v3
├── Phase 1 (Documentation)       ← self-contained ✅
├── Phase 2 (Automation Rules)    ← self-contained ✅
├── Phase 3 (Sprint Reports)      ← depends on jira-daily-reports-skill ⚠️
├── Phase 4 (Cloud App)           ← self-contained ✅
├── Phase 5 (Cross-Project Boards)← depends on kanban-board-from-spreadsheet ⚠️
├── Phase 6 (MR Re-Review)        ← depends on ai-review-system ⚠️
└── Skill: acli                   ← references enhance-acli-skill ✅

Related specs (not direct deps):
└── ops-automation-suite           ← single proposal.md, not yet active
```

---

## Next Steps

1. Apply high-priority fixes to tasks.md, spec.md, design.md
2. Apply medium-priority doc fixes to Best Practices Guide
3. Apply low-priority cross-references
4. Run `openspec status --change "jira-gitlab-integration-v3" --json` to verify
5. Archive if all phases ready

---

**Status:** ✅ Analysis complete — 5 of 6 phases reviewed  
**Ready for:** Spec updates to eliminate duplication

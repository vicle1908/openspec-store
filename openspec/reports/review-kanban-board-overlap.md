# Review: kanban-board-from-spreadsheet vs jira-gitlab-integration-v3 Phase 5 Overlap

**Date:** 2026-05-15  
**Reviewer:** Review subagent  
**Source files reviewed:**

- `openspec/changes/archive/kanban-board-from-spreadsheet/spec.md`
- `openspec/changes/archive/kanban-board-from-spreadsheet/design.md`
- `openspec/changes/archive/kanban-board-from-spreadsheet/MULTI_SPACE_ARCHITECTURE.md`
- `openspec/changes/archive/kanban-board-from-spreadsheet/FEATURES_AND_DEPENDENCIES.md`
- `openspec/changes/jira-gitlab-integration-v3/spec.md`
- `openspec/changes/jira-gitlab-integration-v3/design.md`

---

## 1. What Already Exists That Overlaps With Phase 5

**kanban-board-from-spreadsheet** is already **production-ready** (v1.3, 2026-05-12) and includes every task that Phase 5 proposes:

| Phase 5 Task                               | Already Found In                                    | Evidence                                                                      |
| ------------------------------------------ | --------------------------------------------------- | ----------------------------------------------------------------------------- |
| Create cross-project Jira board            | spec.md §4 — Board #1067                            | Permanent infrastructure, created via `acli jira board create` in PUB project |
| Configure JQL filter for all 11 projects   | spec.md §3 — Filter #15113                          | Uses exact `key in (...)` JQL spanning 10+ projects                           |
| Configure columns for workflow states      | design.md — Decision 9 & spec.md §6                 | Columns: To do, In Progress, Code Review, SIT, Test Done, Done                |
| Add filters for platform (iOS/Android/API) | spec.md §4 — Decision 6                             | Quick-filters by Side column (iOS, AOS, iOS/AOS) documented                   |
| Set up sprint planning view                | spec.md §5 — 8-step workflow                        | Full spreadsheet-to-board pipeline, Pre/Mid/End-Sprint lifecycle              |
| Train team on board usage                  | SKILL.md (708 lines) & FEATURES_AND_DEPENDENCIES.md | Complete documentation with usage patterns, CLI examples                      |

Additionally, `MULTI_SPACE_ARCHITECTURE.md` defines a comprehensive **combined+source** space model with:

- 2 space types: `combined` (PUB) and `source` (SR, RMD, etc.)
- 8 Jira projects fully mapped with filter IDs and board IDs
- Space-switching functions (`jira_space()`, `jira_spaces_list()`)
- Configuration model with precedence rules and backward compatibility
- 4 usage patterns including multi-space workflows

## 2. What Would Be DUPLICATED

If Phase 5 is executed without awareness of kanban-board-from-spreadsheet, the following would be **full or partial duplicates**:

1. **Cross-project board creation** — Board #1067 already exists. Creating another board doubles infrastructure without adding value.
2. **JQL filter configuration** — Filter #15113 already covers all projects. A second filter would create two competing scope definitions.
3. **Column mapping** — Already configured in Board #1067. Repeating is wasted effort.
4. **Platform quick-filters** — Already documented in kanban-board-from-spreadsheet design.md (Decision 6).
5. **Sprint planning integration** — Already fully implemented as the 8-step workflow.

**Estimated waste:** 1–2 days of effort (the full Phase 5 duration estimate).

## 3. Shared Jira Project Filtering, JQL Patterns, Board Configs

Both changes reference the same Jira instance and projects:

| Element                   | kanban-board-from-spreadsheet                    | jira-gitlab-integration-v3                              |
| ------------------------- | ------------------------------------------------ | ------------------------------------------------------- |
| **Jira instance**         | psplit.atlassian.net                             | psplit.atlassian.net                                    |
| **Projects**              | SR, RMD, PWM, FUN, COM, AU, AM, STABI + TJ, P3AP | 11 projects (includes TJ, P3AP)                         |
| **Projects with sprints** | Only P3AP and RMD (spec.md §3 — Decision 10)     | Documented via Sprint-Based Development workflow        |
| **JQL strategy**          | Exact `key in (...)` — proven approach           | Phase 5 proposes `project in (...)` with sprint clauses |
| **Board type**            | Kanban (spec.md §1.2)                            | Kanban (implied by Cross-Project Boards label)          |
| **Host project**          | PUB (classic/company-managed)                    | Not specified                                           |
| **Filter ID**             | #15113 (permanent)                               | Not specified                                           |
| **Board ID**              | #1067 (permanent)                                | Not specified                                           |

## 4. Conflicts in Project Catalogs, Filter IDs, or Board Strategies

### Conflict 1: JQL Strategy — `key in (...)` vs `project in (...)`

**Critical.** kanban-board-from-spreadsheet spec.md §3 (Decision 10) explicitly documents why `project in (...)` was rejected:

> _"Only 2 of 10 projects have sprints. `sprint=` clause would exclude 8 projects. Time-based filtering (`status != Done OR updated >= -14d`) showed **5,376 issues vs 65 planned**. Exact key matching ensures the board shows ONLY planned issues."_

jira-gitlab-integration-v3 Phase 5 tasks say: _"Configure JQL filter for all 11 projects"_ — which implies `project in (SR,RMD,...)`. If implemented, this would create a board showing thousands of unplanned issues, directly contradicting the proven approach.

**Recommendation:** Phase 5 must adopt `key in (...)` matching instead of `project in (...)`.

### Conflict 2: Filter/Board IDs Not Specified in Phase 5

jira-gitlab-integration-v3 Phase 5 does not specify filter or board IDs. This creates a risk of:

- Creating additional filters alongside #15113 (infrastructure sprawl)
- Creating additional boards alongside #1067 (context switching)
- Two boards showing different issue sets for the same purpose

**Recommendation:** Phase 5 must reference Filter #15113 and Board #1067 as existing infrastructure, not create new ones.

### Conflict 3: MULTI_SPACE_ARCHITECTURE.md Space Model

kanban-board-from-spreadsheet's `MULTI_SPACE_ARCHITECTURE.md` defines a **space registry** and **switching functions** that jira-gitlab-integration-v3 is not aware of. The architecture includes:

```
PUB_SPACE_TYPE="combined"
PUB_FILTER_ID="15113"
PUB_BOARD_ID="1067"
PUB_SOURCE_PROJECTS="SR,RMD,PWM,FUN,COM,AU,AM,STABI"
```

Phase 5 does not reference or integrate with this model. Without alignment, Phase 5 would create a parallel space concept with different conventions.

**Recommendation:** Phase 5 should adopt and extend the MULTI_SPACE_ARCHITECTURE.md model rather than defining its own.

### Conflict 4: Project Count Discrepancy

- kanban-board-from-spreadsheet explicitly lists **10 projects**: SR, RMD, PWM, FUN, COM, AU, AM, STABI, TJ, P3AP
- jira-gitlab-integration-v3 references **11 projects** but never lists all 11 explicitly

The missing/mismatched project needs clarification to avoid boards with incomplete scope.

## 5. Recommendations for Alignment

### 5.1 Phase 5 Should Become a Thin Integration Layer

Instead of "Create cross-project Jira board" (which already exists), Phase 5 should be re-scoped to:

1. **Adopt kanban-board-from-spreadsheet as the cross-project board foundation** — Reference Filter #15113, Board #1067, and the MULTI_SPACE_ARCHITECTURE.md model.
2. **Extend the GitLab → Jira integration to recognize the existing board** — Document how Smart Commits, MR linking, and pipeline visibility flow into the existing cross-project board.
3. **Document the complete workflow** — Show how a developer goes from GitLab commit (Smart Commit) → issue updated on Board #1067 → visible to all teams.
4. **Verify the 11th project** — Ensure all 11 Jira projects from jira-gitlab-integration-v3 are included in the space registry.

### 5.2 Specific Fixes Needed in jira-gitlab-integration-v3

| File        | Section                        | Fix                                                                                            |
| ----------- | ------------------------------ | ---------------------------------------------------------------------------------------------- |
| `spec.md`   | Phase 5 — Cross-Project Boards | Replace "Create cross-project Jira board" with "Adopt existing Board #1067 / Filter #15113"    |
| `spec.md`   | Phase 5 tasks                  | Replace generic JQL with `key in (...)` pattern from kanban-board-from-spreadsheet Decision 10 |
| `design.md` | Phase 5 section                | Add reference to MULTI_SPACE_ARCHITECTURE.md, space registry, and `jira_space()` functions     |
| `spec.md`   | Appendix                       | Add cross-reference to `openspec/changes/archive/kanban-board-from-spreadsheet/` as prerequisite       |

### 5.3 Updated Phase 5 Task List (Recommended)

```
Phase 5: Cross-Project Boards (Already Implemented — Integration Layer Only)

Duration: 0.5 day (documentation + verification only)
Effort: Low
Status: Not started

Tasks:
1. Verify existing Board #1067 covers all 11 Jira projects from v3.0.0
2. Document how Smart Commits/MR linking feed into Board #1067
3. Add cross-reference in jira-integration SKILL.md pointing to kanban-board-from-spreadsheet skill
4. Ensure MULTI_SPACE_ARCHITECTURE.md includes all 11 projects in the space registry
5. Test end-to-end: GitLab commit → issue appears on Board #1067

Expected Impact:
- Zero new infrastructure
- Complete traceability from commit to cross-project board visibility
```

### 5.4 Files That Need Cross-Referencing

- `openspec/changes/jira-gitlab-integration-v3/spec.md` → add prerequisite section linking to kanban-board-from-spreadsheet
- `openspec/changes/jira-gitlab-integration-v3/design.md` → update Phase 5 to reference existing board infrastructure
- `.agents/skills/jira-integration/SKILL.md` → add cross-ref to `.agents/skills/kanban-board-from-spreadsheet/SKILL.md`
- `openspec/changes/archive/kanban-board-from-spreadsheet/MULTI_SPACE_ARCHITECTURE.md` → ensure all 11 projects from v3.0.0 are registered

---

## Summary

| Item                                                         | Severity         | Status                                                          |
| ------------------------------------------------------------ | ---------------- | --------------------------------------------------------------- |
| Cross-project board already exists (Board #1067)             | **Conflict**     | Requires Phase 5 to adopt, not recreate                         |
| JQL strategy mismatch (`key in (...)` vs `project in (...)`) | **Critical**     | Phase 5 must adopt exact-key approach or board shows 5K+ issues |
| Filter/board IDs unspecified in Phase 5                      | **Risk**         | Without IDs, Phase 5 creates duplicate infrastructure           |
| MULTI_SPACE_ARCHITECTURE model unknown to Phase 5            | **Risk**         | Two parallel space models would diverge                         |
| Project count mismatch (10 vs 11)                            | **Note**         | Clarify and reconcile                                           |
| Agile metrics (WIP, throughput, CFD) built in kanban-board   | **Already Done** | Phase 5 can consume directly                                    |

**Bottom line:** Phase 5 should be reduced from a 1-2 day implementation to a 0.5 day **integration layer** that connects jira-gitlab-integration-v3 documentation to the existing kanban-board-from-spreadsheet infrastructure. Creating new boards or filters would be purely duplicative.

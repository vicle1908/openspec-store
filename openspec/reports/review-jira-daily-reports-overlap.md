# Review: jira-daily-reports-skill ↔ jira-gitlab-integration-v3 Phase 3

**Reviewer:** Review subagent  
**Date:** 2026-05-15  
**Files examined:**

- `openspec/changes/archive/jira-daily-reports-skill/spec.md` (v1.1)
- `openspec/changes/archive/jira-daily-reports-skill/design.md`
- `openspec/changes/archive/jira-daily-reports-skill/tasks.md`
- `openspec/changes/jira-gitlab-integration-v3/spec.md` (v3.0.0)
- `openspec/changes/jira-gitlab-integration-v3/design.md`
- `openspec/changes/jira-gitlab-integration-v3/tasks.md`
- `docs/jira-gitlab-integration/JIRA-GITLAB-AGILE-BEST-PRACTICES.md` (§8 Metrics and Reporting)

---

## 1. What Already Exists in jira-daily-reports-skill that Overlaps with Phase 3

The `jira-daily-reports-skill` is a **fully implemented, development-ready** skill (all tasks marked `[x] complete`). It covers everything Phase 3 of `jira-gitlab-integration-v3` intends to deliver:

| Capability                      | jira-daily-reports-skill            | Phase 3 asks for                      |
| ------------------------------- | ----------------------------------- | ------------------------------------- |
| 9 report types                  | ✅ Scripts built & tested for all 9 | ✅ Same 9 reports                     |
| Daily Standup (8 AM)            | ✅ Script complete, cron-ready      | ✅ Same                               |
| Blocked Items (9 AM)            | ✅ Script complete, cron-ready      | ✅ Same                               |
| WIP Per Person (5 PM)           | ✅ Script complete, cron-ready      | ✅ Same                               |
| Completion Velocity (10 AM)     | ✅ Script complete, cron-ready      | ✅ Same                               |
| Platform Distribution (10 AM)   | ✅ Script complete, cron-ready      | ✅ Same                               |
| Priority Distribution (10 AM)   | ✅ Script complete, cron-ready      | ✅ Same                               |
| Code Review Bottleneck (2 PM)   | ✅ Script complete, cron-ready      | ✅ Same                               |
| Sprint Health Dashboard (10 AM) | ✅ Script complete, cron-ready      | ✅ Same                               |
| Missing Info Report (8:30 AM)   | ✅ Script complete (v1.1)           | Not listed but implied by "9 reports" |
| Email delivery                  | ✅ Pattern documented               | ✅ Required                           |
| Slack delivery                  | ✅ Pattern documented               | ✅ Required                           |
| Cron automation                 | ✅ Schedule examples documented     | ✅ Required                           |
| Bash + acli implementation      | ✅ All scripts use acli + JQL       | ✅ Same tech stack                    |

**Key evidence:**

- `jira-daily-reports-skill/tasks.md` tasks 2-9: All 9 report scripts implemented and tested
- `jira-daily-reports-skill/tasks.md` task 10: Automation setup (cron, email, Slack) documented
- `jira-daily-reports-skill/spec.md` §6.5: Cron schedule examples
- `jira-daily-reports-skill/spec.md` §7.1-7.3: Email/Slack/file delivery patterns

---

## 2. What Would Be DUPLICATED if Phase 3 Is Implemented

**Phase 3 tasks from `jira-gitlab-integration-v3/tasks.md`:**

| Phase 3 Task                           | Status in jira-daily-reports-skill                                     | Verdict             |
| -------------------------------------- | ---------------------------------------------------------------------- | ------------------- |
| 3.1: Configure cron jobs for 9 reports | ✅ Already documented in `references/automation-setup.md` & `SKILL.md` | **DUPLICATION**     |
| 3.2: Set up email delivery             | ✅ Pattern already in `spec.md` §7.1                                   | **DUPLICATION**     |
| 3.3: Set up Slack delivery             | ✅ Pattern already in `spec.md` §7.2                                   | **DUPLICATION**     |
| 3.4: Train team on reports             | ⚠️ Not documented yet                                                  | Legitimate new work |

If Phase 3 tasks 3.1-3.3 are implemented as written, they would **re-implement** what jira-daily-reports-skill already provides. The only non-duplicative work is training (task 3.4).

**The design.md of jira-gitlab-integration-v3 itself acknowledges this:**

> Phase 3: Sprint Reports — **Status: Not started (skill already exists)**

This confirms the implementer knows the skill exists but still lists these as tasks — which risks duplicate effort.

---

## 3. What Should Be REFERENCED from jira-daily-reports into jira-gitlab-integration-v3

### 3.1 Replace Phase 3 Tasks with References

Instead of re-describing cron/email/Slack setup, Phase 3 should **reference** the existing skill documentation:

**Recommended rewrite of Phase 3 tasks:**

```
Task 3.1: Deploy jira-daily-reports skill
- REFERENCE: `.agents/skills/jira-daily-reports/references/automation-setup.md`
- REFERENCE: `.agents/skills/jira-daily-reports/SKILL.md` → "Quick Start" section
- Action: Copy scripts to server, set executable permissions
- Action: Configure crontab entries (examples in automation-setup.md)

Task 3.2: Configure email delivery
- REFERENCE: `openspec/changes/archive/jira-daily-reports-skill/spec.md` §7.1
- Action: Set SMTP_* env vars in ~/.tdt/.env
- Action: Test with daily_standup_report.sh

Task 3.3: Configure Slack delivery
- REFERENCE: `openspec/changes/archive/jira-daily-reports-skill/spec.md` §7.2
- Action: Set SLACK_WEBHOOK_URL in ~/.tdt/.env
- Action: Test with sprint_health_dashboard.sh

Task 3.4: Train team
- (Keep as-is — unique work)
```

### 3.2 Fix Scope Mismatch in JQL Queries

The **Agile Best Practices Guide** (`JIRA-GITLAB-AGILE-BEST-PRACTICES.md`, §8) defines **different JQL** for reports:

**Best Practices Guide JQL (cross-project):**

```jql
project in ($JIRA_PROJECTS)
AND sprint in openSprints()
AND updated >= -1d
```

**jira-daily-reports JQL (filter-based):**

```jql
filter = 15113 AND updated >= -1d
```

These produce **different results** because:

- `filter = 15113` is a fixed, known scope (Sprint 14, 65 issues across 10 projects)
- `project in (...) AND sprint in openSprints()` is dynamic — it picks up whatever sprint is active per project

**Recommendation:** The Best Practices Guide should either:

1. Add a note that the JQL examples there are for **manual/ad-hoc** queries, not the automated reports
2. Or explicitly reference jira-daily-reports: _"For automated daily reports, see the [jira-daily-reports skill](../.agents/skills/jira-daily-reports/SKILL.md) which uses filter #15113"_

### 3.3 Cross-Reference Already Exists (Good)

The Best Practices Guide already links to jira-daily-reports:

```
### Skills
- [jira-daily-reports skill](./.agents/skills/jira-daily-reports/SKILL.md)
```

This is correct. Phase 3 just needs to operationalize this reference.

---

## 4. Conflicts

### Conflict A: Filter #15113 vs Cross-Project JQL

| Aspect           | jira-daily-reports                  | Best Practices Guide (§8)                              |
| ---------------- | ----------------------------------- | ------------------------------------------------------ |
| Scope mechanism  | `filter = 15113`                    | `project in (11 projects) AND sprint in openSprints()` |
| Scope controller | Filter owner updates JQL            | Runtime-computed per sprint                            |
| Portability      | Tied to filter ID 15113             | Works for any sprint/project                           |
| Performance      | Faster (pre-computed filter)        | Slower (complex JQL)                                   |
| Consistency      | ✅ Guaranteed same scope everywhere | ❌ May vary if sprint assignments differ               |

**Impact:** A team member running a manual JQL query from the Best Practices Guide could get different counts than the automated daily report. This undermines trust.

**Suggested fix:** Add a note in the Best Practices Guide §8:

> ⚠️ Automated daily reports use `filter = 15113` for consistency. The JQL below is for manual/ad-hoc queries only.

### Conflict B: Report Count Mismatch

| Source                  | Report Count     | Details                                             |
| ----------------------- | ---------------- | --------------------------------------------------- |
| jira-daily-reports v1.0 | 8 reports        | No Missing Information Report                       |
| jira-daily-reports v1.1 | 9 reports        | Added Missing Information Report                    |
| Phase 3 spec            | "9 report types" | Matches v1.1 ✅                                     |
| Phase 3 tasks           | "9 reports"      | Matches v1.1 ✅                                     |
| Best Practices Guide §8 | 4 JQL examples   | Only shows Standup, Blocked, CR, Health — not all 9 |

**Impact:** The Best Practices Guide defines only 4 of the 9 reports. If someone reads just the guide, they won't know about WIP Per Person, Completion Velocity, Platform Distribution, Priority Distribution, or Missing Information reports.

**Suggested fix:** Add a table in §8 linking each report to the jira-daily-reports skill:

> | Report        | JQL (if manual) | Automated Script                                                    |
> | ------------- | --------------- | ------------------------------------------------------------------- |
> | Daily Standup | `...`           | `.agents/skills/jira-daily-reports/scripts/daily_standup_report.sh` |
> | Blocked Items | `...`           | `.../scripts/blocked_items_report.sh`                               |
> | ...           | ...             | ...                                                                 |

### Conflict C: No Shared Filter ID Configuration

jira-daily-reports hardcodes `FILTER_ID="${JIRA_FILTER_ID:-15113}"`. The Best Practices Guide uses inline project lists. If filter #15113 changes scope, the Best Practices Guide JQL examples become outdated.

**Risk:** Low — filter changes require coordinated updates anyway. But worth documenting that filter #15113 is the **single source of truth** for automated reports.

---

## 5. Recommendations for Alignment

### Priority: High

1. **Rewrite Phase 3 tasks to reference, not re-implement.** The current tasks 3.1-3.3 in `jira-gitlab-integration-v3/tasks.md` should become deployment steps that point to jira-daily-reports documentation, not re-describe the setup.

2. **Add a scope consistency note** to the Best Practices Guide §8:

   > Automated reports use filter `#15113` (`filter = 15113`). Manual queries below use cross-project JQL. Results may differ slightly due to sprint timing — always trust the automated report for daily standups.

3. **Add a report-to-script mapping table** in the Best Practices Guide §8 so team members know which script generates which report.

### Priority: Medium

4. **Update `jira-gitlab-integration-v3/spec.md`** to explicitly list jira-daily-reports as the Phase 3 deliverable (not a dependency but THE implementation):
   - Current: `jira-daily-reports skill (for Phase 3)` under dependencies
   - Should be: "Phase 3 deploys the existing jira-daily-reports skill — see that skill's documentation for all report configurations"

5. **Add deployment-configuration note** in jira-daily-reports to clarify it uses filter #15113, and that if the team wants cross-project JQL, a new filter or parameterized script would be needed.

### Priority: Low

6. **Consider merging the JQL sections.** The Best Practices Guide §8 defines custom JQL queries. The jira-daily-reports spec defines script JQL. These could be consolidated into one source-of-truth document (e.g., `.agents/skills/jira-daily-reports/references/jql-reference.md`) that both documents reference.

---

## Summary Table

| Item                                                | Status        | Action                                      |
| --------------------------------------------------- | ------------- | ------------------------------------------- |
| Phase 3 cron/email/Slack tasks                      | **DUPLICATE** | Rewrite as deployment + reference           |
| JQL scope mismatch (filter vs cross-project)        | **CONFLICT**  | Add scope note in Best Practices §8         |
| Report count mismatch (4 JQL examples vs 9 reports) | **GAP**       | Add full mapping table                      |
| jira-daily-reports referenced as dependency         | ✅ Correct    | Keep but promote to "is the implementation" |
| Cross-reference link in Best Practices Guide        | ✅ Correct    | Keep                                        |
| Training task (3.4)                                 | ✅ Unique     | Keep as-is                                  |

**Bottom line:** Phase 3 should not re-implement or re-document reports. It should be reduced to a lightweight **deployment phase** that references the existing jira-daily-reports skill. The main alignment work is fixing the JQL scope inconsistency in the Best Practices Guide.

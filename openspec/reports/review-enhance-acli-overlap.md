# Overlap Analysis: enhance-acli-skill ↔ jira-gitlab-integration-v3

**Report generated:** 2026-05-15
**Reviewer:** review subagent
**Sources:**

- `openspec/changes/enhance-acli-skill/` (proposal.md, design.md, tasks.md)
- `openspec/changes/jira-gitlab-integration-v3/` (spec.md, design.md, tasks.md)
- `.agents/skills/jira-integration/SKILL.md`
- `.agents/skills/acli/SKILL.md`

---

## 1. What acli enhancements already support jira-gitlab-v3 needs

The jira-gitlab-integration-v3 spec (Phase 1, FR3, Task 1.4) enhanced `.agents/skills/jira-integration/SKILL.md` with a **"Jira API Integration (via acli)"** section (lines 432–490) covering:

- `acli jira workitem search` (3 examples)
- `acli jira workitem get` (3 examples)
- `acli jira workitem transitions` (1 example)
- `acli jira workitem transition` (2 examples)
- `acli jira workitem comment` (2 examples)
- `acli jira workitem log-work` (2 examples)
- `acli jira sprint list` (1 example in metrics section, line 564)
- `acli auth login` (1 example in appendix, line 722)

These commands come from the **`acli jira workitem`** command group — which is **not** in the set of reference files being modified by enhance-acli-skill. enhance-acli-skill touches:

| File                               | enhance-acli-skill action                                             |
| ---------------------------------- | --------------------------------------------------------------------- |
| `SKILL.md` (acli skill)            | Add team setup, ACLI protocol, compliance, token optimization         |
| `sprint-commands.md`               | Fix flag tables (sprint list-workitems, create, delete, update, view) |
| `board-filter-field-commands.md`   | Fix filter search, expand board search                                |
| `confluence-and-other-commands.md` | Trim Confluence stub                                                  |
| `project-admin-commands.md` (new)  | Extract unique project/auth commands                                  |
| `references/other-commands.md`     | Deleted                                                               |

**No direct acli-command-level support** from enhance-acli-skill feeds into jira-gitlab-v3's needs. The jira-integration skill uses `acli jira workitem` commands, while enhance-acli-skill primarily validates `acli jira sprint`, `acli jira board`, `acli jira filter`, `acli jira field`, `acli jira project`, `acli admin`, and `acli jira auth` command groups.

---

## 2. What would be DUPLICATED

### 2.1 `acli jira sprint list` — minor overlap

**Location:** `.agents/skills/jira-integration/SKILL.md` line 564:

```
acli jira sprint list --board-id 1061 --state closed --output-format json | \
```

**Location in acli skill:** `sprint-commands.md` (being fixed by enhance-acli-skill) documents `sprint list` with its flag table.

**Assessment:** This is **intentional cross-reference, not duplication**. The jira-integration skill shows `sprint list` as a concrete pipeline example (pipe to `jq` for metrics). The acli skill's `sprint-commands.md` documents the full flag table. The two serve different purposes: example usage vs. comprehensive reference. **No deduplication needed.**

### 2.2 `acli auth login` — minor overlap

**Location:** `.agents/skills/jira-integration/SKILL.md` line 722:

```
acli auth login
```

**Location in acli skill:** `project-admin-commands.md` (created by enhance-acli-skill) documents `acli jira auth login` with flags.

**Assessment:** Same as 2.1 — the jira-integration skill shows a minimal auth example for access context, not a reference table. **No deduplication needed.**

### 2.3 Cross-reference from jira-integration → acli skill

**Location:** `.agents/skills/jira-integration/SKILL.md` line 693:

```
**[acli skill](../acli/SKILL.md)** — Atlassian CLI reference
```

**Assessment:** This is the proper pattern — the jira-integration skill delegates acli-specific documentation to the acli skill. enhance-acli-skill ensures that target skill is accurate. **Healthy dependency, not duplication.**

### 2.4 No file-level overlap

```
openspec/changes/enhance-acli-skill/  →  .agents/skills/acli/ (acli skill files)
openspec/changes/jira-gitlab-integration-v3/  →  .agents/skills/jira-integration/ (jira-integration skill files)
                                            →  docs/jira-gitlab-integration/ (documentation)
```

**Zero files are touched by both specs.** Different directories entirely.

---

## 3. Dependencies between the two specs

### Dependency 1 (Weak): jira-integration's acli examples depend on acli skill accuracy

The jira-integration skill documents `acli jira workitem` commands (search, get, transition, comment, log-work). If those commands have undocumented flags or wrong syntax in the acli skill, the jira-integration examples could still be correct — they use basic forms.

**However**, if the jira-integration skill ever adds more acli commands from groups enhanced-acli-skill is fixing (e.g., `acli jira sprint list` from `sprint-commands.md`), it would benefit from the flag validation done in enhance-acli-skill.

**Risk level:** LOW — The current jira-integration acli examples are simple enough that flag drift doesn't affect them.

### Dependency 2 (Weak): Cross-reference link

jira-integration/SKILL.md line 693 links to `../acli/SKILL.md`. If enhance-acli-skill renamed that SKILL.md or changed its path, the link would break. Since enhance-acli-skill only **edits** SKILL.md content (does not move it), this is **not a concern**.

### Dependency 3 (None): Execution ordering

Neither spec modifies overlapping files. They can be applied in any order or simultaneously.

---

## 4. Recommendations for alignment

### 4.1 ✅ No action needed for overlap

The two specs are cleanly separated by scope:

- **enhance-acli-skill** → `.agents/skills/acli/` — acli CLI reference, flag validation, team setup
- **jira-gitlab-integration-v3** → `.agents/skills/jira-integration/` + `docs/jira-gitlab-integration/` — Jira-GitLab workflows, smart commits, automation

The acli commands used in jira-integration (workitem group) are **not** in the set of commands being fixed by enhance-acli-skill (sprint, board, filter, field, project, admin, auth groups). No deduplication is required.

### 4.2 ✅ Cross-reference verification maintained

jira-integration/SKILL.md already correctly references `../acli/SKILL.md`. enhance-acli-skill preserves this link path. No fix needed.

### 4.3 🔍 Future alignment opportunity

If jira-gitlab-integration-v3 Phase 2+ adds more `acli jira sprint` or `acli jira board` commands to the jira-integration skill, consider:

1. Re-using the enhanced acli skill's reference files (`sprint-commands.md`, `board-filter-field-commands.md`) as the single source of truth
2. Adding only usage examples (not flag tables) in jira-integration/SKILL.md, linking back to acli skill for flags

This would prevent the kind of flag-drift problem that motivate enhance-acli-skill in the first place.

### 4.4 ✅ No integration conflict

Both specs are Phase 1 (documentation) complete. They can be committed in either order. No wait-for-dependency constraint exists.

---

## Summary

| Category              | Finding                                                                                                 |
| --------------------- | ------------------------------------------------------------------------------------------------------- |
| **File conflicts**    | ❌ None — zero overlapping files                                                                        |
| **Duplicate content** | ❌ None — different command groups, different purposes                                                  |
| **Cross-references**  | ✅ Healthy — jira-integration→acli link works and is preserved                                          |
| **Dependencies**      | 🔵 Weak — jira-integration acli examples are basic enough that acli flag validation doesn't affect them |
| **Execution order**   | 🔵 Any order — no ordering constraint                                                                   |
| **Action required**   | ❌ None — proceed with both specs independently                                                         |

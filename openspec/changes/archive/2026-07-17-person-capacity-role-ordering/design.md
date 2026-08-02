## Context

The Person Capacity tab in the sprint report is built inside `jira_daily_reports/reports/sprint_report_sheet.py`. Rows come from `_build_person_capacity` and currently flow through a hardcoded active/inactive split with hours-desc ordering inside the active block. Stakeholders want team-bucket grouping; the existing code has no role concept beyond per-row aggregation.

This change adds the role-grouping layer in isolation: a small, focused package with no changes to the sheet writer API or upstream data pipeline. The wire-in is a single site, defensively wrapped so a regression in the new code never breaks the report.

## Goals / Non-Goals

**Goals:**
- Add configurable role-bucket grouping without modifying the sheet writer
- Preserve the active/inactive split (active first, inactive appended)
- Safe zero-config fallback so existing operators see no change
- Single operator config file controls bucket order and member-key prefix matching

**Non-Goals:**
- Changing how hours, worklog data, or roster members are loaded
- Changing per-day hour columns or any other sheet column shape
- Inferring role from email domain, Jira groups, or any external source (member_key prefix is the only signal)
- Backfilling a roster database with role metadata (YAGNI — prefixes are enough)
- Modifying any other report tab (blockers, velocity, standup)

## Decisions

### D1: YAML config at `~/.tdt/person_capacity_roles.yaml`, env override

**Choice:** YAML file at the TDT config dir; env var `PERSON_CAPACITY_ROLE_CONFIG` overrides the default path.

**Why:** Matches the existing operator workflow for `~/.tdt/.env`, `~/.tdt/state/`, etc. The operator workflow is "drop a file in `~/.tdt/` and reload". YAML was preferred over JSON because the file has comments and human-edited labels.

**Alternatives considered:**
- JSON-only: rejected — comments make operator edits error-prone.
- Code-defined buckets: rejected — every roster change requires a deploy.
- Per-bucket env vars (`PERSON_CAPACITY_BUCKET_1_NAME`, etc.): rejected — ugly, un-grouped, no atomic update.

### D2: First-match prefix matching, not regex

**Choice:** Case-insensitive prefix match on `member_key`, with first match in `role_order` list winning.

**Why:** Roster member_keys are deterministic prefixes (`QA_*`, `AOS_*`, `iOS_*`, `Auto_*`, `PL_*`, `Technical_*`, `BA_*`). Prefix match is fast, predictable, and operator-readable. Regex would add a re.compile cost and a sharp edge for operator typos. The first-match-wins rule means operators can layer most-specific prefixes first (`ios_sy` before `ios_`) when they need finer-grained grouping.

**Alternatives considered:**
- Glob (`fnmatch`): rejected — overkill for prefixes.
- Full substring: rejected — `dev` would match `devops-engineer` accidentally.

### D3: "Other" bucket for unmatched members

**Choice:** Members whose `member_key` matches no prefix get bucket label `"Other"`, appended after all explicit buckets.

**Why:** Silent dropping of members is a data-integrity hazard. "Other" preserves visibility while keeping explicit buckets ordered by operator intent.

### D4: Two-pass sort (active first, inactive appended), both grouped

**Choice:** Rows are split into active (`logged_total_seconds > 0`) and inactive, then each block is sorted by `(role priority, person name)`. The active block comes first; inactive follows.

**Why:** Preserves the existing visual hierarchy (active people first — these are the work-hours signal) while applying role grouping within each block. Inactive DEV members still appear before inactive QA members, which is what operators expect.

### D5: Three small modules, not one

**Choice:** `role_config`, `role_classifier`, `sorter` — each in its own file, each with one responsibility.

**Why:** Skill rule: "Each file should have one clear responsibility." Smaller files test better and reason better in context. The classifier has no YAML dependency and can be tested purely against dataclasses.

### D6: Defensive `try/except` at the wire-in site

**Choice:** The integration point in `sprint_report_sheet.py` wraps `sort_person_rows` in `try/except` and falls back to the existing ungrouped renumbering on any exception.

**Why:** A bug in the new module must never crash the sprint report. The fallback preserves the pre-change behavior (active/inactive by hours, name asc).

### D7: Mutate rows in place for `no` renumbering

**Choice:** `sort_person_rows` mutates the `no` field on each input dict and returns the sorted list.

**Why:** `_build_person_capacity` already produces dicts with `no=0` set as a placeholder. The wire-in site needs `no` populated before passing to the sheet writer. Mutating in place avoids a copy. Documented in the function docstring.

## Risks / Trade-offs

- **[Risk] Member_key prefix collisions across buckets** → **Mitigation:** First-match-wins is deterministic. The example config lists buckets from QA → AOS → iOS → Auto → PL → Technical → BA (matching the live Sprint 17 roster prefixes); an operator who reverses them gets a documented behavior, not a crash.

- **[Risk] Operator edits the YAML and breaks parsing** → **Mitigation:** Malformed YAML triggers a logged warning and falls back to empty config (name-only sort). The report still runs.

- **[Risk] Operator forgets to deploy the YAML** → **Mitigation:** The default config is empty, so absent YAML = current behavior. No silent surprises.

- **[Risk] PyYAML not available in the venv** → **Mitigation:** PyYAML is already in `jira-daily-reports` transitive deps (transitively pulled by google-api-python-client and friends). Verified via `uv lock --check`.

- **[Trade-off] Renumbering happens after sort, not during build** → Operators can no longer rely on `no` reflecting "this person logged the most hours". Trade-off accepted because the new ordering conveys team capacity, not personal volume.

## Migration Plan

1. Ship the new module + tests in a single PR.
2. Ship `config/person_capacity_roles.yaml.example` as the operator starter template.
3. Operator copies the example to `~/.tdt/person_capacity_roles.yaml` and edits prefixes to match their roster.
4. **Rollback:** Delete `~/.tdt/person_capacity_roles.yaml` → behavior reverts to current (name-asc / hours-desc). No code rollback needed.
5. **Roll-forward:** Edit YAML and reload — no restart required (config is read at report-time).

## Open Questions

- **Resolved:** YAML config with env override.
- **Resolved:** Name-ascending sort within each role bucket.
- **Resolved:** `qa-chennai-auto` vs `qa-chennai` distinguished via prefix order (most-specific first).
- **Resolved (Sprint 17 verification):** Live operator config uses underscore-separated prefixes (`qa_`, `aos_`, `ios_`, `auto_`, `pl_`, `technical_`, `ba_`) matching the "Dropdown Keys - Do Not Delete -" mapping sheet's member-key convention. The example YAML mirrors these prefixes verbatim; operators adapting to other teams should swap in their own roster's separator.

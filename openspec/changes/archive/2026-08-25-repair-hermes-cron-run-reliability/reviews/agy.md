# AGY Review (Normalized)

**Provider:** agy 1.1.19 (Gemini 3.7 Flash High)
**Status:** SUCCESS
**Tokens:** input=192540, output=17755, total=210295

---

# OpenSpec Change Review: `repair-hermes-cron-run-reliability`

**Reviewer Lens:** Architecture, Ownership Boundaries, and Canonical Automation Paths (`agy`)
**Frozen SHA:** `7c9ceac6e35b5019622be98dfb5788610e2514b3`
**Worktree:** [`/Users/androidteam/orca/workspaces/openspec-store/review-hermes-cron`](file:///Users/androidteam/orca/workspaces/openspec-store/review-hermes-cron)
**Target Change:** [`openspec/changes/repair-hermes-cron-run-reliability`](file:///Users/androidteam/orca/workspaces/openspec-store/review-hermes-cron/openspec/changes/repair-hermes-cron-run-reliability)

---

## 1. Verdict

**`PASS_WITH_CHANGES`**

The core architectural direction is **sound and strongly recommended**:
1. Decoupling the deterministic watchdog check from LLM agent inference eliminates the circular dependency on model auth.
2. Restoring the canonical automation path by converting the weekly freshness job into a strictly read-only reporter eliminates conflicting `graphify update` mutations against the primary LaunchAgent (`com.developer.index-refresh`).
3. Making the wiki lint validation deterministic and read-only preserves repository immutability during automated checks.

However, the change packet contains **architectural contradictions, unresolved ownership decision gates, and contract mismatches** across [`proposal.md`](file:///Users/androidteam/orca/workspaces/openspec-store/review-hermes-cron/openspec/changes/repair-hermes-cron-run-reliability/proposal.md), [`design.md`](file:///Users/androidteam/orca/workspaces/openspec-store/review-hermes-cron/openspec/changes/repair-hermes-cron-run-reliability/design.md), [`tasks.md`](file:///Users/androidteam/orca/workspaces/openspec-store/review-hermes-cron/openspec/changes/repair-hermes-cron-run-reliability/tasks.md), and the delta specs that must be resolved before proceeding to implementation.

---

## 2. Blockers (Must resolve before task execution)

1. **Unresolved Script Ownership Decision Gate (AD1)**
   - [`design.md:6-12`](file:///Users/androidteam/orca/workspaces/openspec-store/review-hermes-cron/openspec/changes/repair-hermes-cron-run-reliability/design.md#L6-L12), [`tasks.md:5,19,37`](file:///Users/androidteam/orca/workspaces/openspec-store/review-hermes-cron/openspec/changes/repair-hermes-cron-run-reliability/tasks.md#L5)
   - *Issue:* Tasks 1.1, 2.1, and 3.6 are marked as `BLOCKED on ownership decision gate`. An OpenSpec change cannot enter implementation with an open architectural gate on script storage.
   - *Architectural Resolution:*
     - **Track 1 (`mcp-router-watchdog` wrapper):** Store canonically in `ops-automation-suite/scripts/hermes-cron/mcp-router-watchdog.sh` (or `mcp-router/scripts/watchdog.sh`) and deploy/symlink to `~/.hermes/scripts/mcp-router-watchdog.sh`.
     - **Track 2 (`weekly-graphify-freshness` reporter):** Store canonically in `~/Developer/scripts/knowledge-refresh/cron-freshness-report.sh` (tracked in workspace repository automation).
     - **Track 3 (`weekly-wiki-lint` validator):** Store canonically in `wiki/scripts/wiki-lint-validator.sh` (tracked within the wiki repo).

2. **Architectural Contradiction on Wiki Lint Execution Model & Ownership**
   - [`design.md:51`](file:///Users/androidteam/orca/workspaces/openspec-store/review-hermes-cron/openspec/changes/repair-hermes-cron-run-reliability/design.md#L51) vs [`proposal.md:25`](file:///Users/androidteam/orca/workspaces/openspec-store/review-hermes-cron/openspec/changes/repair-hermes-cron-run-reliability/proposal.md#L25), [`tasks.md:37`](file:///Users/androidteam/orca/workspaces/openspec-store/review-hermes-cron/openspec/changes/repair-hermes-cron-run-reliability/tasks.md#L37), [`specs/workspace-wiki-integrity/spec.md:67-88`](file:///Users/androidteam/orca/workspaces/openspec-store/review-hermes-cron/openspec/changes/repair-hermes-cron-run-reliability/specs/workspace-wiki-integrity/spec.md#L67-L88)
   - *Issue:* `design.md:51` claims `"Wiki lint: prompt-only, no script ownership needed"`. But `proposal.md:25`, `tasks.md:37` (Task 3.6), and `spec.md:83-88` define it as a deterministic `--no-agent` validator script.
   - *Architectural Resolution:* Reconcile `design.md:51` to explicitly acknowledge the script ownership for `wiki-lint-validator.sh`.

---

## 3. Major Findings

### M1. Contradiction between Recovery Policy in AD2 vs Tasks and Specification
- **References:** [`design.md:26`](file:///Users/androidteam/orca/workspaces/openspec-store/review-hermes-cron/openspec/changes/repair-hermes-cron-run-reliability/design.md#L26) vs [`tasks.md:11-12`](file:///Users/androidteam/orca/workspaces/openspec-store/review-hermes-cron/openspec/changes/repair-hermes-cron-run-reliability/tasks.md#L11-L12) vs [`specs/hermes-cron-run-reliability/spec.md:48-55`](file:///Users/androidteam/orca/workspaces/openspec-store/review-hermes-cron/openspec/changes/repair-hermes-cron-run-reliability/specs/hermes-cron-run-reliability/spec.md#L48-L55)
- **Detail:** AD2 states: *"No duplicate recovery policy. The wrapper does NOT add cooldown timers, daily restart limits, or a second state machine."* However, Task 1.7 introduces a 5-minute cooldown check (`last_restart <5min`), Task 1.8 introduces a crash threshold check (`crash_count_24h >=3`), and `spec.md:48-55` specifies reporting deduplication for historical crash patterns.
- **Architectural Assessment:** The wrapper must remain a thin dispatcher. If cooldown and crash statistics are calculated upstream by `mcp-router-health.sh --json`, the wrapper merely reads those fields. Clarify in AD2 that reading upstream telemetry from JSON does not constitute an independent state machine.

### M2. Conflation of Agent-Mode `[SILENT]` Token vs No-Agent Empty Stdout
- **References:** [`proposal.md:25`](file:///Users/androidteam/orca/workspaces/openspec-store/review-hermes-cron/openspec/changes/repair-hermes-cron-run-reliability/proposal.md#L25) vs [`design.md:28-30`](file:///Users/androidteam/orca/workspaces/openspec-store/review-hermes-cron/openspec/changes/repair-hermes-cron-run-reliability/design.md#L28-L30) (AD3) vs [`specs/workspace-wiki-integrity/spec.md:81`](file:///Users/androidteam/orca/workspaces/openspec-store/review-hermes-cron/openspec/changes/repair-hermes-cron-run-reliability/specs/workspace-wiki-integrity/spec.md#L81)
- **Detail:** `proposal.md:25` states: `"[SILENT] suppression when findings are reported to origin."` In Hermes, `[SILENT]` is an LLM agent prompt convention. For `--no-agent` (script) mode, Hermes suppresses delivery strictly when stdout is empty (0 bytes). If an alert or findings are present, stdout is emitted to origin without any `[SILENT]` tag.
- **Architectural Assessment:** Emitting `[SILENT]` in a script would leak the string literal `[SILENT]` to the user channel. Standardize all three tracks on strict 0-byte stdout silence semantics.

### M3. Inconsistency on Schema Field Auditing (`type` field)
- **References:** [`specs/workspace-wiki-integrity/spec.md:11`](file:///Users/androidteam/orca/workspaces/openspec-store/review-hermes-cron/openspec/changes/repair-hermes-cron-run-reliability/specs/workspace-wiki-integrity/spec.md#L11) vs [`specs/workspace-wiki-integrity/spec.md:37-38`](file:///Users/androidteam/orca/workspaces/openspec-store/review-hermes-cron/openspec/changes/repair-hermes-cron-run-reliability/specs/workspace-wiki-integrity/spec.md#L37-L38) vs [`tasks.md:29`](file:///Users/androidteam/orca/workspaces/openspec-store/review-hermes-cron/openspec/changes/repair-hermes-cron-run-reliability/tasks.md#L29)
- **Detail:** `spec.md:11` and `tasks.md:29` state that `type` is *not* part of the audit (only 5 fields audited: `title`, `tags`, `created`, `updated`, `status`). But `spec.md:37-38` states: *"its frontmatter template SHALL include `title`, `type`, `tags`, `created`, `updated`, and `status` AND the lint audit SHALL check exactly these fields"*.
- **Architectural Assessment:** If `type` is optional in the audit, `spec.md:38` must specify that the audit checks the 5 required fields while `SCHEMA.md` documents `type` as optional frontmatter.

### M4. Artificial Blocker: AD5b Reference Page Date is Already Resolved in Spec & Evidence
- **References:** [`design.md:37-39`](file:///Users/androidteam/orca/workspaces/openspec-store/review-hermes-cron/openspec/changes/repair-hermes-cron-run-reliability/design.md#L37-L39) (AD5b), [`tasks.md:30`](file:///Users/androidteam/orca/workspaces/openspec-store/review-hermes-cron/openspec/changes/repair-hermes-cron-run-reliability/tasks.md#L30) (Task 3.2) vs [`specs/workspace-wiki-integrity/spec.md:89-98`](file:///Users/androidteam/orca/workspaces/openspec-store/review-hermes-cron/openspec/changes/repair-hermes-cron-run-reliability/specs/workspace-wiki-integrity/spec.md#L89-L98) vs [`evidence.md:64`](file:///Users/androidteam/orca/workspaces/openspec-store/review-hermes-cron/openspec/changes/repair-hermes-cron-run-reliability/evidence.md#L64)
- **Detail:** `design.md` and `tasks.md` list date resolution as an open gate blocking Task 3.2. However, `spec.md:89-98` and `evidence.md:64` have already established the rule: rename `date: 2026-08-20` to `created: 2026-08-20`.
- **Architectural Assessment:** Unblock Task 3.2 by syncing `design.md` and `tasks.md` with the resolved requirement in `spec.md`.

### M5. Log Parsing Coupling in Track 2 Freshness Reporter
- **References:** [`specs/workspace-index-freshness/spec.md:32,41`](file:///Users/androidteam/orca/workspaces/openspec-store/review-hermes-cron/openspec/changes/repair-hermes-cron-run-reliability/specs/workspace-index-freshness/spec.md#L32)
- **Detail:** Deriving `operation_status` (such as `TIMEOUT` or `DIRTY_SKIP`) requires bounded parsing of raw log lines in `~/Developer/.knowledge-refresh/refresh.log`.
- **Architectural Assessment:** Coupling the reporter to raw unstructured log files creates a brittle dependency if log formatting or rotation changes. The spec must define a safe fallback (`operation_status: UNKNOWN`) if `refresh.log` is absent or unparseable.

---

## 4. Minor Findings

- **m1. Duplicate Phrasing in Wiki Integrity Spec:**
  - [`specs/workspace-wiki-integrity/spec.md:81`](file:///Users/androidteam/orca/workspaces/openspec-store/review-hermes-cron/openspec/changes/repair-hermes-cron-run-reliability/specs/workspace-wiki-integrity/spec.md#L81): `"THEN the job SHALL emit empty stdout or empty stdout (suppressing delivery)"` contains duplicate phrasing.
- **m2. Baseline Snapshot in Cron Mutation Tasks:**
  - [`tasks.md:13,23`](file:///Users/androidteam/orca/workspaces/openspec-store/review-hermes-cron/openspec/changes/repair-hermes-cron-run-reliability/tasks.md#L13): Modifying jobs with `hermes cron edit` should explicitly specify saving `hermes cron list --json` baseline output as audit evidence alongside backup files (per [`hermes-configuration-safety/spec.md`](file:///Users/androidteam/orca/workspaces/openspec-store/review-hermes-cron/openspec/specs/hermes-configuration-safety/spec.md)).
- **m3. Provider Version Reporting Consistency:**
  - [`specs/workspace-index-freshness/spec.md:20-26`](file:///Users/androidteam/orca/workspaces/openspec-store/review-hermes-cron/openspec/changes/repair-hermes-cron-run-reliability/specs/workspace-index-freshness/spec.md#L20-L26): Correctly adjusts the canonical spec's fail-closed behavior to allow honest reporting of installed vs pinned versions (Graphify 0.9.46 vs 0.9.42).

---

## 5. Evidence References

| File & Line | Context / Finding |
|---|---|
| [`proposal.md:8`](file:///Users/androidteam/orca/workspaces/openspec-store/review-hermes-cron/openspec/changes/repair-hermes-cron-run-reliability/proposal.md#L8) | Watchdog failure evidence during model auth outage (36 failed, 3 unknown). |
| [`proposal.md:25`](file:///Users/androidteam/orca/workspaces/openspec-store/review-hermes-cron/openspec/changes/repair-hermes-cron-run-reliability/proposal.md#L25) | Erroneous reference to `[SILENT]` suppression for a `--no-agent` script. |
| [`design.md:6-12`](file:///Users/androidteam/orca/workspaces/openspec-store/review-hermes-cron/openspec/changes/repair-hermes-cron-run-reliability/design.md#L6-L12) | AD1 unclosed decision gate blocking script creation tasks. |
| [`design.md:26`](file:///Users/androidteam/orca/workspaces/openspec-store/review-hermes-cron/openspec/changes/repair-hermes-cron-run-reliability/design.md#L26) | AD2 prohibiting duplicate cooldown policy. |
| [`design.md:37-39`](file:///Users/androidteam/orca/workspaces/openspec-store/review-hermes-cron/openspec/changes/repair-hermes-cron-run-reliability/design.md#L37-L39) | AD5b unresolved date gate conflicting with `spec.md:89-98`. |
| [`design.md:51`](file:///Users/androidteam/orca/workspaces/openspec-store/review-hermes-cron/openspec/changes/repair-hermes-cron-run-reliability/design.md#L51) | Claim that wiki lint is prompt-only conflicting with Task 3.6 / Track 3. |
| [`tasks.md:5,19,37`](file:///Users/androidteam/orca/workspaces/openspec-store/review-hermes-cron/openspec/changes/repair-hermes-cron-run-reliability/tasks.md#L5) | Tasks 1.1, 2.1, 3.6 blocked on script ownership gate. |
| [`tasks.md:11-12`](file:///Users/androidteam/orca/workspaces/openspec-store/review-hermes-cron/openspec/changes/repair-hermes-cron-run-reliability/tasks.md#L11-L12) | Tasks 1.7 and 1.8 testing cooldown and crash limits conflicting with AD2 text. |
| [`tasks.md:30`](file:///Users/androidteam/orca/workspaces/openspec-store/review-hermes-cron/openspec/changes/repair-hermes-cron-run-reliability/tasks.md#L30) | Task 3.2 blocked on date decision gate. |
| [`specs/hermes-cron-run-reliability/spec.md:48-55`](file:///Users/androidteam/orca/workspaces/openspec-store/review-hermes-cron/openspec/changes/repair-hermes-cron-run-reliability/specs/hermes-cron-run-reliability/spec.md#L48-L55) | Historical crash deduplication requirement. |
| [`specs/workspace-index-freshness/spec.md:32,41`](file:///Users/androidteam/orca/workspaces/openspec-store/review-hermes-cron/openspec/changes/repair-hermes-cron-run-reliability/specs/workspace-index-freshness/spec.md#L32) | Log scraping from `~/Developer/.knowledge-refresh/refresh.log`. |
| [`specs/workspace-wiki-integrity/spec.md:11,37-38`](file:///Users/androidteam/orca/workspaces/openspec-store/review-hermes-cron/openspec/changes/repair-hermes-cron-run-reliability/specs/workspace-wiki-integrity/spec.md#L11) | Contradiction regarding `type` field in wiki audit. |
| [`specs/workspace-wiki-integrity/spec.md:81`](file:///Users/androidteam/orca/workspaces/openspec-store/review-hermes-cron/openspec/changes/repair-hermes-cron-run-reliability/specs/workspace-wiki-integrity/spec.md#L81) | Typo: duplicate `"empty stdout or empty stdout"`. |
| [`specs/workspace-wiki-integrity/spec.md:89-98`](file:///Users/androidteam/orca/workspaces/openspec-store/review-hermes-cron/openspec/changes/repair-hermes-cron-run-reliability/specs/workspace-wiki-integrity/spec.md#L89-L98) | Spec codifying `date: 2026-08-20` -> `created: 2026-08-20`. |
| [`evidence.md:64`](file:///Users/androidteam/orca/workspaces/openspec-store/review-hermes-cron/openspec/changes/repair-hermes-cron-run-reliability/evidence.md#L64) | Diagnostic discovery confirming reference date rename. |

---

## 6. Concrete Proposed Edits

### Edit 1: Resolve Script Ownership in `design.md` & `tasks.md`
- **File:** [`openspec/changes/repair-hermes-cron-run-reliability/design.md`](file:///Users/androidteam/orca/workspaces/openspec-store/review-hermes-cron/openspec/changes/repair-hermes-cron-run-reliability/design.md#L6-L12)
  - Replace AD1 with:
    ```markdown
    ### AD1: Script ownership and canonical paths
    All cron wrapper and validator scripts SHALL reside in version-controlled repositories and be deployed to their runtime paths:
    1. Watchdog wrapper: Canonical source `ops-automation-suite/scripts/hermes-cron/mcp-router-watchdog.sh` -> deployed to `~/.hermes/scripts/mcp-router-watchdog.sh`.
    2. Freshness reporter: Canonical source `~/Developer/scripts/knowledge-refresh/cron-freshness-report.sh` (tracked in workspace repository).
    3. Wiki lint validator: Canonical source `wiki/scripts/wiki-lint-validator.sh` (tracked in wiki repository).
    ```
  - Update `Ownership` section (lines 49–51) to reflect these three tracked locations.
- **File:** [`openspec/changes/repair-hermes-cron-run-reliability/tasks.md`](file:///Users/androidteam/orca/workspaces/openspec-store/review-hermes-cron/openspec/changes/repair-hermes-cron-run-reliability/tasks.md#L5)
  - Remove `BLOCKED on ownership decision gate` from Tasks 1.1, 2.1, and 3.6.

### Edit 2: Align Cooldown and Telemetry in `design.md` AD2
- **File:** [`openspec/changes/repair-hermes-cron-run-reliability/design.md`](file:///Users/androidteam/orca/workspaces/openspec-store/review-hermes-cron/openspec/changes/repair-hermes-cron-run-reliability/design.md#L26)
  - Replace paragraph with:
    ```markdown
    **Telemetry consumption without duplicate policy engine.** The wrapper delegates process restart and escalation execution to `mcp-router-health.sh`. It consumes the health script's JSON fields (`crash_count_24h`, `last_restart_seconds_ago`, `restart_needed`) to format state-change alerts and deduplicate recurring crash notices in the local state file, without maintaining a separate independent daemon or recovery state machine.
    ```

### Edit 3: Fix Silence Semantics in `proposal.md`
- **File:** [`openspec/changes/repair-hermes-cron-run-reliability/proposal.md`](file:///Users/androidteam/orca/workspaces/openspec-store/review-hermes-cron/openspec/changes/repair-hermes-cron-run-reliability/proposal.md#L25)
  - Replace line 25 with:
    ```markdown
    Add `status: active` to 17 pages. Rename references page `date` to `created: 2026-08-20`. Fix broken relative links with `../` prefixes. Update `SCHEMA.md` template. Convert wiki lint to a deterministic no-agent validator script — empty stdout (0 bytes) when clean, emitting findings to stdout only when validation issues are detected.
    ```

### Edit 4: Reconcile Date Gate AD5b and Task 3.2
- **File:** [`openspec/changes/repair-hermes-cron-run-reliability/design.md`](file:///Users/androidteam/orca/workspaces/openspec-store/review-hermes-cron/openspec/changes/repair-hermes-cron-run-reliability/design.md#L37-L39)
  - Replace AD5b with:
    ```markdown
    ### AD5b: Reference page creation date preservation
    The references page `date: 2026-08-20` is renamed to `created: 2026-08-20` to preserve the authentic semantic evaluation date, rather than overwriting with the git commit timestamp (2026-08-23).
    ```
- **File:** [`openspec/changes/repair-hermes-cron-run-reliability/tasks.md`](file:///Users/androidteam/orca/workspaces/openspec-store/review-hermes-cron/openspec/changes/repair-hermes-cron-run-reliability/tasks.md#L30)
  - Replace Task 3.2 with:
    ```markdown
    - [ ] 3.2 Rename references page frontmatter `date: 2026-08-20` to `created: 2026-08-20`
    ```

### Edit 5: Clarify Wiki Frontmatter Schema vs Audit Scope
- **File:** [`openspec/changes/repair-hermes-cron-run-reliability/specs/workspace-wiki-integrity/spec.md`](file:///Users/androidteam/orca/workspaces/openspec-store/review-hermes-cron/openspec/changes/repair-hermes-cron-run-reliability/specs/workspace-wiki-integrity/spec.md#L37-L38)
  - Update Scenario `Schema template includes all required fields`:
    ```markdown
    - **WHEN** SCHEMA.md is inspected
    - **THEN** its frontmatter template SHALL include `title`, `type`, `tags`, `created`, `updated`, and `status`
    - **AND** the lint audit SHALL enforce presence of the 5 required fields (`title`, `tags`, `created`, `updated`, `status`), treating `type` as optional metadata
    ```
- **File:** [`openspec/changes/repair-hermes-cron-run-reliability/specs/workspace-wiki-integrity/spec.md`](file:///Users/androidteam/orca/workspaces/openspec-store/review-hermes-cron/openspec/changes/repair-hermes-cron-run-reliability/specs/workspace-wiki-integrity/spec.md#L81)
  - Fix typo: change `empty stdout or empty stdout (suppressing delivery)` to `empty stdout (suppressing delivery)`.

---

## 7. Residual Risks

1. **Log Rotation & Parsing Fragility in Freshness Reporting:**
   - Because Track 2 relies on reading `~/Developer/.knowledge-refresh/refresh.log` to infer `operation_status` (`TIMEOUT` / `DIRTY_SKIP`), log truncation or concurrent rotation during cron execution could yield `UNKNOWN`. The wrapper script must handle unreadable log scenarios gracefully without crashing (exiting 0 with `operation_status: UNKNOWN`).
2. **State File Stale Locks in `/tmp`:**
   - `/tmp/mcp-router-watchdog-state.json` is purged across system reboots. The wrapper must always validate file existence and permissions defensively on every tick.
3. **Deployment Divergence:**
   - Because scripts are copied or symlinked to `~/.hermes/scripts/`, operators must ensure the deployment step is verified during acceptance testing (`tasks.md: 1.10, 2.6, 3.7`).

---

*(Note: In accordance with READ-ONLY review instructions, no files, commits, or configuration states were modified.)*


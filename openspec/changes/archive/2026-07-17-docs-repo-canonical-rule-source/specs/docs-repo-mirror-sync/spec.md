# Spec: `code-daily-scan` — Docs-Repo Mirror Sync & Retirement

The docs repo's v1.1.0 freeze created two local mirrors that have **already drifted** from the canonical source. The drift-detection capability (`docs-repo-drift-detection`) SURFACES the problem; this capability **fixes** it by introducing a sync mechanism and a documented retirement timeline. End state: there is exactly one canonical source of truth (the docs repo) and zero local mirrors — every consumer reads from the canonical source directly.

## ADDED Requirements

### Requirement: M-1 — `sync-rules` CLI pushes canonical → mirror

The scanner SHALL expose a `code-daily-scan sync-rules` subcommand that reads the canonical docs-repo category files and writes them into the local mirror in the platform repo. The command MUST be idempotent and MUST refuse to clobber a mirror file whose content is NOT byte-identical to the canonical version unless `--force` is supplied.

#### Scenario: Sync writes mirror for Android
- GIVEN `poems-mobile3-docs/50.RCA/20.AOS/rules/categories/state-mutation.md` exists with content `S`
- AND `poems-mobile3-android/docs/rules/categories/state-mutation.md` either is missing or matches `S`
- WHEN `code-daily-scan sync-rules --platform=android` runs
- THEN the local mirror file MUST contain content `S` (byte-identical to canonical)
- AND the command MUST emit `sync_status=ok identical_written=1`.

#### Scenario: Sync refuses to clobber without --force
- GIVEN the local mirror in `poems-mobile3-android/docs/rules/categories/architecture-maintainability.md` differs from canonical (the existing drift)
- WHEN `code-daily-scan sync-rules --platform=android` runs (without `--force`)
- THEN the local mirror MUST NOT be modified
- AND the command MUST emit `sync_status=refused files=[architecture-maintainability.md]` and exit 1.

#### Scenario: Sync with --force clobbers
- GIVEN the local mirror differs from canonical
- WHEN `code-daily-scan sync-rules --platform=android --force` runs
- THEN the local mirror MUST be overwritten with canonical content
- AND a backup MUST be written to `docs/rules/categories/.sync-backup/<timestamp>/<file>.md` before overwrite
- AND the command MUST emit `sync_status=ok_with_force clobbered_files=[architecture-maintainability.md]`.

#### Scenario: Sync for iOS swaps categories layout
- GIVEN `poems-mobile3-ios/docs/technical-debt-scan/categories/` contains 4 legacy files (`architecture-maintainability.md`, `crash-prevention.md`, `lifecycle-observers-state.md`, `retain-cycle-memory.md`) in legacy naming
- WHEN `code-daily-scan sync-rules --platform=ios --restructure` runs
- THEN the command MUST back up the legacy folder to `docs/technical-debt-scan/.sync-backup/<timestamp>/`
- AND MUST write the 9 canonical files to a new mirror location `docs/rules/categories/` (note: a different folder, matching Android's canonical mirror path)
- AND MUST print a manual-step message: "Update poems-mobile3-ios/.agents/load-project-rulebook.mdc to reference `docs/rules/categories/` instead of `docs/technical-debt-scan/categories/`."

### Requirement: M-2 — Sync is workspace-relative, not global

`sync-rules` MUST operate only on the configured target repo for the specified platform. It MUST NOT modify any file outside the platform repo's `docs/` subtree.

#### Scenario: Sync respects --repo-path override
- GIVEN a developer points `--repo-path` at a non-default checkout for testing
- WHEN `code-daily-scan sync-rules --platform=android --repo-path=~/work/foo` runs
- THEN only files under `~/work/foo/docs/rules/categories/` are touched
- AND the configured global mirror at `~/Developer/tdt/poems-mobile3-android/docs/rules/categories/` is NOT modified.

### Requirement: M-3 — Sync requires a clean git tree or --force-clobber

To prevent data loss, `sync-rules` MUST refuse to run when the target repo has uncommitted local changes in the mirror folder unless `--force-clobber` is supplied (a separate flag from `--force`, more dangerous).

#### Scenario: Sync refuses on dirty mirror
- GIVEN `poems-mobile3-android/docs/rules/categories/state-mutation.md` has uncommitted local modifications (verified via `git status --porcelain`)
- WHEN `code-daily-scan sync-rules --platform=android --force` runs (without `--force-clobber`)
- THEN the command MUST exit 1 with `sync_status=refused_dirty reason="<file> has uncommitted changes; pass --force-clobber to proceed"`
- AND the mirror MUST NOT be modified.

#### Scenario: Sync with --force-clobber accepts dirty mirror
- GIVEN the mirror has uncommitted changes
- WHEN `code-daily-scan sync-rules --platform=android --force --force-clobber` runs
- THEN the local edits MUST be backed up to `.sync-backup/<timestamp>/<file>.md`
- AND the mirror MUST be overwritten with canonical content.

### Requirement: M-4 — Mirror retirement is phased (zero mirrors at end state)

This change declares a **3-release retirement timeline** for the local mirrors. The end state is that NO local mirror MUST remain on disk in any app repo. Every consumer SHALL read the canonical docs repo directly via the scanner's `rules_repo_path` config or the AI workflow's docs-repo path. CI SHALL fail-when-drift once the v2 follow-up ships.

| Release | Phase | Mirror state |
|---|---|---|
| v1 of this change | Detection | Mirrors MAY exist; drift is detected and logged at runtime |
| v2 follow-up (task §10.7) | Sync | `sync-rules` CLI ships in `code-daily-scan`; CI guard runs `check-docs-drift` and fails on drift |
| v3 follow-up (task §10.8) | Retirement | Local mirrors MUST be removed from app repos; `.agents/load-project-rulebook.mdc` MUST be updated to reference the canonical docs-repo path |

#### Scenario: v3 state - no mirrors
- GIVEN the v3 follow-up has shipped
- WHEN a developer runs `ls poems-mobile3-android/docs/rules/` or `ls poems-mobile3-ios/docs/technical-debt-scan/categories/`
- THEN those folders MUST NOT exist on disk
- AND the `load-project-rulebook.mdc` Cursor rule MUST reference `<rules_repo>/20.Developments/40.AI/50.RCA/<platform>/rules/categories/`.

#### Scenario: Offline operator still supported at end state
- GIVEN a developer whose workstation has no docs-repo checkout
- WHEN they set `rules_repo_path: ""` (explicit empty) in their config
- THEN the scanner MUST fall back to legacy YAML exactly as it does today
- AND the offline dev workflow SHALL NOT be broken by mirror retirement.

### Requirement: M-5 — Sync must produce an audit trail per run

`sync-rules` MUST append a log entry to `<target_repo>/docs/.sync-history.md` (creating it if absent) describing what it did, when, and why.

#### Scenario: Successful sync produces audit entry
- GIVEN `code-daily-scan sync-rules --platform=android --force` runs successfully
- WHEN the run completes
- THEN `<target_repo>/docs/.sync-history.md` MUST contain a new dated entry following the format below.

#### Scenario: Failed sync (refuse) does not produce audit entry
- GIVEN the local mirror differs from canonical and `--force` is NOT supplied
- WHEN `code-daily-scan sync-rules --platform=android` runs
- THEN the command MUST exit 1 without writing any mirror files
- AND the audit log MUST NOT receive a new entry (a refused sync is not a sync).

#### Scenario: Audit header is created on first run
- GIVEN `<target_repo>/docs/.sync-history.md` does not exist
- WHEN the first successful sync runs
- THEN the file MUST be created with an `# Sync History` header followed by the first dated entry.

#### Scenario: Audit entry format
- The format MUST be a Markdown heading + table, structured as follows.

- A successful run with `<platform>=android`, no clobber, 9 files written produces an entry like:

```
## YYYY-MM-DD HH:MM:SS UTC -- code-daily-scan sync-rules

| Platform | Status | Files written | Files clobbered | Backup path |
|---|---|---|---|---|
| android | ok | 9 | 0 | n/a |

Operator: <env_user>@<hostname>
Source: <canonical_docs_repo_path>@<short-SHA>
```

- A clobbering run with `<platform>=ios` produces an entry like:

```
## YYYY-MM-DD HH:MM:SS UTC -- code-daily-scan sync-rules

| Platform | Status | Files written | Files clobbered | Backup path |
|---|---|---|---|---|
| ios | ok_with_force | 9 | 0 | docs/technical-debt-scan/.sync-backup/2026-07-09T14-32-15Z/ |

Operator: <env_user>@<hostname>
Source: <canonical_docs_repo_path>@<short-SHA>
```

## Cross-references

- Internal: companion `specs/docs-repo-drift-detection/spec.md` (D-4 references the `sync-rules` CLI)
- Internal: `code_daily_scan.cli.sync_rules` (new subcommand)
- External docs: `poems-mobile3-docs/20.Developments/40.AI/50.RCA/changelog.md` must record each sync breaking change
- External OpenSpec change: `code-daily-scan-mirror-retirement-v2` (tasks §10.7 + §10.8)
- External Cursor rule: `poems-mobile3-docs/20.Developments/40.AI/30.AOS/rules/load-project-rulebook.mdc` (will be updated in v3)

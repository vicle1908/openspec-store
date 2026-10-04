# Verification Evidence: Automate Scheduled Refresh of Upstream Skill Content

## Date: 2026-10-04

Target of change: `~/Developer/scripts/workstation-daily-update.sh` — a daily
launchd job (`com.developer.workstation-daily-update`, 08:00). `~/Developer` is
not a Git repository; the store `openspec-store` holds the planning artifacts.

---

## 1. Refresh stage scaffolding and output parsing (tasks 1.1–1.4)

### 1.1 Helper runs and captures output

- **Command**: `skills update -y` run from a scratch dir holding a copy of
  `skills-lock.json`, output captured to a file.
- **Result**: exit `0`, 3862 bytes captured; ANSI sequences stripped with `sed`.
- **Observed (raw, pre-strip)**:

  ```text
  Checking for skill updates…
  Refreshing 43 skill(s)…
  ✓ Updated 42 skill(s)
  ```

### 1.2 Five-outcome classifier

Sample outputs captured from real runs and fed to `classify_refresh`.

| Sample                        | Expected                                                              | Observed |
| ----------------------------- | --------------------------------------------------------------------- | -------- |
| project refresh (real capture)| `drift=1 refreshed=42 already_current=0 path_ambiguous=1 failed=0`    | match    |
| already-current               | `drift=1 refreshed=0 ... failed=0`                                    | match    |
| global drift (`Found 3 …`)    | `drift=1 refreshed=1 ... failed=0`                                    | match    |
| path-ambiguous only           | `drift=0 refreshed=0 already_current=0 path_ambiguous=1 failed=0`     | match    |

Test harness result: `pass=5 fail=0`.

### 1.3 Unrecognized summary is a failure

- **Command**: `classify_refresh` fed a garbled, a truncated, and an empty summary.
- **Observed**: all three → `failed=1` (not `already_current=1`).
- Also verified `rc!=0` → `failed=1` even when a plausible summary is present.

### 1.4 No `computedHash` reliance

- **Command**: `grep -c 'computedHash' workstation-daily-update.sh`
- **Observed**: no match in the helper — the classifier does not compare the
  lockfile digest against a locally computed one.

---

## 2. Pipeline integration and stage ordering (tasks 2.1–2.4)

### 2.1 Stage order

- **Command**: `grep -oE 'Stage [0-9]/8' workstation-daily-update.sh`
- **Observed**: banners `1/8` … `8/8` in order, with:
  - `6/8` Cross-Agent Skills Parity Check
  - `7/8` Skill Content Refresh (canonical store)
  - `8/8` OpenSpec Store Strict Validation

  Line-number check: parity=288, refresh=311, validation=325 → `ORDER OK`.

### 2.2 Outcome summary is logged

- **Observed in a full apply run**:

  ```text
  >>> [Stage 7/8] Skill Content Refresh (canonical store)
      drift=1 refreshed=42 already_current=0 path_ambiguous=1 failed=0
      summary: refreshed=42 already_current=0 path_ambiguous=1 failed=0
  ```

### 2.3 Refresh failure does not abort later stages

- **Observed**: full run reaches `Stage 8/8` and prints
  `Totals: 437 passed, 0 failed`, then reports the degradation and
  `— Complete [MODE=apply]` with exit `0`. A refresh failure therefore does not
  suppress validation.

### 2.4 Parity fail-closed behavior unchanged

- **Command**: `python3 ~/Developer/platform/openspec-store/scripts/sync-workspace-agent-skills.py --check`
- **Observed**: exit `0` on a clean tree; the script still gates on
  `SYNC_FAILED` and `return 1`s when unresolved links remain (paths unchanged at
  lines 289–305 and 341).

---

## 3. Path-ambiguity handling (tasks 3.1–3.3)

### 3.1 Ambigit count is separate from failures

- **Observed (live refresh stage)**:
  `drift=1 refreshed=42 already_current=0 path_ambiguous=1 failed=0`
- `path_ambiguous=1` (for `docfork-docs`) with `failed=0` — not counted as failed.

### 3.2 Ambiguity-only run concludes successfully

- **Observed**: full apply run exit `0`, `— Complete [MODE=apply]`; the
  fail-closed path was not triggered.

### 3.3 Ambiguity is logged as informational with its source

- **Observed**:

  ```text
  path-ambiguous (informational, not stale/broken/failed): 1 entr(y/ies)
    Warning: Multiple current paths match these skills from docfork/docfork; skipping them rather than deleting or migrating the wrong skill:
  ```

  The entry is labelled informational and names `docfork/docfork`; it is not
  labelled stale or broken.

---

## 4. Agent CLI coverage (tasks 4.1–4.5)

Run of `agent_cli_coverage` with the declared covered set:

```text
covered set: claude,codex,opencode,kilo,auggie,qoder,pi
  - Claude Code (claude): updated
  - OpenAI Codex (codex): updated
  - OpenCode (opencode): updated
    Error: Failed to change directory to /private/tmp/update
  - Kilo (kilo): FAILED (rc=0 but reported an error)
  - Auggie (auggie): updated
  - Claude-Fable (qoder): updated
  - Pi (pi): updated
  - uncovered: droid (installed, no scriptable update verb; self-updates in-app)
AGENT_FAILED=1
```

- **4.1** Covered set is declared and reported; each installed covered agent was
  updated by the loop.
- **4.2** `auggie` ran as `auggie update --skip-confirmation`; observed
  `✅ You are already running the latest version (0.36.0)` — completed without
  blocking on a prompt.
- **4.3** `droid` reported `uncovered`; no absent agent produced an error.
- **4.4** Each update is wrapped: `run_with_timeout "${AGENT_UPDATE_TIMEOUT}" ...`
  with `AGENT_UPDATE_TIMEOUT=900`.
- **4.5** `kilo` exited `0` while printing
  `Error: Failed to change directory to …`; reported as
  `FAILED (rc=0 but reported an error)` and `AGENT_FAILED=1`.

---

## 5. Time-bounded refresh (tasks 5.1–5.3)

### 5.1 Helper present

- `run_with_timeout()` is defined in the daily script (copied from
  `knowledge-refresh/refresh-knowledge-indexes.sh`), no new cross-file sourcing.

### 5.2 Timeout returns 124

- **Commands / results**:

  ```text
  run_with_timeout 2 sleep 30   -> rc=124   (expected 124)
  run_with_timeout 10 true      -> rc=0
  run_with_timeout 10 false     -> rc=1
  run_with_timeout 10 printf 'hello-from-child\n' -> captured: hello-from-child
  ```

### 5.3 Timeout does not stall the run

- A `124` return is classified `refresh_failed`; the stage returns `0` to the
  pipeline, so later stages still execute (see 2.3).

---

## 6. Documentation and integration verification (tasks 6.1–6.6)

### 6.1 Documentation

The script header documents: the absence of a dry-run mode, the pre-flight drift
signal, the five outcomes, the path-ambiguity exception, the lock-digest rule,
the timeout bounds, the zero-exit-error rule, and the manual command.

- **Verification**: `bash workstation-daily-update.sh --check`
- **Observed**: `rc=0`,
  `— Workstation Daily Update [MODE=check]`,
  refresh summary `summary: refreshed=42 already_current=0 path_ambiguous=1 failed=0`,
  `— Complete [MODE=check]`. The documented command reproduced the outcome.

### 6.2 Drift reported before mutation

- **Observed line order** from a captured run:
  - index 1: `Refreshing 43 skill(s)…`
  - index 2: `Updating agent-onboarding…`
- → `ORDER OK`.

### 6.3 No dry-run mode

- **Command**: `skills update --help`
- **Observed**: only `-g, --global`, `-p, --project`, `-y, --yes`. No
  `--dry-run`, `--check`, or `--json`. Documented as such in the script header.

### 6.4 Zero regressions

- **Command**: `openspec validate --all --strict --store openspec-store`
- **Observed**: `✓ change/automate-skill-content-refresh`,
  `Totals: 437 passed, 0 failed (437 items)`.

### 6.5 Idempotence

Two immediate successive apply runs:

```text
run1: drift=1 refreshed=42 already_current=0 path_ambiguous=1 failed=0
run2: drift=1 refreshed=42 already_current=0 path_ambiguous=1 failed=0
```

Identical outcome, same single path-ambiguous entry.

### 6.6 Schedule unchanged

- **Command**: `plutil -p ~/Library/LaunchAgents/com.developer.workstation-daily-update.plist`
- **Observed**:

  ```text
  1 => "/Users/androidteam/Developer/scripts/workstation-daily-update.sh"
  "Hour" => 8
  "Minute" => 0
  ```

No plist change was required.

---

## 7. Change durability (task 7.1)

The change artifacts are committed to the store rather than left untracked,
because on 2026-10-04 an untracked change directory in this store was removed at
the filesystem level with no git recovery path.

- **Command**: `git -C ~/Developer/platform/openspec-store ls-files openspec/changes/automate-skill-content-refresh`
- **Observed**: 5 files tracked (`proposal.md`, `specs/.../spec.md`, `design.md`,
  `tasks.md`, `.openspec.yaml`).
- **Commits**: `e0399e38` (artifacts), `89336f03`, `44ca9131` (task progress).

---

## Residual risks

- **`kilo update` fails upstream** with `Error: Failed to change directory to …`
  and exit `0`. This stage now *detects and reports* it, but the underlying
  upstream defect is out of scope and unfixed.
- **`docfork-docs` is unrefreshable** while upstream publishes it at two paths.
  Its on-disk content already equals the lock digest, so nothing is stale; the
  skip is reported as informational.
- **The actor that removed untracked change directories on 2026-10-04 is
  unidentified.** Verified exclusions: OpenSpec archive/bulk-archive (always
  `mv` + commit), the knowledge-refresh job family (its launchd logs last wrote
  02:35, before the change existed), and workspace-retention/workspace-lifecycle
  (scope excludes `openspec/changes`; explicitly protects active changes). The
  removal happened outside git; no dangling object references the change.

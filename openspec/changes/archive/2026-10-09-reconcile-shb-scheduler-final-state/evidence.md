# OpenSpec Verification Evidence: reconcile-shb-scheduler-final-state

## 1. Environment & Target Roots

- **Central Planning Store**: `/Users/androidteam/Developer/platform/openspec-store` (git commit: `1991c03b`)
- **Scheduler Repository**: `/Users/androidteam/Developer/shb/shb-schedule` (git commit: `d0729567d2d819a570a9f49bde86a78a02f22a35`, branch: `main`)
- **Skills Repository**: `/Users/androidteam/Developer/shb/shb-agent-skills` (git commit: `4d3aa3d35feff458afb0c5e98d862c1198974c45`, branch: `main`)
- **Documentation Root**: `/Users/androidteam/Developer/wiki/entities`
- **Cleanup Targets**:
  - LaunchAgent: `/Users/androidteam/Library/LaunchAgents/com.shb.schedule.plist`
  - Service Cache: `/Users/androidteam/Developer/shb/shb-schedule/src/shb_schedule/service/`

---

## 2. Archive Immutability & Historical Reconciliations

- **Immutable Archive Path**: `openspec/changes/archive/2026-10-09-containerize-shb-scheduler-postgres18/`
- **Diff Against Archive**: `git diff --name-only HEAD -- openspec/changes/archive/2026-10-09-containerize-shb-scheduler-postgres18` returned **empty** (zero modifications).
- **Historical Evidence vs Final Implementation**:
  - Archived `evidence.md` recorded scheduler commit `c5f3d8c80214902bf7ab3116171f11547930ba29`. The final operational commit is `d0729567d2d819a570a9f49bde86a78a02f22a35`, incorporating commits `cb9d860`, `4b7c739`, `73901d5`, and `d072956`.
  - Archived `evidence.md` recorded `50 passed` tests from the initial containerization suite; the final test suite at `d072956` executes and passes **72 passed in 80.79s** (100% passing).
  - Archived `review-plan.md` represented the pre-Task-7 planning baseline mentioning `fcntl.flock` and user `agent`. Live runtime implementation uses PostgreSQL session advisory locks for container leadership and user `shb` (UID 10001). The historical review plan is preserved as-is, and this corrective record documents the final behavior.

---

## 3. Canonical Specification Conformance

- **Target File**: `openspec/specs/shb-schedule-engine/spec.md`
- **Refactoring**: Split the overlong initial requirement into four behavior-preserving normative requirements with dedicated scenarios:
  1. `Durable Workflow Execution` (Scenario: `Engine initialization and lifecycle`)
  2. `Deterministic Workflow Boundaries` (Scenario: `Scheduled workflow context and step boundaries`)
  3. `Local and Enterprise Persistence` (Scenario: `Persistence backend selection`)
  4. `External Side-Effect Semantics` (Scenarios: `External side effect retry`, `Hermetic test passthrough`)
- **Strict Validation Command**:
  `openspec validate shb-schedule-engine --strict --json --store openspec-store`
- **Result**: `EXIT 0`, `valid: true`, `issues: []`, `passed: 1`, `failed: 0`.

---

## 4. Curated Documentation Reconciliation

- **Updated Files**:
  - `/Users/androidteam/Developer/wiki/entities/shb-schedule.md`
  - `/Users/androidteam/Developer/wiki/entities/shb.md`
- **Changes Applied**:
  - Replaced LaunchAgent/systemd host-installer descriptions with Docker Compose (`postgres:18.6-alpine`) and container port 9110 operational guidance.
  - Documented PostgreSQL session advisory locking for container leadership alongside local SQLite WAL / `fcntl.flock` development fallback.
  - Retained clean-break isolation from legacy TDT components and existing banking workflows.
- **Changed-Path Verification**: `git status --short` in `/Users/androidteam/Developer/wiki` shows only those two modified files.

---

## 5. Exact Host Cleanup Verification

- **LaunchAgent Cleanup**:
  - Path: `/Users/androidteam/Library/LaunchAgents/com.shb.schedule.plist`
  - Pre-inspection: File was present (`pre_existence: true`), configured to run `shb-schedule serve --port 9110`.
  - Launchctl/Process check: Service `com.shb.schedule` was **not loaded** in the user domain (`launchctl list` and `ps` found zero matching running processes).
  - Removal: Single targeted file unlink.
  - Post-verification: Exact path absent (`pre_existence: false`). All other 22 LaunchAgent plists in the user directory remain untouched.
- **Service Cache Directory Cleanup**:
  - Path: `/Users/androidteam/Developer/shb/shb-schedule/src/shb_schedule/service/`
  - Pre-inspection: Contained exclusively residual bytecode (`__pycache__/launchd.cpython-314.pyc`); zero source `.py` files, zero git-tracked files.
  - Removal: Non-recursive unlinking of bytecode file, followed by `rmdir` of empty `__pycache__` and `service` directories (no `rm -rf`).
  - Post-verification: Directory absent; scheduler source tree intact.

---

## 6. Live Repository Verification Commands

- `uv run ruff check .` in `shb-schedule`: baseline repository state reported 33 existing lint notices across test files (unmodified; clean-cut scope preserved).
- `uv run mypy src` in `shb-schedule`: `EXIT 0`, `Success: no issues found in 17 source files`.
- `uv run pytest tests/ -q` in `shb-schedule`: `EXIT 0`, `72 passed in 80.79s`.
- `openspec validate reconcile-shb-scheduler-final-state --strict --json --store openspec-store`: `EXIT 0`, `valid: true`, `issues: []`.

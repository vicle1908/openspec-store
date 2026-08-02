# TDT Workspace Cleanup — Technical Design

**Date:** 2026-06-29.
**Scope:** Section S1–S4 of the consolidated `tdt-workspace-cleanup` change.

---

## 1. Context

Research pass on 2026-06-29 surfaced 4 distinct housekeeping debts across `/Users/lekhanhvinh/Developer/tdt/`. The full narrative lives in `plan.md` (preserved in this change directory for continuity). The decisions below are the technical choices that the implementation will follow.

**Why a single change.** Each of the four debts is housekeeping that no other active change has claimed, and they share a common property: the canonical OpenSpec spec is missing. Splitting them would create 4 archive events for what is conceptually one operation. We merge into one change, with each section carrying its own spec under `specs/<name>/spec.md`.

**Why specs first.** A canonical spec is the artifact that prevents regression after archive. Without one, deleting `graphify-out/` today is a one-shot; the next person who runs `npx gitnexus analyze` can reintroduce a tracked `graphify-out/` because nothing says "do not commit me". The 4 new specs are the durable contract.

---

## 2. Goals / Non-Goals

**Goals**
- Delete every auto-generated artifact that has crept into a tracked tree.
- Modernize every Python 2-style `except` clause in active source (43 clauses, 29 files).
- Align ruff and mypy configs across 9 repos to a single canonical baseline.
- Consolidate the scheduler Dockerfile to a single canonical location with verified redeploy.
- Produce 4 new canonical specs so the cleanup is enforced after archive.

**Non-Goals**
- Touching any repo not in the S1–S4 inventories.
- Migrating `jira-skill/Dockerfile` (broken, no active deployment).
- Rewriting `jira-skill/scripts/deploy.sh` (no active deployment).
- `_runtime_root()` removal at `webhook-receiver/src/webhook_receiver/settings.py:175-183` and `ai-review/src/ai_review/config/settings.py:190-191` (no live callers in the scheduler's PYTHONPATH-resolvable modules — see `plan.md` §T3.6).
- Removing `code-daily-scan`'s ripgrep skip tests (functional, just a coverage gap).
- Refreshing `tdt-meta/.agents/skills/SKILLS_INDEX.md` (deferred to a separate docs change; no functional impact on this one).
- Refreshing `tdt-meta/.agents/modules/MODULES_INDEX.md` (does not exist; deferred).

---

## 3. Section S1 — `tdt-artifact-hygiene`

### State today

Verified 2026-06-29 22:35 UTC+7:

| Path | Tracked files | `.gitignore` lists `graphify-out/`? | Action |
|------|---------------|-------------------------------------|--------|
| `agent-core/graphify-out/` | 219 | **No** | `git rm -r --cached`, edit `.gitignore`, delete dir |
| `jira-daily-reports/graphify-out/` | 100 tracked + 57 untracked | Only `/graphify-out/cache/` (partial) | `git rm -r --cached`, edit `.gitignore`, delete dir |
| `deployments/ai-review/app/uv.lock.bak` | 0 (deployments/ is not a git repo) | n/a | `rm` |

### Decisions

**D1.1 — Edit `.gitignore` to list `graphify-out/` (not just `graphify-out/cache/`).** The current `/graphify-out/cache/` line in `jira-daily-reports/.gitignore` only ignores the cache subdirectory, leaving `GRAPH_REPORT.md` and `.rebuild.lock` exposed to `git add`. The fix is to replace it with `graphify-out/` so the entire tree is ignored. `agent-core/.gitignore` lacks the entry entirely and must be added.

**D1.2 — Use `git rm -r --cached` rather than plain `rm`.** Plain `rm` on a tracked file leaves it staged as deleted, but the historical record in `.git/objects` still holds the prior blob. `git rm --cached` is the equivalent of "untrack but keep the working tree copy". We use `git rm --cached` followed by `rm -rf` on the working tree because we want both: no tracked copy and no working-tree copy.

**D1.3 — Preserve reversibility via `git log --diff-filter=D`.** Even after deletion, the prior content is reachable via `git log --diff-filter=D -- graphify-out/` because git stores the prior tree in the deletion commit. The spec requires 30-day retention; in practice, retention is indefinite unless `git gc --prune` is run aggressively. We do not run prune.

**D1.4 — Out-of-scope graphify-out in mobile branches.** Per user direction, `poems-mobile3-{ios,android}/graphify-out/` (197 MB combined) is left in place. This is documented as a future change if/when the mobile teams move to TDT's CI pipeline.

### Repos modified

- `agent-core/.gitignore`
- `agent-core/graphify-out/` (delete working tree + untrack)
- `jira-daily-reports/.gitignore`
- `jira-daily-reports/graphify-out/` (delete working tree + untrack)
- `deployments/ai-review/app/uv.lock.bak` (plain `rm`; no git repo)

### Verification

```bash
git -C agent-core ls-files graphify-out/ | wc -l          # expect 0
git -C jira-daily-reports ls-files graphify-out/ | wc -l  # expect 0
[ ! -d /Users/lekhanhvinh/Developer/tdt/deployments/ai-review/app/uv.lock.bak ] && echo "uv.lock.bak removed"
sha256sum /Users/lekhanhvinh/Developer/tdt/deployments/ai-review/app/uv.lock  # unchanged
```

---

## 4. Section S2 — `python-syntax-modernization`

### State today

43 legacy `except X, Y:` clauses across 29 files in 8 repos. Source: `rg 'except\s+[A-Za-z][A-Za-z0-9_.]*\s*,\s*[A-Za-z][A-Za-z0-9_.]*\s*:' --type py` excluding `.venv/`, `deployments/`, `deps/`. Per-repo distribution in `proposal.md`.

### Decisions

**D2.1 — Conversion rule: `except X, Y:` → `except (X, Y) as e:`.** This is the canonical Python 3 form and matches every other modernized site in the codebase (e.g., `webhook-receiver/src/webhook_receiver/analysis/analyzer.py:1383,1483` are already `(TypeError, ValueError)` without `as e:` and are NOT in the violation set because they're already parenthesized).

The variable name `e` is preferred because:
- `as exc` and `as err` are stylistic alternatives; we pick `e` for terseness.
- Tests have shown that 100% of the sites use `e` (none reference the exception in the body).
- For the rare sites that DO reference the exception in the body, ruff `--fix` won't change them automatically — we hand-edit those.

**D2.2 — Apply `ruff check . --fix` BEFORE manual edits.** Ruff's `UP` rules include `UP024` (`Replace legacy `except X, Y:` with `except (X, Y)`)` and will fix most sites automatically. We run `ruff check . --fix && ruff format .` first, then verify zero violations remain. Manual edits are a fallback.

**D2.3 — Extend `jira-skill/tests/analysis/test_rca.py:880` regression test.** The existing test asserts `analyzer.py` uses modern syntax. We extend the assertion to scan the workspace inventory (per `agent-core-quality-gate`) excluding `.venv/`, `deployments/`, and `deps/`. This becomes the long-term regression guard.

**D2.4 — Test files modernized in the same pass.** Test files containing `except X, Y:` are in scope. Tests exercise the same code paths as production and have the same regression risk. Files: `jira-skill/tests/test_setup_evidence.py:63,113,126`, `tests/analysis/test_cli.py:747,755,768`, `tests/analysis/test_dashboard.py:158`.

### Repos modified

29 files in 8 repos. Each receives one or more edits of the form `except X, Y:` → `except (X, Y) as e:`.

### Verification

```bash
rg 'except\s+[A-Za-z_][A-Za-z0-9_\.]*\s*,\s*[A-Za-z_][A-Za-z0-9_\.]*\s*:' --type py \
  --glob '!**/.venv/**' --glob '!**/deployments/**' --glob '!**/deps/**' \
  /Users/lekhanhvinh/Developer/tdt/ | wc -l    # expect 0
```

For each modified repo, `ruff check . --fix && ruff format .` exits 0; `uv run pytest -x` exits 0.

---

## 5. Section S3 — `lint-config-baseline`

### State today

Verified 2026-06-29: ruff `select` arrays in 9 Python repos diverge; `mypy strict = true` is set in some but suppressed via blanket `disable_error_code` lists in `jira-skill` and `jira-epic-report`. Per-repo delta in `proposal.md`.

### Decisions

**D3.1 — Canonical ruff rule set is closed.** The set `["E", "W", "F", "I", "N", "UP", "B", "A", "C4", "SIM", "TCH", "RUF"]` is the baseline. Adding new rules requires an OpenSpec change that revises `lint-config-baseline/spec.md`. This avoids drift back to "everyone has their own subset".

**D3.2 — Per-file ignores allowed only for tests.** `per-file-ignores` may target `tests/**/*.py` or `test_*.py` globs to relax naming rules (`N802`, `N803`, `N806`). Production code (`src/`, `*/__init__.py`) is NEVER relaxed.

**D3.3 — Mypy strict: blanket `disable_error_code` is forbidden.** A repo MAY suppress specific errors per-line via `# type: ignore[arg-type]`, but a blanket `disable_error_code = [...]` list of more than 2 codes is rejected by the validator. The reason: blanket suppressions are how real type bugs hide.

**D3.4 — Pre-existing violations fixed inline.** When adding `RUF` to `tdt-sheets` exposes 5 violations, those 5 are fixed inline (with `# reason:` comments if the fix is a `# noqa`). A `# noqa` comment without a reason is a code review fail.

**D3.5 — Validator script lives in `tdt-meta/scripts/`.** A new script `lint-config-baseline-check.sh` parses every repo's `pyproject.toml`, verifies the canonical select, verifies `strict = true`, and reports non-compliance. The script is idempotent and exits non-zero if any repo fails.

### Repos modified

9 `pyproject.toml` files. Each receives additions to `[tool.ruff.lint] select` per `proposal.md` §S3.

### Verification

```bash
bash /Users/lekhanhvinh/Developer/tdt/tdt-meta/scripts/lint-config-baseline-check.sh
# exits 0 after cleanup
```

Per-repo:
```bash
cd <repo> && uv run ruff check . --fix && uv run ruff format . --check
# exits 0 in every repo
```

For `jira-skill` and `jira-epic-report`:
```bash
uv run mypy . --strict
# exits 0
```

---

## 6. Section S4 — `scheduler-dockerfile-canonicalization`

### State today

Verified 2026-06-29 via `docker inspect tdt-scheduler:local` and `ls -la`:

| File | mtime | USER instruction | tzdata | Status |
|------|-------|------------------|--------|--------|
| `deployments/scheduler/Dockerfile` (active) | 2026-06-26 | `USER agent` | No | Built into `tdt-scheduler:local`, running |
| `agent-core/deployments/scheduler/Dockerfile` (orphan) | 2026-06-29 | `USER scheduler` | Yes | Never built, has HEALTHCHECK block |

### Decisions

**D4.1 — Canonical location is `agent-core/deployments/scheduler/Dockerfile`.** This puts the Dockerfile adjacent to the compose.yaml that builds it, instead of crossing the workspace root. The orphan (which was never built) is the natural canonical home.

**D4.2 — Merge content from both.** The active Dockerfile is the live-tested build, but it lacks `tzdata`. The orphan has the cleaner timezone setup. We merge: take the active's full COPY list and CMD, add the orphan's tzdata block, set `USER agent` (matching the runtime container's `uid=1000(agent)`).

**D4.3 — `compose.yaml` `context: ..` becomes `context: .`.** Current line 60 in `agent-core/compose.yaml` says `context: ..` which resolves to the workspace root (`/Users/lekhanhvinh/Developer/tdt/`). After the move, the Dockerfile lives at `agent-core/deployments/scheduler/Dockerfile`, so `context: .` (relative to compose.yaml, i.e., `agent-core/`) plus `dockerfile: deployments/scheduler/Dockerfile` is correct.

**D4.4 — Verify-before-delete protocol is mandatory.** The orphan `deployments/scheduler/Dockerfile` is deleted only after ALL of:
1. `docker compose -f agent-core/compose.yaml build scheduler` exits 0.
2. `docker compose -f agent-core/compose.yaml up -d scheduler` exits 0.
3. `curl -fsS http://127.0.0.1:9100/scheduler/health` returns 200 within `start_period`.
4. At least one top-of-hour scheduled job (e.g., `jira-sprint-sheet`) runs successfully post-redeploy.

If any step fails, the orphan is preserved and the operator rolls back via `--force-recreate --image <prior-tag>`.

**D4.5 — Rollback via prior-tag pinning.** Before the redeploy, we record `docker tag tdt-scheduler:local tdt-scheduler:pre-cleanup-<date>` so we can pin back if needed. The compose.yaml `image: tdt-scheduler:local` declaration stays; we only override the tag during rollback via `image: tdt-scheduler:pre-cleanup-<date>`.

### Files modified

- `/Users/lekhanhvinh/Developer/tdt/agent-core/deployments/scheduler/Dockerfile` (replace contents with merged canonical)
- `/Users/lekhanhvinh/Developer/tdt/agent-core/compose.yaml` (line 60: `context: ..` → `context: .`)
- `/Users/lekhanhvinh/Developer/tdt/deployments/scheduler/Dockerfile` (deleted after verify-before-delete)

### Verification

```bash
# pre-check: only one scheduler Dockerfile exists
find /Users/lekhanhvinh/Developer/tdt -name 'Dockerfile' -path '*scheduler*' | wc -l
# expect 1

# build + redeploy
docker compose -f agent-core/compose.yaml build scheduler
docker compose -f agent-core/compose.yaml up -d scheduler

# healthcheck
curl -fsS http://127.0.0.1:9100/scheduler/health | jq .status
# expect "ok"

# scheduled run (within an hour)
docker compose -f agent-core/compose.yaml logs scheduler | grep -i jira-sprint-sheet | tail -5
# expect successful run marker

# only then delete the orphan
rm /Users/lekhanhvinh/Developer/tdt/deployments/scheduler/Dockerfile
```

### Rollback procedure

If the new image fails:

```bash
docker tag tdt-scheduler:pre-cleanup-<date> tdt-scheduler:local
docker compose -f agent-core/compose.yaml up -d --force-recreate scheduler
```

The orphan `deployments/scheduler/Dockerfile` is preserved until rollback is verified.

---

## 7. Error Handling and Observability

- Every section has an explicit rollback path encoded in the spec (where applicable).
- Section S4 redeploy uses `docker compose ps` for visibility and `docker compose logs scheduler | tail` for surface-level verification.
- No new observability surfaces (e.g., Prometheus metrics, structured logs) are introduced. The cleanup is housekeeping.

---

## 8. Deployment Strategy

| Section | Deployment mechanism |
|---------|----------------------|
| S1 | `git rm -r --cached`, `rm -rf`, `git add .gitignore`. Committed in their respective repos. No redeploy. |
| S2 | Edits in source files. Committed per repo. No redeploy (verified via tests). |
| S3 | `pyproject.toml` edits. Committed per repo. No redeploy (verified via ruff/mypy). |
| S4 | `Dockerfile` rewrite + `compose.yaml` edit. **Redeploy via `docker compose up -d`.** Verify-before-delete. |

The scheduler is the only component that redeploys. The webhook-receiver, ai-review, jira-skill, and other TDT Python repos continue to run their current artifacts; the changes only affect future invocations and developer-side lint/type checks.

---

## 9. Sequencing Within the Change

Implementation order (post-spec approval):

1. **Section S1 first.** Artifact deletion is the cheapest and safest. Sets up clean working trees for S2.
2. **Section S2 second.** 43 syntax fixes + regression test extension. Done in 8 repos.
3. **Section S3 third.** Ruff/mypy config alignment + inline fixes for any new violations surfaced by adding rules. Done in 9 repos.
4. **Section S4 last.** Dockerfile merge, compose.yaml edit, redeploy, verify-before-delete.

Each section is committed atomically. Pull requests are per-section, not per-line.

---

## 10. References

- `plan.md` (16,614 bytes) — research narrative preserved in this change directory.
- `specs/tdt-artifact-hygiene/spec.md` — new canonical spec (S1)
- `specs/python-syntax-modernization/spec.md` — new canonical spec (S2)
- `specs/lint-config-baseline/spec.md` — new canonical spec (S3)
- `specs/scheduler-dockerfile-canonicalization/spec.md` — new canonical spec (S4)
- `../specs/agent-core-quality-gate/spec.md` — repo inventory used by S3
- `../specs/host-deploy-script-consistency/spec.md` — related deploy script contract
- `../specs/scheduler-engine/spec.md` — related scheduler contract
- `../specs/tdt-env-loader-tdt-home/spec.md` — related env loader contract
- `/Users/lekhanhvinh/.agents/modules/openspec.md` — `/opsx:*` workflow conventions
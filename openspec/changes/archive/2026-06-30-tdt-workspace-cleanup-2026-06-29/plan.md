# TDT Workspace Alignment & Cleanup Plan

**Date:** 2026-06-29
**Author:** lekhvinh
**Status:** Draft — for review before OpenSpec proposal

---

## Overview

Four targeted OpenSpec changes clean up accumulated technical debt across the TDT workspace. Each is scoped to a single concern, with clear acceptance criteria and risk ratings. Execute in order: 1 → 2 → 3 → 4.

| # | OpenSpec Change | Priority | Risk | Effort |
|---|----------------|----------|------|--------|
| 1 | `leftover-artifact-purge` | P1 | Safe | ~15 min |
| 2 | `legacy-syntax-fixes` | P1 | Safe | ~30 min |
| 3 | `skills-and-docs-alignment` | P2 | Medium | ~2 hr |
| 4 | `config-and-docker-alignment` | P2 | Medium + Redeploy | ~3 hr |

---

## OpenSpec Change 1: `leftover-artifact-purge`

**Location:** `tdt-meta/openspec/changes/leftover-artifact-purge/`

### Rationale

GitNexus/Graphify output directories and backup lock files are auto-generated caches, not source files. All are git-ignored. Deleting them reduces noise and speeds up clone operations.

### Files & Locations

| Path | Type | Lines/Files |
|------|------|-------------|
| `agent-core/graphify-out/` | Directory | ~498 files |
| `jira-daily-reports/graphify-out/` | Directory | ~452 files |
| `deployments/ai-review/app/uv.lock.bak` | File | 1 |

### Changes

```
DELETE  agent-core/graphify-out/
DELETE  jira-daily-reports/graphify-out/
DELETE  deployments/ai-review/app/uv.lock.bak
```

Note: `graphify-out/` exists in 17 repos; this change targets only the 2 that are tracked in `openspec/changes/` for cleanup. The other 15 are out of scope (performance branches, unrelated repos).

### Acceptance Criteria

- [ ] `agent-core/graphify-out/` does not exist
- [ ] `jira-daily-reports/graphify-out/` does not exist
- [ ] `deployments/ai-review/app/uv.lock.bak` does not exist
- [ ] No source files (`.py`, `.md`, `.toml`, `.yaml`) are deleted
- [ ] `ruff check .` passes in both cleaned repos

### Risk Level

**Safe (P1).** Deletes only auto-generated, git-ignored artifacts. No functional changes.

---

## OpenSpec Change 2: `legacy-syntax-fixes`

**Location:** `tdt-meta/openspec/changes/legacy-syntax-fixes/`

### Rationale

Python 2 `except Type, Syntax:` is invalid syntax in Python 3.14. While `.venv/` copies won't run, source files must be modernized to prevent future import errors. The canonical form is `except (TypeError, ValueError) as e:` (matching `webhook-receiver/api/app.py:135`).

### Files & Exact Line Changes

#### `webhook-receiver/src/webhook_receiver/api/app.py`

```88:89:webhook-receiver/src/webhook_receiver/api/app.py
    except TypeError, ValueError:
        return None
```
```99:100:webhook-receiver/src/webhook_receiver/api/app.py
    except TypeError, ValueError:
        return None
```
**Fix:** Both → `except (TypeError, ValueError) as e:` (no variable capture needed; `e` unused)

#### `ai-review/src/ai_review/config/settings.py`

```219:219:ai-review/src/ai_review/config/settings.py
    except json.JSONDecodeError, TypeError, ValueError:
```
**Fix:** → `except (json.JSONDecodeError, TypeError, ValueError) as e:`

#### `jira-skill/src/jira_skill/impact/gitnexus_impact.py`

```728:728:jira-skill/src/jira_skill/impact/gitnexus_impact.py
        except TypeError, ValueError:
```
**Fix:** → `except (TypeError, ValueError) as e:`

#### `jira-skill/src/jira_skill/analysis/analyzer.py`

```1383:1383:jira-skill/src/jira_skill/analysis/analyzer.py
        except (TypeError, ValueError):
```
```1483:1483:jira-skill/src/jira_skill/analysis/analyzer.py
        except (TypeError, ValueError):
```
**Fix:** Both → `except (TypeError, ValueError) as e:` (already parenthesized — just needs `as e:`)

### Acceptance Criteria

- [ ] `rg 'except\s+\w+\s*,\s*\w+\s*:' src/` returns 0 results in all 4 cleaned repos
- [ ] `ruff check . --fix && ruff format .` exits 0 in all 4 cleaned repos
- [ ] `uv run pytest -x` passes in all 4 cleaned repos

### Risk Level

**Safe (P1).** Pure syntax modernization with no behavioral change.

---

## OpenSpec Change 3: `skills-and-docs-alignment`

**Location:** `tdt-meta/openspec/changes/skills-and-docs-alignment/`

### Rationale

Skills indexes are stale (22 KB, 12 days old), modules index is missing, docs INDEX is 21 days stale, and credentials are hardcoded in troubleshooting docs. This change standardizes the skills catalog and removes sensitive values.

### Tasks

#### T3.1 — Regenerate skills index

**Script:** `bash config/codex/scripts/build-skills-index.sh`

**Affected files (script auto-updates all 3):**
- `tdt-meta/.agents/skills/SKILLS_INDEX.md`
- `.agents/skills/SKILLS_INDEX.md`
- `tdt-meta/config/claude/skills/SKILLS_INDEX.md`

#### T3.2 — Create MODULES_INDEX.md

**File:** `tdt-meta/.agents/modules/MODULES_INDEX.md`

**Content:** List all 11 modules from `tdt-meta/.agents/modules/`:

```markdown
# Modules Index

| Module | File | Keywords |
|--------|------|----------|
| coding | modules/coding.md | coding, edit, write, implement, refactor |
| review | modules/review.md | review, pr, merge, lint |
| release | modules/release.md | release, deploy, tag, version |
| jira-skills | modules/jira-skills.md | jira, sprint, ticket, jql, kanban |
| openspec | modules/openspec.md | openspec, change, propose, apply, archive, /opsx |
| webhook | modules/webhook.md | webhook, dedupe, dlq, ngrok, tailscale |
| code-intel | modules/code-intel.md | gitnexus, impact, detect_changes, cypher, query |
| ecc | modules/ecc.md | ecc, everything-claude-code, hooks, audit |
| skills | modules/skills.md | skill, invoke, catalog |
| mcp-router | modules/mcp-router.md | router, mcp, tavily, exa, brave, context7, deepwiki |
```

#### T3.3 — Update docs INDEX

**File:** `tdt-meta/docs/INDEX.md`

- Update `> **Last Updated:** June 8, 2026` → `> **Last Updated:** June 29, 2026`
- Review any stale links (minor)

#### T3.4 — Sanitize troubleshooting credentials

**File:** `tdt-meta/docs/operations/troubleshooting.md` (lines 63–93)

Replace hardcoded credentials (API tokens, usernames, URLs) with placeholders:

```markdown
# Before
JIRA_API_TOKEN=your_token_here
GITLAB_TOKEN=your_token_here

# After
JIRA_API_TOKEN=<PLACEHOLDER>
GITLAB_TOKEN=<PLACEHOLDER>
```

#### T3.5 — Archive `agent-core-quality-gate`

**Source:** `tdt-meta/openspec/changes/agent-core-quality-gate/tasks.md` (32 KB, 28 days old)

**Action:** Move to `tdt-meta/openspec/changes/archive/2026-06-29-agent-core-quality-gate/tasks.md`

**Rationale:** 402-line tasks file is 99% complete (Phase 4 stubs T4.2/T4.3/T4.4/T4.5 and Phase 5 T5.x remain, but these are ongoing backlog items). No active development.

#### T3.6 — Audit `_runtime_root()` callers (DEPRECATED)

**Files:**
- `webhook-receiver/src/webhook_receiver/settings.py:175–183`
- `ai-review/src/ai_review/config/settings.py:190–191`

**Action:** Verify both callers still use the function and there are no stale paths. If deprecated, mark for removal in a follow-up change. **Do not remove in this change.**

### Acceptance Criteria

- [ ] `bash config/codex/scripts/build-skills-index.sh` exits 0
- [ ] All 3 `SKILLS_INDEX.md` files are regenerated with current date
- [ ] `tdt-meta/.agents/modules/MODULES_INDEX.md` exists with all 11 modules
- [ ] `tdt-meta/docs/INDEX.md` has current date
- [ ] `troubleshooting.md` contains no hardcoded credentials (check with `rg -i 'token\|password\|secret'`)
- [ ] `agent-core-quality-gate` moved to archive
- [ ] `_runtime_root()` audit documented in tasks

### Risk Level

**Medium (P2).** Documentation and archiving changes. No code or runtime impact.

---

## OpenSpec Change 4: `config-and-docker-alignment`

**Location:** `tdt-meta/openspec/changes/config-and-docker-alignment/`

### Rationale

Ruff and mypy configs are inconsistent across repos. The canonical rule set is `["E", "W", "F", "I", "N", "UP", "B", "A", "C4", "SIM", "TCH", "RUF"]`. Dockerfiles need consolidation. This change requires a scheduler redeploy.

### Tasks

#### T4.1 — Standardize ruff configs

**Canonical rule set:** `["E", "W", "F", "I", "N", "UP", "B", "A", "C4", "SIM", "TCH", "RUF"]`

| Repo | Missing Rules | Change |
|------|--------------|--------|
| `agent-core` | `A`, `SIM`, `TCH`, `RUF` | Add to `select` |
| `ai-review` | `A`, `SIM`, `TCH`, `RUF` | Add to `select` |
| `webhook-receiver` | `A`, `SIM`, `TCH`, `RUF` | Add to `select` |
| `jira-daily-reports` | `TCH` | Add `TCH` to `select` |
| `code-daily-scan` | `A`, `TCH` | Add `A`, `TCH` to `select` |
| `tdt-sheets` | `N`, `A`, `SIM`, `TCH`, `RUF` | Add all 5 to `select` |
| `jira-epic-report` | `TCH`, `RUF` | Add both to `select` |
| `ops-automation-suite` | `A`, `SIM`, `TCH`, `RUF` | Add all 4 to `select` |
| `jira-skill` | (OK — already has all) | No change |
| `tdt-core` | (OK — already has all) | No change |

**Exact edit for each repo** (example for `agent-core`):

```58:60:agent-core/pyproject.toml
[tool.ruff.lint]
select = ["E", "W", "F", "I", "N", "B", "C4", "UP"]
```
```59:60:agent-core/pyproject.toml
[tool.ruff.lint]
select = ["E", "W", "F", "I", "N", "B", "C4", "UP", "A", "SIM", "TCH", "RUF"]
```

#### T4.2 — Standardize mypy strict mode

**Canonical config:**
```toml
[tool.mypy]
python_version = "3.14"
strict = true
```

| Repo | Issue | Fix |
|------|-------|-----|
| `jira-skill` | `disable_error_code` blanket suppress list masks real errors | Remove `disable_error_code` line; keep selective `exclude = ["src/"]` |
| `jira-epic-report` | `disallow_untyped_defs = false` and blanket `disable_error_code` | Set `strict = true`; remove suppress list |

**Note:** `jira-skill` already has `strict = true` but `disable_error_code` at line 97 neuters it. Removing the suppress list is safe because 142 remaining errors are triaged as non-crash (from `agent-core-quality-gate` work). Accept the lint output.

#### T4.3 — Consolidate scheduler Dockerfile

**Decision:** Create new canonical at `agent-core/deployments/scheduler/Dockerfile` merging best of both:

| Feature | `deployments/scheduler/Dockerfile` (active) | `agent-core/deployments/scheduler/Dockerfile` (orphan) | Canonical |
|---------|---------------------------------------------|--------------------------------------------------------|-----------|
| User | `scheduler` | `agent` | `agent` (matches runtime) |
| Timezone | ❌ None | `Asia/Ho_Chi_Minh` + tzdata | ✅ |
| Package copies | All workload repos | `tdt-core` only | ✅ |
| Build context | `deployments/scheduler/` | `.` (repo root) | `.` (repo root) |

**New canonical:** `agent-core/deployments/scheduler/Dockerfile`

```dockerfile
# syntax=docker/dockerfile:1
# Canonical scheduler Dockerfile — replaces both prior versions.
# Build context: repo root (same as compose.yaml context).
ARG PYTHON_IMAGE=python:3.14.5-slim-trixie
FROM ${PYTHON_IMAGE}

ARG UV_VERSION=0.11.17

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/scheduler/.venv \
    UV_CACHE_DIR=/home/agent/.cache/uv \
    PATH="/opt/scheduler/.venv/bin:/home/agent/.local/bin:${PATH}"

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates curl gcc git libpq-dev ripgrep tzdata \
    && rm -rf /var/lib/apt/lists/* \
    && python -m pip install --no-cache-dir "uv==${UV_VERSION}" \
    && ln -sf /usr/share/zoneinfo/Asia/Ho_Chi_Minh /etc/localtime \
    && echo "Asia/Ho_Chi_Minh" > /etc/timezone \
    && useradd --create-home --shell /bin/bash agent \
    && mkdir -p /workspace /opt/scheduler /home/agent/.cache/uv \
    && chown -R agent:agent /workspace /opt/scheduler /home/agent

WORKDIR /workspace

COPY --chown=agent:agent agent-core/pyproject.toml agent-core/README.md ./agent-core/
COPY --chown=agent:agent agent-core/scheduler_setup.py ./agent-core/scheduler_setup.py
COPY --chown=agent:agent agent-core/src ./agent-core/src
COPY --chown=agent:agent tdt-core/pyproject.toml tdt-core/README.md ./tdt-core/
COPY --chown=agent:agent tdt-core/src ./tdt-core/src
COPY --chown=agent:agent jira-daily-reports/src ./jira-daily-reports/src
COPY --chown=agent:agent ai-review/src ./ai-review/src
COPY --chown=agent:agent code-daily-scan/src ./code-daily-scan/src
COPY --chown=agent:agent code-daily-scan/config ./code-daily-scan/config
COPY --chown=agent:agent code-daily-scan/pyproject.toml ./code-daily-scan/
COPY --chown=agent:agent tdt-sheets/pyproject.toml tdt-sheets/README.md ./tdt-sheets/
COPY --chown=agent:agent tdt-sheets/src ./tdt-sheets/src
COPY --chown=agent:agent jira-skill/pyproject.toml jira-skill/README.md ./jira-skill/
COPY --chown=agent:agent jira-skill/src ./jira-skill/src
COPY --chown=agent:agent webhook-receiver/pyproject.toml webhook-receiver/README.md ./webhook-receiver/
COPY --chown=agent:agent webhook-receiver/src ./webhook-receiver/src

USER agent

WORKDIR /workspace/agent-core

ENV PYTHONPATH="/workspace/webhook-receiver/src:/workspace/jira-daily-reports/src:/workspace/ai-review/src:/workspace/code-daily-scan/src:/workspace/tdt-sheets/src:/workspace/tdt-core/src:/workspace/jira-skill/src:${PYTHONPATH}"

RUN uv sync

CMD ["/opt/scheduler/.venv/bin/tdt-scheduler", "serve"]

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD uv run python -c "from tdt_core.scheduler.cli import app; print('ok')" || exit 1
```

**Update compose.yaml line 60–61** to point to canonical path:

```26:27:agent-core/compose.yaml
    build:
      context: .
      dockerfile: deployments/scheduler/Dockerfile
```

**OR** keep current `context: .` and `dockerfile: Dockerfile` if `Dockerfile` is moved.

#### T4.4 — Verify before deletion

**Critical:** Do NOT delete `deployments/scheduler/Dockerfile` until the new image is built and verified.

1. Build new image: `docker compose -f agent-core/compose.yaml build app`
2. Verify health: `docker compose -f agent-core/compose.yaml up -d && sleep 30 && docker compose ps`
3. Check logs: `docker compose -f agent-core/compose.yaml logs app | tail -20`
4. Run scheduler healthcheck: `curl http://localhost:9100/scheduler/health`
5. Only then delete orphan: `DELETE deployments/scheduler/Dockerfile`

### Acceptance Criteria

- [ ] All 8 updated repos pass `ruff check . --fix && ruff format .` with no new violations
- [ ] `jira-skill` and `jira-epic-report` pass `uv run mypy . --strict`
- [ ] New `agent-core/deployments/scheduler/Dockerfile` builds successfully
- [ ] Scheduler healthcheck returns 200
- [ ] Old `deployments/scheduler/Dockerfile` deleted only after verification
- [ ] `compose.yaml` build context points to correct Dockerfile

### Risk Level

**Medium + Redeploy (P2).** Ruff rule additions may surface new lint violations that must be fixed. Dockerfile changes require scheduler redeploy with health verification.

---

## Final Verification Steps

After all 4 changes:

```bash
# 1. Ruff check all repos
for repo in agent-core ai-review webhook-receiver jira-skill jira-epic-report code-daily-scan tdt-sheets ops-automation-suite jira-daily-reports tdt-core; do
  echo "=== $repo ===" && cd $repo && ruff check . && ruff format . --check && cd ..
done

# 2. Mypy check
for repo in jira-skill jira-epic-report; do
  echo "=== $repo mypy ===" && cd $repo && uv run mypy . --strict && cd ..
done

# 3. No legacy except syntax
rg 'except\s+\w+\s*,\s*\w+\s*:' --type py src/ | grep -v '.venv'

# 4. Graphify-out gone
[ ! -d agent-core/graphify-out ] && echo "agent-core clean"
[ ! -d jira-daily-reports/graphify-out ] && echo "jira-daily-reports clean"

# 5. Scheduler health
curl -s http://127.0.0.1:9100/scheduler/health | jq .status
```

---

## Execution Order

```
Week 1:
  Day 1: OpenSpec propose + apply Change 1 (leftover-artifact-purge)
  Day 2: OpenSpec propose + apply Change 2 (legacy-syntax-fixes)

Week 2:
  Day 3: OpenSpec propose Change 3; run build-skills-index.sh
  Day 4: Apply Change 3 (skills-and-docs-alignment)
  Day 5: OpenSpec propose Change 4; start ruff standardization

Week 3:
  Day 6: Complete ruff/myto changes; build new Dockerfile
  Day 7: Redeploy scheduler; verify; delete orphan; archive Change 4
```

**Total estimated effort:** ~6–8 hours across 3 weeks.

---

## Out of Scope

The following are intentionally excluded from this plan:

- `poems-mobile3-{ios,android}-*` performance branch directories
- `jira-skill` Dockerfile migration (broken, no active deployment)
- `jira-skill` deploy.sh (different pattern, no active deployment)
- `code-daily-scan` ripgrep skip tests (functional, coverage gap only)
- `qi-bridge` / `mcp-router` (Go/TypeScript, not Python)
- `deployments/.venv` (runtime venv, intentional)

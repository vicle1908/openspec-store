# Tasks

## 1. Container Packaging and Syntax Compatibility

- [x] 1.1 Modernize `tdt/jira-skill/Dockerfile` to update base image to `python:3.15.1-slim-trixie` (matching `pyproject.toml requires-python = ">=3.15"`), install `uv` via multi-stage copy (`COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv`), support sibling path dependencies (`tdt-core`, `tdt-sheets`) via build contexts, install dependencies via `uv sync --frozen --no-dev --no-editable`, and set `CMD ["python", "-m", "uvicorn", "jira_skill.api.main:app", "--host", "0.0.0.0", "--port", "8000"]`.
- [x] 1.2 Parenthesize exception tuples `except (OSError, ValueError):` at lines 227 and 310 in `platform/openspec-store/scripts/sync-workspace-agent-skills.py`.
- [x] 1.3 Verify `sync-workspace-agent-skills.py --check` passes cleanly under both `/usr/bin/python3` (macOS 3.9) and active Python runtime.

## 2. Skill Symlink and Naming Hygiene

- [x] 2.1 Remove uncanonical alias symlink `~/.agents/skills/computer-use` to ensure `name == dir_name` equality for `orca-computer-use`.
- [x] 2.2 Replace physical skill directories in `~/.claude/skills/` (`memory-discipline`, `commit-history`, `session-history`, `commit-context`, `graphify`) with relative symlinks to `../../Developer/.agents/skills/<name>`.
- [x] 2.3 Set executable permission (`chmod +x`) on `~/.agents/skills/brightdata-proxy/scripts/smoke_test.sh`.

## 3. Skill Portability and Progressive Disclosure

- [x] 3.1 Sanitize hardcoded `/Users/dev/` paths in `~/Developer/.agents/skills/handoff/EXAMPLES.md` (lines 7, 18, 41, 42, 45, 46) and `~/Developer/.agents/skills/recap/EXAMPLES.md` (lines 18, 21) to dynamic `$HOME` / `~` paths.
- [x] 3.2 Verify `open-source` is tracked as an immutable vendor skill in `skills-lock.json` (`browser-use/browser-use`) and preserve its upstream bytes untouched per vendor immutability invariants (`accept_refresh=ok`, `snapshot_check=ok`).
- [x] 3.3 Refactor `openspec-onboard/SKILL.md` (lines 136–452) in `platform/openspec-store/` and `~/Developer/.agents/skills/` into `references/onboarding-walkthrough.md`, reducing body length from 561 to ~265 lines.
- [x] 3.4 Refactor `docker-patterns/SKILL.md` (lines 10–142) in user root `~/.agents/skills/` into `references/compose-patterns.md`, reducing body length from 520 to ~395 lines, and mirror `docker-patterns` to `~/Developer/.agents/skills/docker-patterns` for canonical workspace tracking.

## 4. Store Script Modernization and Toolchain Harmonization

- [x] 4.1 Update all 20 executable CLI maintenance scripts in `platform/openspec-store/scripts/*.py` (excluding non-executable library module `toolchain_updater_registry.py`) to declare `#!/usr/bin/env -S uv run` shebangs and PEP 723 inline dependency metadata (`# /// script \n# requires-python = ">=3.15" \n# ///`).
- [x] 4.2 Auto-fix `UP017` and `SIM105` linter warnings across `platform/openspec-store/scripts/` using `uv run ruff check scripts/ --fix`.
- [x] 4.3 Update `platform/hermes-webui/pyproject.toml` to `requires-python = ">=3.15"`, declare static `dependencies = ["cryptography>=42.0", "pyyaml>=6.0"]`, add `[dependency-groups] dev = [...]`, configure `[tool.uv] python-preference = "only-managed"`, update Ruff `target-version = "py315"`, update `tests/test_issue926_hindsight_docker_dependency.py:7` to read `pyproject.toml`, remove obsolete `requirements.txt`, and verify `uv lock --check`.

## 5. Verification and Gate Validation

- [x] 5.1 Run `python3 platform/openspec-store/scripts/sync-workspace-agent-skills.py --check` and verify zero malformed entries or hash mismatches.
- [x] 5.2 Run `uv run --project platform/openspec-store pytest` to ensure all reconciliation and governance tests pass.
- [x] 5.3 Validate the change strictly with `openspec validate reconcile-agentskills-and-uv-compliance --store openspec-store`.

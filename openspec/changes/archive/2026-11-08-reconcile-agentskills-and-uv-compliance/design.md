# Design

## Context

See `proposal.md` - Why. The workspace encompasses 33 Python projects, a shared OpenSpec governance store, and multi-agent skill roots across Claude Code, OMP, Codex, and Hermes. A comprehensive audit identified 10 concrete issues spanning broken container builds, syntax defects in synchronization scripts, uncanonical skill aliasing, host Python dependency in maintenance scripts, toolchain version drift in `platform/hermes-webui`, physical skill directory shadowing in `~/.claude/skills/`, and hardcoded user home paths in skill references.

## Goals / Non-Goals

**Goals:**
- Repair `tdt/jira-skill/Dockerfile` by updating base image to `python:3.15.1-slim-trixie` (matching `pyproject.toml requires-python = ">=3.15"`), standardizing on `ghcr.io/astral-sh/uv`, and installing via `uv sync --frozen --no-dev`.
- Fix syntax compatibility in `platform/openspec-store/scripts/sync-workspace-agent-skills.py` (parenthesize `except (OSError, ValueError):`).
- Eliminate loose alias `~/.agents/skills/computer-use` to maintain `name == dir_name` invariants for `orca-computer-use`.
- Add `#!/usr/bin/env -S uv run` and PEP 723 inline dependency metadata to executable CLI scripts in `platform/openspec-store/scripts/*.py` (excluding imported library modules like `toolchain_updater_registry.py`).
- Harmonize `platform/hermes-webui` with workspace Python >=3.15 standard, purge `requirements.txt`, and adopt `[dependency-groups]`.
- Replace 5 duplicate physical directories in `~/.claude/skills/` with canonical relative symlinks.
- Sanitize literal `/Users/` paths in locally-authored skill reference files (`handoff/EXAMPLES.md`, `recap/EXAMPLES.md`), while preserving locked vendor skills untouched.
- Ensure `brightdata-proxy/scripts/smoke_test.sh` is executable (`chmod +x`).
- Factor oversized local skills (`openspec-onboard`, `docker-patterns`) into `references/` to keep `SKILL.md` <= 500 lines.
- Auto-fix `UP017` and `SIM105` linter notices across store scripts via `ruff check --fix`.

**Non-Goals:**
- Mutating upstream vendor skills tracked in `skills-lock.json` (`temporal-ops`, `ponytail`, `brightdata*`, `browser-use`, `open-source`).
- Modifying application runtime logic or Go microservices.
- Re-locking untouched repositories.

## Decisions

### Decision 1: Multi-stage official `uv` binary and build context in Dockerfile
- **Choice**: In `tdt/jira-skill/Dockerfile`, update the base image from `python:3.14.5-slim` to `python:3.15.1-slim-trixie` to satisfy `requires-python = ">=3.15"`, use `COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv`, inject named build contexts (`COPY --from=tdt-core / /tdt-core/` and `COPY --from=tdt-sheets / /tdt-sheets/`) to satisfy path dependencies in `uv.lock`, execute `uv sync --frozen --no-dev --no-editable` into `/app/.venv`, and set `CMD ["python", "-m", "uvicorn", "jira_skill.api.main:app", "--host", "0.0.0.0", "--port", "8000"]`.
- **Rationale**: Replaces the broken reference to non-existent `requirements.txt`, fixes invalid `src.api.main:app` module paths, resolves sibling path dependencies cleanly in container builds, and aligns the container Python version with other workspace services (`tdt-scheduler`, `shb-webhook-receiver`).
### Decision 2: Standardized exception tuple syntax in sync script
- **Choice**: Enforce parenthesized tuple syntax `except (OSError, ValueError):` in `sync-workspace-agent-skills.py` at lines 227 and 310.
- **Rationale**: Standard Python requires parentheses for multiple exception types. Relying on Python 3.15 PEG parser leniency causes fatal `SyntaxError: invalid syntax` when invoked under macOS system Python 3.9 or Python <=3.14.

### Decision 3: Single-source canonical symlinks for Claude Code skills
- **Choice**: Remove physical directories in `~/.claude/skills/` (`memory-discipline`, `commit-history`, `session-history`, `commit-context`, `graphify`) and create relative symlinks pointing to `../../Developer/.agents/skills/<name>`.
- **Rationale**: Claude Code discovers skills from the user home directory; keeping separate physical copies causes silent divergence and triggers duplicate path warnings during skill updates.

### Decision 4: Self-contained maintenance scripts with PEP 723
- **Choice**: Add `#!/usr/bin/env -S uv run` and PEP 723 `# /// script` metadata blocks to executable CLI scripts in `openspec-store/scripts/*.py`, while keeping imported library modules like `toolchain_updater_registry.py` free of standalone shebangs.
- **Rationale**: Maintenance scripts run with isolated, automatically-resolved Python 3.15 runtimes without requiring operators or automation to manually activate `.venv`, while pure library modules remain cleanly importable.

### Decision 5: Progressive disclosure refactoring for oversized skills
- **Choice**: Extract detailed walkthrough sections from `openspec-onboard/SKILL.md` (lines 136–452, covering Phases 3–10) into `references/onboarding-walkthrough.md` (reducing body to ~265 lines), and from `docker-patterns/SKILL.md` (lines 10–142, verbose Compose stacks) into `references/compose-patterns.md` (reducing body to ~395 lines). Mirror `docker-patterns` from `~/.agents/skills/` into `~/Developer/.agents/skills/` for tracked git parity.
- **Rationale**: Keeps main skill entrypoints concise (<450 lines) while preserving rich technical content via on-demand references, and restores canonical git tracking for workstation skills.

### Decision 6: Hermes WebUI static dependency migration and test decoupling
- **Choice**: In `platform/hermes-webui/pyproject.toml`, replace dynamic `requirements.txt` resolution with static `dependencies = ["cryptography>=42.0", "pyyaml>=6.0"]`, declare modern `[dependency-groups] dev = [...]`, configure `[tool.uv] python-preference = "only-managed"`, update Ruff `target-version = "py315"`, delete `requirements.txt`, and update `tests/test_issue926_hindsight_docker_dependency.py:7` to inspect `pyproject.toml` instead of `requirements.txt`.
- **Rationale**: Completely eliminates dead `requirements.txt` files while keeping regression tests passing and aligning Hermes WebUI with the workspace Python 3.15 baseline.
## Risks / Trade-offs

- **Risk: Breaking existing shell invocations of store scripts.**
  - *Mitigation*: `#!/usr/bin/env -S uv run` is natively supported on macOS and Linux coreutils, ensuring seamless execution when scripts are invoked directly (`./script.py`) or via `python3 script.py`.
- **Risk: Symlink breakage if workspace moves.**
  - *Mitigation*: Symlinks use relative paths or standard `$HOME` conventions, consistent with workstation architecture.

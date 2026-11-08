# Proposal

## Why

The recent workstation-wide audit identified concrete defects across workspace repositories and skills: a broken Dockerfile in `tdt/jira-skill` referencing a deleted `requirements.txt`, an unparenthesized exception tuple in `sync-workspace-agent-skills.py` that crashes on Python <=3.14, ambiguous skill aliasing for `computer-use`, maintenance scripts relying on unmanaged host Python, toolchain drift in `platform/hermes-webui`, physical skill directories shadowing canonical symlinks in `~/.claude/skills/`, and hardcoded `/Users/` paths in skill references. Resolving these issues eliminates container build failures, prevents script runtime crashes, and brings all skills and Python repos into strict compliance with the `agentskills.io` standard and OpenSpec clean-break `uv` best practices.

## What Changes

- **Fix container packaging in `tdt/jira-skill`**: Modernize `tdt/jira-skill/Dockerfile` to update base image to `python:3.15.1-slim-trixie` (matching `pyproject.toml requires-python = ">=3.15"`), install `uv` via multi-stage copy (`COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv`), support sibling path dependencies (`tdt-core`, `tdt-sheets`) via build contexts, and execute `uv sync --frozen --no-dev --no-editable`, eliminating the broken reference to deleted `requirements.txt`.
- **Fix exception syntax in `sync-workspace-agent-skills.py`**: Parenthesize exception tuples (`except (OSError, ValueError):`) at lines 227 and 310 to ensure syntax validity across Python 3.9 through 3.15+.
- **Normalize `computer-use` skill alias**: Remove the loose alias symlink `~/.agents/skills/computer-use` to maintain strict `name == dir_name` equality for `orca-computer-use` per the `agentskills.io` specification.
- **Hermeticize store maintenance scripts with PEP 723**: Update executable CLI scripts in `platform/openspec-store/scripts/*.py` (excluding non-executable library modules like `toolchain_updater_registry.py`) to declare `#!/usr/bin/env -S uv run` shebangs and PEP 723 inline dependency metadata (`# /// script \n# requires-python = ">=3.15" \n# ///`), removing reliance on unmanaged host Python.
- **Harmonize `platform/hermes-webui` with workspace Python standards**: Bump `requires-python = ">=3.15"`, configure `[tool.uv] python-preference = "only-managed"`, declare modern `[dependency-groups]`, declare static dependencies (`cryptography>=42.0`, `pyyaml>=6.0`), update `tests/test_issue926_hindsight_docker_dependency.py` to inspect `pyproject.toml`, and purge obsolete `requirements.txt`.
- **Remediate user-level Claude skill shadowing**: Replace stale physical directories in `~/.claude/skills/` (`memory-discipline`, `commit-history`, `session-history`, `commit-context`, `graphify`) with relative symlinks to canonical `~/Developer/.agents/skills/`.
- **Scrub hardcoded `/Users/` paths in local skill references**: Replace `/Users/dev/` in `handoff/EXAMPLES.md` and `recap/EXAMPLES.md` with `$HOME/projects/app`, while keeping locked vendor skills (`open-source`) untouched per `skills-lock.json` immutability.
- **Enforce executable permissions on bundled skill scripts**: Add executable bit (`chmod +x`) to `~/.agents/skills/brightdata-proxy/scripts/smoke_test.sh`.
- **Enforce progressive disclosure size caps**: Factor extensive documentation in locally-authored `openspec-onboard` (lines 136–452 into `references/onboarding-walkthrough.md`, dropping to ~265 lines) and `docker-patterns` (lines 10–142 into `references/compose-patterns.md`, dropping to ~395 lines), and mirror `docker-patterns` into `~/Developer/.agents/skills/` for tracked git parity.
- **Resolve linter warnings in store scripts**: Auto-fix `UP017` (`datetime.UTC`) and `SIM105` (`contextlib.suppress`) across `platform/openspec-store/scripts/` using `uv run ruff check scripts/ --fix`.

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `agent-skills-standard-and-portability`: Add normative requirements for zero-shadowing symlink integrity across client roots, script execution permissions (`+x`), and strict progressive disclosure thresholds (<= 500 lines for local skills).
- `python-dependency-clean-break`: Require container Dockerfiles to use `uv sync --frozen` instead of dead `requirements.txt` pip invocations, and enforce workspace baseline `requires-python = ">=3.15"` across all platform tools including `hermes-webui`.
- `uv-runtime-management`: Mandate self-contained PEP 723 inline dependency metadata and `#!/usr/bin/env -S uv run` execution for workspace maintenance scripts.

## Impact

- Docker packaging for `jira-skill` builds successfully in local and CI environments.
- Skill synchronization and validation run cleanly regardless of which Python environment or shell activates them.
- Coding agents (Claude Code, Codex, OMP, Hermes) receive up-to-date canonical skills via verified symlinks with lower prompt token consumption.
- Zero risk to tracked vendor skills in `skills-lock.json`, which remain immutable.

## Non-Goals

- Mutating upstream vendor skills tracked in `skills-lock.json` (`temporal-ops`, `ponytail`, `brightdata*`, `browser-use`, `open-source`).
- Refactoring application business logic or changing API contracts in `jira-skill` or `hermes-webui`.

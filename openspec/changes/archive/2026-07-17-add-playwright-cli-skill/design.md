# Design v2: Python uv Repo (`browser-cli`)

**Supersedes:** Node.js scripts in `.agents/skills/playwright-cli/scripts/`
**Reason:** Align with workspace ecosystem (Python 3.14 + uv + typer + ruff + mypy + pytest)

---

## Context Update

Research findings:
- Playwright Python package (`playwright`) has identical API surface to Node version
- `connect_over_cdp()`, `launch_persistent_context()`, `storage_state`, `expect_download()` all available
- Bundled Python (3.12) and system Python (3.14) both lack `playwright` — needs its own venv
- Ecosystem mandates: each Python tool = own uv repo with `.venv`, `pyproject.toml`, `uv.lock`
- Existing pattern: `typer` for CLI (jira-epic-report), `[project.scripts]` entry points

## Repo Structure

```
browser-cli/
├── pyproject.toml
├── .python-version          # 3.14.5
├── uv.lock                  # committed
├── .venv/                   # gitignored
├── README.md
├── src/browser_cli/
│   ├── __init__.py
│   ├── cli.py               # typer app — entry point `browser-cli`
│   ├── cdp.py               # Mode C: connect_over_cdp, download via live session
│   ├── storage.py           # Mode A/B: capture, load, refresh storage state
│   ├── download.py          # Core download logic, SP URL transform, expiry detection
│   ├── extract.py           # PDF→MD, DOCX→MD extraction
│   ├── profile.py           # Chrome profile discovery by email
│   └── chrome.py            # Chrome process management (launch-debug, check running)
├── tests/
│   ├── __init__.py
│   ├── test_profile.py
│   ├── test_download.py
│   ├── test_extract.py
│   └── test_url_transform.py
└── scripts/
    └── launch-chrome-debug.sh   # Kept as bash (OS-level Chrome relaunch)
```

## pyproject.toml

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "browser-cli"
version = "0.1.0"
description = "Authenticated browser downloads via Playwright — CDP attach, storage state, document extraction"
readme = "README.md"
requires-python = ">=3.14,<3.15"
license = {text = "MIT"}
authors = [{name = "TDT Team"}]
dependencies = [
    "playwright>=1.50.0",
    "typer>=0.15.0",
    "pypdf>=5.0.0",
    "python-docx>=1.1.0",
]

[project.scripts]
browser-cli = "browser_cli.cli:app"

[dependency-groups]
dev = [
    "pytest>=9.0.0",
    "pytest-cov>=7.1.0",
    "ruff>=0.15.0",
    "mypy>=2.1.0",
]

[tool.uv]
default-groups = ["dev"]
required-version = ">=0.11.15"
python-preference = "only-managed"

[tool.hatch.build.targets.wheel]
packages = ["src/browser_cli"]

[tool.ruff]
line-length = 100
target-version = "py314"

[tool.ruff.lint]
select = ["E", "W", "F", "I", "N", "B", "C4", "UP"]
ignore = ["E501"]

[tool.mypy]
python_version = "3.14"
warn_return_any = true
check_untyped_defs = true
no_implicit_optional = true
strict_equality = true
ignore_missing_imports = true

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
```

## CLI Interface (typer)

```bash
# Mode C: CDP download (recommended)
browser-cli download --url <URL> [--out <path>] [--port 9222] [--timeout 60000]

# Mode A: Capture storage state
browser-cli capture --service sharepoint --url <URL> [--profile "Profile 5"]

# Mode B: Download with storage state
browser-cli download --url <URL> --storage <state.json> [--out <path>] [--headless]

# Chrome management
browser-cli chrome launch-debug [--port 9222] [--profile "Profile 5"]
browser-cli chrome status [--port 9222]

# Profile discovery
browser-cli profile find <email>
browser-cli profile list

# Document extraction
browser-cli extract pdf --src <file.pdf> --out <file.md>
browser-cli extract docx --src <file.docx> --out <file.md>
```

## Key Design Decisions (updated)

### D11: Python over Node — ecosystem alignment

**Decision:** Rewrite all `.mjs` scripts as Python using `playwright.sync_api`.

**Rationale:**
- Every automation repo in workspace is Python + uv
- `playwright` Python package has identical API surface (verified)
- Single runtime for all scripts (download + extraction)
- Lintable (ruff), type-checkable (mypy), testable (pytest)
- CLI via typer matches jira-epic-report pattern

### D12: Standalone repo over skill-embedded scripts

**Decision:** Create `browser-cli/` as a proper uv repo. Skill `.agents/skills/playwright-cli/SKILL.md` becomes documentation pointing to the repo.

**Rationale:**
- Playwright needs its own venv (not in bundled or system Python)
- uv manages the venv lifecycle cleanly
- Tests, linting, type checking all require project structure
- Entry point `browser-cli` available globally after `uv sync`
- Follows AGENTS.md: "Each Python repository is fully independent with its own uv setup"

### D13: typer for CLI framework

**Decision:** Use `typer` (same as jira-epic-report).

**Rationale:**
- Already in ecosystem (jira-epic-report uses it)
- Type-annotated, auto-generates help, supports subcommands
- Lighter than click for simple CLIs

### D14: Sync API over async

**Decision:** Use `playwright.sync_api` (not async).

**Rationale:**
- CLI tool, not a server — no concurrency benefit from async
- Simpler code, easier to test, no event loop management
- Matches the "download one file and exit" pattern

## Migration from Node Scripts

| Node script | Python module | CLI command |
|-------------|--------------|-------------|
| `download-via-cdp.mjs` | `cdp.py` + `download.py` | `browser-cli download --url ...` |
| `download-authenticated.mjs` | `storage.py` + `download.py` | `browser-cli download --url ... --storage ...` |
| `capture-state.mjs` | `storage.py` + `chrome.py` | `browser-cli capture --service ...` |
| `launch-chrome-debug.sh` | `chrome.py` (+ kept as bash) | `browser-cli chrome launch-debug` |
| `find-chrome-profile.sh` | `profile.py` | `browser-cli profile find <email>` |
| `extract-pdf.py` | `extract.py` | `browser-cli extract pdf --src ...` |
| `extract-docx.py` | `extract.py` | `browser-cli extract docx --src ...` |

## Skill Update

`.agents/skills/playwright-cli/SKILL.md` becomes a thin reference:
- Points to `browser-cli/` repo for implementation
- Documents `browser-cli` CLI commands (not raw scripts)
- Keeps Critical Rules, Mode Selection, troubleshooting references
- Removes `scripts/` directory (code lives in repo)

## Integration with Existing Skills

```bash
# Agent workflow: acli → browser-cli → extract
acli jira workitem view TJ-1656  # get SharePoint URL
browser-cli download --url "$URL" --out docs/urs/tradeticket/URS.docx
browser-cli extract docx --src docs/urs/tradeticket/URS.docx --out docs/urs/tradeticket/URS.md
```

## Post-Install Setup

```bash
cd browser-cli
uv sync                          # creates .venv, installs deps
uv run playwright install chromium  # one-time browser binary
uv run browser-cli --help        # verify CLI works
```

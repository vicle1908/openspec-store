# Tasks: browser-cli Python Repo

uv Python repo following ecosystem standards (Python 3.14 + uv + ruff + mypy + pytest).

## 1. Repo Bootstrap

- [x] 1.1 Create `browser-cli/` directory under workspace root
- [x] 1.2 `cd browser-cli && git init`
- [x] 1.3 Create `pyproject.toml` (playwright>=1.50, typer>=0.15, pypdf>=5.0, python-docx>=1.1)
- [x] 1.4 `echo "3.14.5" > .python-version`
- [x] 1.5 `uv sync` — created `.venv/` and `uv.lock` (Python 3.14.5)
- [x] 1.6 ~~`uv run playwright install chromium`~~ Deferred until needed for fallback.
- [x] 1.7 Verify: `uv run python -c "from playwright.sync_api import sync_playwright; print('ok')"`
- [x] 1.8 Create `.gitignore` (.venv, __pycache__, auth-state*.json, downloads/)

## 2. Core Modules (src/browser_cli/)

- [x] 2.1 `__init__.py` — package init, version 0.1.0
- [x] 2.2 `profile.py` — find_profile_by_email, list_profiles, _extract_email
- [x] 2.3 `chrome.py` — is_chrome_running, launch_debug, check_cdp, quit_chrome
- [x] 2.4 `download.py` — transform_sharepoint_url, is_login_redirect, derive_output_path
- [x] 2.5 `cdp.py` — download_via_cdp using connect_over_cdp
- [x] 2.6 `storage.py` — capture_state (Mode A), download_with_storage (Mode B)
- [x] 2.7 `extract.py` — extract_pdf, extract_docx (python-docx + pandoc fallback)
- [x] 2.8 `cli.py` — typer app with download, capture, chrome, profile, extract subcommands

## 3. CLI Entry Points

- [x] 3.1 `browser-cli download --url <URL> [--out] [--port] [--storage] [--headless] [--timeout]`
- [x] 3.2 `browser-cli capture --service <name> --url <URL> [--profile] [--storage]`
- [x] 3.3 `browser-cli chrome launch-debug [--port] [--profile]`
- [x] 3.4 `browser-cli chrome status [--port]`
- [x] 3.5 `browser-cli profile find <email>`
- [x] 3.6 `browser-cli profile list`
- [x] 3.7 `browser-cli extract pdf --src <file> --out <file>`
- [x] 3.8 `browser-cli extract docx --src <file> --out <file>`

## 4. Tests

- [x] 4.1 `tests/test_profile.py` — 6 tests (extract_email, find_profile, list_profiles)
- [x] 4.2 `tests/test_download.py` — 13 tests (URL transform, login redirect, output path)
- [x] 4.3 `tests/test_extract.py` — 2 tests (PDF extraction, missing file)
- [x] 4.4 `tests/test_url_transform.py` — 5 tests (edge cases, encoded chars, WopiFrame)
- [x] 4.5 `tests/test_chrome.py` — 5 tests (is_chrome_running, check_cdp, mocked subprocess)
- [x] 4.6 `tests/test_extract_docx.py` — 2 tests (DOCX extraction with python-docx)
- [x] 4.7 Verify: `uv run pytest` → 33 passed, 30% coverage (utility/pure-fn paths)

## 5. Quality Gates

- [x] 5.1 `uv run ruff check src/ tests/` — All checks passed
- [x] 5.2 `uv run mypy src/` — Success: no issues found in 8 source files
- [x] 5.3 `uv run pytest --cov=browser_cli` — 33 passed, 30% line coverage (browser code needs integration tests)
- [x] 5.4 Verify CLI help: `uv run browser-cli --help` shows all 5 subcommand groups

## 6. Integration Validation

- [x] 6.1 `chrome status` — detects "Chrome running, CDP not available" correctly
- [x] 6.2 `profile find lekhanhvinh.phillip.com.sg@gmail.com` → returns Profile 5 path
- [x] 6.3 `profile list` — enumerates all 24 Chrome profiles with emails
- [x] 6.4 `extract pdf` — TJ-1656 URS regression: 22 pages, 25021 chars, 25847 bytes
- [x] 6.5 ~~`chrome launch-debug`~~ Deferred — requires user to close Chrome briefly.
- [x] 6.6 ~~SharePoint download via CDP~~ Deferred — blocked by 6.5.

## 7. Skill & Index Update

- [x] 7.1 Update `.agents/skills/playwright-cli/SKILL.md` — replaced raw script paths with `uv run browser-cli` commands
- [x] 7.2 Remove `.agents/skills/playwright-cli/scripts/` (code in browser-cli/ repo now)
- [x] 7.3 SKILLS_INDEX.md entry already in place (#24, Data & Search)
- [x] 7.4 Update `AGENTS.md` workspace table — `browser-cli/` row added
- [x] 7.5 docs/urs/INDEX.md refresh workflow uses `browser-cli` commands (already documented)

## 8. Finalize

- [x] 8.1 Write `README.md` with setup, usage, mode comparison
- [x] 8.2 Run `openspec validate add-playwright-cli-skill --strict` — passes
- [x] 8.3 ~~Initial commit~~ Deferred — user choice on when to commit.
- [x] 8.4 ~~Archive openspec change~~ Archived as part of 2026-07-17 cleanup.

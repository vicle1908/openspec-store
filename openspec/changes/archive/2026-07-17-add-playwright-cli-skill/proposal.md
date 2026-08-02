## Why

We frequently need to access authenticated web resources (SharePoint documents, internal wikis, corporate portals) from the CLI/agent workflow. Currently there's no skill for browser automation with existing user sessions. Playwright CLI supports `--user-data-dir` which allows reusing an existing Chrome profile's cookies/sessions — enabling download of authenticated resources without re-login or complex OAuth flows.

The immediate trigger: accessing SharePoint-hosted URS documents linked from Jira epics for analysis. But the capability generalizes to any authenticated download/scrape task using existing browser profiles.

## What Changes

- **New repo** `browser-cli/` — Python uv repo with typer CLI for authenticated browser downloads
- **Skill update** `.agents/skills/playwright-cli/SKILL.md` — thin reference pointing to `browser-cli/` repo
- **CLI tool** `browser-cli` — entry point with subcommands: download, capture, chrome, profile, extract
- **Integration pattern** with existing skills (acli → find link → playwright-cli → download → parse)

Key capabilities:
- Launch browser with existing Chrome user data dir (`--user-data-dir`)
- Download authenticated files (SharePoint .docx, Google Docs exports, internal PDFs)
- Capture page content/screenshots from authenticated pages
- Record interactions via `codegen` for replayable automation scripts
- Save storage state for session portability (`--save-storage` / `--load-storage`)

## Capabilities

### New Capabilities
- `authenticated-browser-download`: Use Playwright CLI with existing Chrome profiles to download files from authenticated web services (SharePoint, corporate portals) and save locally for processing
- `browser-session-management`: Manage browser storage states — export, import, and reuse authenticated sessions across CLI invocations without requiring Chrome to be closed

- `document-extraction`: Extract text from downloaded PDF/DOCX binaries into agent-readable markdown, register in docs/urs/INDEX.md for discovery

### Modified Capabilities
<!-- None — this is a new standalone skill with no existing spec dependencies -->

## Impact

**Dependencies:**
- `playwright` npm package (already available via `npx playwright@latest`)
- Chrome installed with user profiles at `~/Library/Application Support/Google/Chrome/`
- Profile lock constraint: `--user-data-dir` requires Chrome to be closed for that profile, OR use copied/cloned profile, OR use `--load-storage` with exported state

**Affected systems:**
- `.agents/skills/` — new skill directory
- `SKILLS_INDEX.md` — add entry
- No code repos affected (skill is workspace-level tooling)

**Constraints:**
- macOS-specific Chrome profile paths (skill documents macOS paths; Linux/Windows noted as variants)
- Chrome profile lock: cannot share profile with running Chrome instance
- SharePoint/M365 sessions may expire; skill must document re-auth flow
- Large file downloads need temp directory management

**Integration points:**
- `acli` skill → extracts URLs from Jira issues → `playwright-cli` downloads the resource
- `gws-drive` skill → alternative for Google-hosted docs (prefer native API when available)
- `pandoc` / `python-docx` → post-download document parsing

**Risk:**
- LOW: Playwright is well-maintained, CLI is stable, `--user-data-dir` is a documented feature
- MEDIUM: Chrome profile lock requires user coordination (close Chrome briefly)
- Mitigation: storage state export (`--save-storage`) eliminates need to touch live profile after initial export

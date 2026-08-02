# Workspace Relocation - Tasks

**Status:** Ready for complete migration
**Date:** 2026-05-23
**Policy:** one-way cutover; future development happens only in `$HOME/Developer/tdt/`

---

## Phase 0 - Preflight

### Task 0.1: Verify machine prerequisites
- confirm `git`, `glab`, `uv`, `npx`, `python3`, and `rg` exist
- confirm `$HOME/Developer/` is writable and has at least 4 GB free
- confirm the legacy legacy cloud workspace is readable for migration only
- confirm `$HOME/.tdt/.env` exists and has mode `600` or stricter

### Task 0.2: Capture baseline state
- save current `tools/legacy cloud-audit.sh` output
- save test totals for every Python repo
- save webhook receiver health, PID, and deploy source path
- save current GitNexus and Graphify index locations

---

## Phase 1 - Create Git-backed metadata

### Task 1.1: Create or reuse `tdt-meta`
- create `git.ecomedic.vn/tdt/tdt-meta` if absent
- clone it locally for staging
- keep `main` as the default branch

### Task 1.2: Move workspace metadata into `tdt-meta`
- include `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `README.md`, `INDEX.md`, `MACCY_GUIDE.md`, `RESEARCH_TOOLS_GUIDE.md`
- include `docs/`, `openspec/`, `.agents/`, `config/`, `skills/`, `openapi/`, `examples/`, `tools/`, `.github/`, `.vscode/`
- include `.env.example`, `.gitignore`, `.graphifyignore`
- exclude secrets, venvs, caches, worktrees, and generated outputs

### Task 1.3: Commit and push `tdt-meta`
- commit with `initial: migrate workspace metadata out of legacy cloud`
- push to `origin/main`
- clone back cleanly to verify remote state

---

## Phase 2 - Convert source-like directories without `.git/`

### Task 2.1: Convert `bootstrap-nexus-for-mobile/`
- create `git.ecomedic.vn/tdt/bootstrap-nexus-for-mobile`
- commit source/config only
- push `main`
- verify clone works

### Task 2.2: Convert `qi-bridge/`
- create `git.ecomedic.vn/tdt/qi-bridge`
- ignore generated `qi-gen-proxy`
- add build instructions (`go build ./...`) to README
- push `main`
- verify clone works

---

## Phase 3 - Build the new workspace

### Task 3.1: Clone repos into `$HOME/Developer/tdt/`
- create the workspace root
- clone `tdt-meta`
- clone every source repo from its `origin`
- clone the converted Category B repos
- verify each HEAD matches the expected remote state

### Task 3.2: Create root compatibility symlinks
- symlink `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `docs`, `openspec`, `.agents`, `config`, `skills`, `openapi`, `examples`, `tools`, `.github`, `.vscode`, `.gitignore`, `.graphifyignore`
- verify reads and writes resolve through `tdt-meta`

### Task 3.3: Handle secrets and local-only state
- compare legacy workspace `.env` keys with `$HOME/.tdt/.env`
- merge missing keys only after review
- do not copy `.env` to the new workspace
- keep runtime dotdirs and generated paths local only

---

## Phase 4 - Repoint tooling

### Task 4.1: Update shell hooks
- match only `$HOME/Developer/tdt/*`
- set `UV_PROJECT_ENVIRONMENT=$HOME/.tdt/venvs/<repo>` per repo
- set `PYTHONPYCACHEPREFIX=$HOME/.tdt/pycache/<repo>` per repo
- verify the hook does not activate under the legacy legacy cloud path

### Task 4.2: Recreate Python environments
- run `tools/relocate-venvs.sh` from the new workspace
- verify each `<repo>/.venv` symlink points to `$HOME/.tdt/venvs/<repo>`
- verify editable `.pth` files point only at `$HOME/Developer/tdt`

### Task 4.3: Install hooks from the new path
- run `tools/install-precommit-hooks.sh`
- smoke-test duplicate-file rejection with a staged fake file

### Task 4.4: Repoint deploy source
- update `webhook-receiver/scripts/deploy.sh` default source to `$HOME/Developer/tdt/webhook-receiver`
- keep `WEBHOOK_RECEIVER_SOURCE` override for tests
- deploy and verify `/health`

---

## Phase 5 - Rebuild path-bound state

### Task 5.1: Rebuild GitNexus indexes
- re-run analyze for every indexed active repo from `$HOME/Developer/tdt/`
- verify no index paths reference `legacy workspace` or `legacy-cloud-workspace`

### Task 5.2: Regenerate Graphify output
- run Graphify from `$HOME/Developer/tdt/`
- verify output references new paths only

### Task 5.3: Regenerate IDE caches
- open iOS project in Xcode and refresh Source Control
- open Android project in Android Studio and regenerate stale `.idea/workspace.xml` if needed

### Task 5.4: Validate Docker bind mount
- run a bind mount of `$HOME/Developer/tdt`
- confirm repo listing appears inside the container

---

## Phase 6 - Verification

### Task 6.1: Run Python and live SDK checks
- run all Python repo tests from relocated venvs
- run Jira smoke via `JiraClientFactory.from_env()`
- run GitLab smoke via `GitlabClientFactory.from_env().create_client()`

### Task 6.2: Verify webhook receiver runtime
- deploy from `$HOME/Developer/tdt/webhook-receiver`
- verify `launchctl print gui/$(id -u)/com.tdt.webhook-receiver` shows a PID
- verify one listener on port `8080`
- verify signed transition and bad-HMAC behavior

### Task 6.3: Scan for legacy path refs
- run `rg 'legacy workspace|legacy-tdt-workspace|tdt-knowledge' $HOME/Developer/tdt`
- replace active refs with `$HOME/Developer/tdt`, `TDT_WORKSPACE_ROOT`, or historical-note wording
- allow legacy refs only in archived docs or migration history

### Task 6.4: Verify legacy cloud independence
- confirm `AGENTS.md`, `openspec/`, docs, skills, and tools are readable from Git without legacy cloud
- confirm no supported script requires `tdt-knowledge/`
- confirm legacy cloud workspace can be disabled without blocking development

---

## Phase 7 - Decommission legacy legacy cloud path

### Task 7.1: Remove active legacy support
- remove legacy legacy cloud branches from shell hooks and deploy defaults
- update `AGENTS.md` and OpenSpec canonical specs to the new layout
- mark the old path as unsupported in docs

### Task 7.2: Make legacy workspace inert
- delete or rename the legacy legacy cloud workspace as an operator backup
- do not document rollback steps
- do not run future development commands from the legacy path

### Task 7.3: Archive this OpenSpec change
- promote requirements into `openspec/specs/uv-runtime-management/spec.md`
- archive `openspec/changes/workspace-relocation` after verification

---

## Success criteria

- `$HOME/Developer/tdt/` is the only active workspace root
- `tdt-meta` contains all workspace metadata and is pushed to GitLab
- root compatibility symlinks point to `tdt-meta/`
- all source-like directories are Git repos
- secrets live only in `$HOME/.tdt/.env` or reviewed local-only locations
- venvs and pycache live outside source and outside legacy cloud
- tests, live SDK smoke, deploy, Xcode, Android Studio, Docker, GitNexus, and Graphify pass from the new location
- `rg` finds no active dependency on the legacy legacy cloud path
- future agent work starts in `$HOME/Developer/tdt/`, not legacy cloud

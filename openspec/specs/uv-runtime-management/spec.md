# uv-runtime-management Specification

## Purpose
Define uv dependency and runtime boundaries for TDT repositories in the canonical non-legacy cloud workspace. The top-level workspace is a container for multiple independent repositories, not a Git repo and not a uv workspace.

## Requirements
### Requirement: Canonical workspace location
All active development SHALL run from `$HOME/Developer/tdt/`.

#### Scenario: Workspace root policy
- **WHEN** inspecting the active workspace root
- **THEN** it SHALL be `$HOME/Developer/tdt/`
- **AND** it SHALL NOT be treated as a Git repository or uv project
- **AND** the legacy path under `~/Library/legacy-workspace/legacy-cloud-workspace/...` SHALL NOT be used for active development.

### Requirement: Git-backed workspace metadata
Workspace-level metadata SHALL be versioned in `tdt-meta`.

#### Scenario: Metadata source of truth
- **WHEN** reading workspace-level docs/config/OpenSpec/skills/tools
- **THEN** the source of truth SHALL be `$HOME/Developer/tdt/tdt-meta/`
- **AND** root compatibility paths (for example `AGENTS.md`, `docs/`, `openspec/`, `.agents/`, `tools/`) SHALL resolve to that repo via symlink or equivalent mapping.

### Requirement: Repository-local uv environments
The top-level workspace SHALL remain a container only; each Python repo SHALL own its own uv files.

#### Scenario: Root folder has no uv runtime files
- **WHEN** checking `$HOME/Developer/tdt/`
- **THEN** it SHALL NOT contain root `pyproject.toml`, `uv.lock`, `.python-version`, or `.venv`
- **AND** uv commands SHALL run from the target repo directory.

#### Scenario: Each Python repo owns uv setup
- **WHEN** checking a Python repository under `$HOME/Developer/tdt/`
- **THEN** that repository SHALL contain its own `pyproject.toml`, `uv.lock`, and `.python-version`
- **AND** its dev environment SHALL be created with `uv sync --locked` from that repo root.

### Requirement: Reproducible uv-managed dependencies
`webhook-receiver/uv.lock` and `ai-review/uv.lock` SHALL be authoritative for development, verification, and production runtime.

#### Scenario: Developer setup uses locked environment
- **WHEN** a developer prepares `webhook-receiver`
- **THEN** they SHALL run `cd $HOME/Developer/tdt/webhook-receiver && uv sync --locked`
- **AND** commands SHALL run via `uv run ...` unless `.venv` is intentionally invoked.
- **AND** **WHEN** a developer prepares `ai-review`
- **THEN** they SHALL run `cd $HOME/Developer/tdt/ai-review && uv sync --locked`.

#### Scenario: Lockfile validity is checked before rollout
- **WHEN** deployment verification is performed
- **THEN** `uv lock --check` SHALL pass in `webhook-receiver`, `ai-review`, `tdt-core`, and `jira-daily-reports`
- **AND** deployment SHALL fail fast if any lockfile is stale.

### Requirement: Production runtime uses uv sync, not copied virtual environments
The runtime SHALL be built from source files and lockfiles in runtime paths; `.venv` copying is forbidden.

#### Scenario: Production runtime install
- **WHEN** deployment runs
- **THEN** deploy SHALL copy source, `pyproject.toml`, `uv.lock`, and `.python-version` into runtime directories
- **AND** deploy SHALL run `uv sync --frozen --no-dev --no-editable --compile-bytecode`
- **AND** dev dependencies SHALL NOT be installed in production runtime.

#### Scenario: Runtime dependency drift prevention
- **WHEN** `pyproject.toml` and lockfile disagree
- **THEN** deployment SHALL fail before service restart
- **AND** operators SHALL update lockfiles intentionally before retry.

### Requirement: Runtime and deploy source paths SHALL follow workspace-local deployment roots
Runtime SHALL stay outside the source workspace; deploy source SHALL be canonical and non-legacy cloud.

#### Scenario: LaunchAgent runtime root
- **WHEN** launchd starts `webhook-receiver`
- **THEN** it SHALL execute from `$HOME/Developer/tdt/deployments/webhook-receiver`
- **AND** it SHALL use the uv-synced executable from `$HOME/Developer/tdt/deployments/webhook-receiver/app/.venv/bin/uvicorn`
- **AND** it SHALL not rely on the legacy `$HOME/.tdt-webhook-receiver` runtime root.

#### Scenario: Deploy default source path
- **WHEN** `webhook-receiver/scripts/deploy.sh` runs without `WEBHOOK_RECEIVER_SOURCE`
- **THEN** the source path SHALL default to `$HOME/Developer/tdt/webhook-receiver`
- **AND** the script SHALL reject sources under `legacy workspace` / `legacy-cloud-workspace`.

### Requirement: Development venv isolation SHALL be enforced
Development venv and bytecode caches SHALL live outside source trees.

#### Scenario: Recommended environment hook
- **WHEN** running Python repos under `$HOME/Developer/tdt/`
- **THEN** `UV_PROJECT_ENVIRONMENT` SHOULD resolve to `$HOME/.tdt/venvs/<repo-name>`
- **AND** `PYTHONPYCACHEPREFIX` SHOULD resolve to `$HOME/.tdt/pycache/<repo-name>`
- **AND** `<repo>/.venv` MAY be a symlink for IDE/tool discovery.

### Requirement: No manual Python environment hacks
Startup SHALL NOT rely on shell activation or manual interpreter-state injection.

#### Scenario: Startup script inspection
- **WHEN** inspecting LaunchAgent startup commands
- **THEN** they SHALL NOT contain `source .venv/bin/activate`
- **AND** they SHALL NOT set `PYTHONHOME`
- **AND** they SHALL NOT inject `.venv/lib/.../site-packages` into `PYTHONPATH`
- **AND** they SHALL NOT start Python with `-S`.

### Requirement: Production launch uses synced entrypoint
The webhook receiver SHALL launch from the uv-created runtime environment.

#### Scenario: Uvicorn service starts
- **WHEN** launchd starts the service
- **THEN** it SHALL execute `$HOME/Developer/tdt/deployments/webhook-receiver/app/.venv/bin/uvicorn webhook_receiver.api.app:app`
- **AND** it SHALL listen on `127.0.0.1:8080` unless approved env overrides are set.

### Requirement: Environment and secrets SHALL be machine-local
Secrets SHALL be loaded from machine-local config outside source repos.

#### Scenario: Launchd environment loading
- **WHEN** launchd starts the service
- **THEN** the launchd plist's `EnvironmentVariables` dict SHALL provide `PATH`, `HOME`, and any service-specific env vars the app needs at startup (e.g. `JIRA_GUARD_*`, `SSL_CERT_FILE`, `REQUESTS_CA_BUNDLE`)
- **AND** the runtime launcher script SHALL NOT `source $HOME/.tdt/.env` (bash source is brittle when the file contains shell-unsafe content like unescaped `|`)
- **AND** the Python app SHALL load `$HOME/.tdt/.env` via `tdt_core.env.load_tdt_env()` (which wraps `python-dotenv`; tolerant of malformed lines)
- **AND** secrets SHALL NOT be committed to source repos or `tdt-meta`.

### Requirement: Local tests isolate external health dependencies
Unit tests SHALL mock external services for health-failure modes.

#### Scenario: OmniRoute failure unit tests
- **WHEN** unit tests validate unhealthy/refused/timeout/exception paths
- **THEN** tests SHALL patch the HTTP client or health-check dependency explicitly
- **AND** tests SHALL pass regardless of local live service availability.

### Requirement: Deployment verification is mandatory
Every rollout SHALL verify runtime health and process state before success.

#### Scenario: Rollout verification
- **WHEN** deployment completes
- **THEN** `/health` SHALL return `status: healthy`
- **AND** `launchctl print gui/$(id -u)/com.tdt.webhook-receiver` SHALL show a running PID
- **AND** exactly one process SHALL listen on port 8080
- **AND** recent logs SHALL show no recurring startup crash loop.

### Requirement: No workspace rollback contract to legacy cloud SHALL exist
Cutover to canonical workspace SHALL be one-way for supported workflows.

#### Scenario: Post-cutover policy
- **WHEN** migration verification has passed
- **THEN** active docs/scripts/automation SHALL not reference legacy legacy cloud workspace paths
- **AND** no supported rollback workflow to legacy cloud SHALL be specified, tested, or maintained.

### Requirement: Path-bound cache and index invalidation
Any path-bound cache, index, or editable install SHALL be regenerated whenever the workspace root changes.

#### Scenario: Code intelligence indexes
- **WHEN** the workspace root changes
- **THEN** GitNexus indexes (`<repo>/.gitnexus/`) SHALL be rebuilt from the new root
- **AND** `meta.json` and parse caches SHALL contain no path strings from the previous root.

#### Scenario: Workspace graph
- **WHEN** the workspace root changes
- **THEN** Graphify output (`graphify-out/`) SHALL be regenerated from the new root
- **AND** `manifest.json` SHALL contain no path strings from the previous root.

#### Scenario: Editable installs
- **WHEN** the workspace root changes
- **THEN** every editable `.pth` file in `$HOME/.tdt/venvs/<repo>/lib/python*/site-packages/` SHALL be regenerated by `uv sync --reinstall-package <repo>` from the new source path
- **AND** `.pth` files SHALL contain no path strings from the previous root.

#### Scenario: Production runtime config
- **WHEN** the workspace root changes
- **THEN** `$HOME/.tdt/.env` SHALL have any path-valued keys (for example `LOCAL_REPO_PATHS`) updated to the new root
- **AND** the daemon SHALL be restarted to pick up the new values.

### Requirement: Multi-machine consistency without legacy cloud
Propagation between machines SHALL use Git, not synchronized file systems.

#### Scenario: Source propagation
- **WHEN** changes need to reach another machine
- **THEN** they SHALL be committed and pushed to the repo's GitLab `origin`
- **AND** the receiving machine SHALL `git pull` the change.

#### Scenario: Metadata propagation
- **WHEN** workspace metadata changes (docs, OpenSpec, skills, config, tools)
- **THEN** changes SHALL be committed in `tdt-meta` and pushed to GitLab
- **AND** the receiving machine SHALL `git pull` `tdt-meta`.

#### Scenario: New machine bootstrap
- **WHEN** bootstrapping a new machine
- **THEN** the operator SHALL clone every repo into `$HOME/Developer/tdt/` from GitLab
- **AND** install the chpwd hook from `tdt-meta`'s documented snippet
- **AND** run `uv sync` per repo
- **AND** SHALL NOT enable legacy cloud sync over `$HOME/Developer/tdt/`.

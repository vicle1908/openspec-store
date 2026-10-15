# Design

## Context

See `proposal.md` for background and problem statement.

The workspace hosts multiple AI coding agents (Hermes, Codex, Claude Code, OMP) operating across 40+ repositories under `~/Developer/`. Previously, Google Workspace integrations relied on legacy Python wrappers (`google_api.py`, `setup.py`) tied to an unencrypted JSON token file (`~/.hermes/google_token.json`) that frequently expired. Meanwhile, Google has released the official `gws` CLI (`v0.22.5`, installed at `/opt/homebrew/bin/gws`) with OS keyring-backed AES-256-GCM encrypted credential storage, native JSON output format, and an upstream catalog of 40+ modular Agent Skills (`googleworkspace/cli/skills`).

The workspace standardizes on `npx skills` (Agent Skills CLI v1.0.0+) to manage external upstream skills with deterministic lockfile tracking via `~/Developer/.agents/skills-lock.json`. Skills installed via `npx skills add` establish canonical roots under `~/Developer/.agents/skills/` and symlinks under `~/Developer/.claude/skills/`, while supporting recurring synchronization via `npx skills update`.

## Goals / Non-Goals

**Goals:**
- Adopt core official Google Workspace Agent Skills (`gws-calendar`, `gws-drive`, `gws-gmail`, `gws-docs`, `gws-sheets`, `gws-tasks`) from upstream `https://github.com/googleworkspace/cli` using `npx skills add`.
- Track sources, revisions, and content hashes in `~/Developer/.agents/skills-lock.json` to enable automated maintenance via `npx skills update`.
- Wire native discovery for Claude Code (`~/Developer/.claude/skills/`) and Codex (`codex-user-skill-manifest.txt` -> `~/.agents/skills/`).
- Establish runtime verification procedures using `gws auth status` before executing API mutations.
- Validate end-to-end skill discovery and link integrity via `sync-workspace-agent-skills.py --check`.

**Non-Goals:**
- Re-implementing or modifying the binary `gws` CLI itself.
- Adopting niche or enterprise-only skills (`gws-modelarmor`, `gws-classroom`, `gws-admin-reports`) in this initial phase.
- Modifying Google Cloud Console OAuth application configurations beyond existing scopes.

## Decisions

### Decision 1: Use `npx skills` as Official Package & Lifecycle Manager
- **Choice:** Standardize on `npx skills add https://github.com/googleworkspace/cli/tree/main/skills/<skill-name> -y` and `npx skills update [skills...]`.
- **Rationale:** `npx skills` is the cross-agent specification standard. It automatically manages `~/Developer/.agents/skills-lock.json`, wires symlinks into `.claude/skills/` and `.agents/skills/`, and provides clean CLI update capabilities (`npx skills update`) without manual Git cloning or hash tracking.
- **Alternatives Considered:** Manual curl/git subtrees or vendoring. Rejected because they lack automated upstream update detection and break lockfile tracking.

### Decision 2: Direct CLI Subcommand Invocations Over Python Wrappers
- **Choice:** Standardize on direct `/opt/homebrew/bin/gws <service> <resource> <method> [flags]` invocations with `--format json`.
- **Rationale:** Native subcommands are maintained upstream, auto-discover API versions, handle multipart uploads/downloads cleanly, and eliminate python dependency drift (`google-auth`, `google-api-python-client`).
- **Alternatives Considered:** Maintaining Python client libraries or custom CLI wrappers. Rejected due to ongoing maintenance burden, credential drift, and duplicate token storage.

### Decision 3: Multi-Agent Manifest Inclusion for Codex and Claude Code
- **Choice:** Add adopted `gws-*` skill slugs to `codex-user-skill-manifest.txt` and `claude-user-skill-manifest.txt`.
- **Rationale:** Leverages the existing `sync-workspace-agent-skills.py` synchronization engine to wire symlinks into `~/.agents/skills/` and `~/.claude/skills/` deterministically.
- **Alternatives Considered:** Manual symlinking in ad-hoc shell scripts. Rejected as it bypasses the workspace's audited link reconciliation.

## Risks / Trade-offs

- **[Risk] OAuth token expiration in headless environments** → Mitigation: `gws auth status` must be checked prior to mutations. If `token_valid: false`, agents report clear instructions to run `gws auth login` or utilize the Chrome profile bridge.
- **[Risk] Parameter JSON escaping in shell environments** → Mitigation: Skills explicitly guide agents to construct structured JSON payloads via Python or input files (`--params @params.json`, `--json @body.json`) rather than fragile nested bash quoting.
- **[Risk] Upstream breaking changes during `npx skills update`** → Mitigation: `skills-lock.json` pins exact revisions; changes are audited via Git diff in `~/Developer/` before committing.

## Migration Plan

1. Run `npx skills add https://github.com/googleworkspace/cli/tree/main/skills/<name> -y` for core skills (`gws-calendar`, `gws-drive`, `gws-gmail`, `gws-docs`, `gws-sheets`, `gws-tasks`).
2. Verify lockfile entries in `~/Developer/.agents/skills-lock.json` and symlinks in `~/Developer/.claude/skills/`.
3. Update `codex-user-skill-manifest.txt` and `claude-user-skill-manifest.txt` in `platform/openspec-store/config/`.
4. Run `python3 ~/Developer/platform/openspec-store/scripts/sync-workspace-agent-skills.py` and verify `--check` exits cleanly (0).
5. Verify `npx skills update gws-calendar` executes without error.
6. Deprecate legacy `~/.hermes/skills/productivity/google-workspace/scripts/google_api.py` and document `gws` as the primary standard.

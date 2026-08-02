# Workspace Relocation - Design

**Change ID:** workspace-relocation
**Date:** 2026-05-23

---

## Decision

Perform a complete migration out of legacy cloud workspace. The canonical workspace becomes `$HOME/Developer/tdt/`. Workspace-level metadata moves to a Git repository named `tdt-meta`. No supported workflow will depend on legacy cloud after cutover.

---

## Research notes

| Source | Relevant finding | Design consequence |
|--------|------------------|--------------------|
| Apple File Provider docs: https://developer.apple.com/documentation/fileprovider | File Provider manages synced remote-storage content, local copies, and placeholders. | Do not treat legacy cloud workspace as a transparent local source/build filesystem. |
| Apple legacy cloud file-management docs: https://developer.apple.com/library/archive/documentation/FileManagement/Conceptual/FileSystemProgrammingGuide/legacy cloud/legacy cloud.html | legacy cloud file access requires coordination because the sync daemon may manipulate files concurrently. | Avoid high-churn uncoordinated writes from build tools, venvs, Git indexes, IDEs, and agents inside legacy cloud. |
| uv project config docs: https://docs.astral.sh/uv/concepts/projects/config/#project-environment-path | `UV_PROJECT_ENVIRONMENT` can set the project venv path; one absolute path reused by multiple projects can be overwritten. | Use unique `$HOME/.tdt/venvs/<repo>` envs, not one shared venv. |
| Docker Desktop settings: https://docs.docker.com/desktop/settings-and-maintenance/settings/#file-sharing | `/Users` is shared by default on Mac; external paths need explicit file sharing. | `$HOME/Developer/tdt` is Docker-compatible without custom settings. |

---

## Goals

1. Remove legacy cloud from all active development paths.
2. Keep source repos independent; no root Git repo and no root uv workspace.
3. Version workspace metadata in Git for auditability and conflict resolution.
4. Preserve root-level compatibility paths through symlinks.
5. Keep production runtime unchanged at `$HOME/.tdt-webhook-receiver/`.
6. Rebuild all path-bound caches/indexes after relocation.
7. Make future work happen only from `$HOME/Developer/tdt/`.

## Non-goals

- No uv workspace consolidation.
- No source package restructuring.
- No supported rollback to legacy cloud.
- No legacy cloud-backed knowledge-base hybrid.
- No migration of local secrets into Git.

---

## Target layout

```text
$HOME/Developer/tdt/
├── tdt-meta/                         # Git repo: workspace metadata
│   ├── AGENTS.md
│   ├── CLAUDE.md
│   ├── GEMINI.md
│   ├── docs/
│   ├── openspec/
│   ├── .agents/
│   ├── config/
│   ├── skills/
│   ├── openapi/
│   ├── examples/
│   ├── tools/
│   ├── .github/
│   ├── .vscode/
│   ├── .gitignore
│   └── .graphifyignore
├── tdt-core/                         # source repo
├── webhook-receiver/                 # source repo
├── jira-skill/                       # source repo
├── jira-daily-reports/               # source repo
├── jira-epic-report/                 # source repo
├── jira-kanban-from-spreadsheet/     # source repo
├── ops-automation-suite/             # source repo
├── browser-cli/                      # source repo
├── poems-mobile3-ios/                # source repo
├── poems-mobile3-android/            # source repo
├── bootstrap-nexus-for-mobile/       # new source repo
├── qi-bridge/                        # new source repo
├── AGENTS.md -> tdt-meta/AGENTS.md
├── docs -> tdt-meta/docs
├── openspec -> tdt-meta/openspec
├── .agents -> tdt-meta/.agents
├── config -> tdt-meta/config
├── skills -> tdt-meta/skills
├── tools -> tdt-meta/tools
└── openapi -> tdt-meta/openapi
```

The root remains a container. `tdt-meta` is the only Git repo for root-level metadata.

---

## Content categorization

| Category | Inputs | Destination |
|----------|--------|-------------|
| A: source repos | Directories with `.git/` | Clone from origin into `$HOME/Developer/tdt/<repo>` |
| B: source-like dirs without `.git/` | `bootstrap-nexus-for-mobile/`, `qi-bridge/` | Create GitLab repos, commit source only, clone into new workspace |
| C: metadata | docs, OpenSpec, skills, agent config, root MDs, workspace config, shared tools | Commit into `tdt-meta/`, expose via root symlinks |
| D: AI runtime dotdirs | `.claude/`, `.continue/`, `.augment/`, etc. | Do not migrate; ignore; recreate local state as needed |
| E: secrets | workspace `.env` | Merge reviewed keys into `$HOME/.tdt/.env`; never commit |
| F: generated/runtime | venvs, caches, graphify output, GitNexus DBs, worktrees, build output | Skip; regenerate after cutover |
| G: uncategorized | Any unrecognized top-level entry | Stop; require operator decision; record decision |

---

## Migration sequence

1. Preflight: clean/ pushed repos, required CLIs, disk space, legacy path readable.
2. Create `tdt-meta` on GitLab if absent.
3. Stage metadata into `tdt-meta`, excluding secrets/runtime/generated files.
4. Create repos for Category B directories and push source-only initial commits.
5. Clone all source repos and `tdt-meta` into `$HOME/Developer/tdt/`.
6. Create root symlinks from `$HOME/Developer/tdt/*` to `tdt-meta/*`.
7. Install/update shell hooks so only `$HOME/Developer/tdt/*` gets TDT env vars.
8. Run `tools/relocate-venvs.sh` from the new workspace.
9. Install pre-commit hooks from the new `tools/` path.
10. Rebuild GitNexus and Graphify indexes from the new workspace.
11. Regenerate IDE path caches as needed.
12. Redeploy webhook receiver from the new source path.
13. Scan all scripts/docs/configs/automations for legacy legacy cloud path references and replace them.
14. Verify full harness.
15. Decommission the legacy legacy cloud workspace as unsupported/inert.

---

## Path-bound state to invalidate

| Surface | Action |
|---------|--------|
| uv venv editable `.pth` files | Recreate via `tools/relocate-venvs.sh`; verify paths point to `$HOME/Developer/tdt` |
| Python bytecode | Redirect to `$HOME/.tdt/pycache/<repo>` or clear old source `__pycache__` |
| GitNexus | Re-run analyze for active repos; reject old index paths |
| Graphify | Regenerate `graphify-out/` from new workspace |
| Android Studio | Delete/regenerate absolute-path workspace state such as `.idea/workspace.xml` if stale |
| Xcode | Refresh Source Control / DerivedData if stale path state appears |
| launchd deploy | Default source path becomes `$HOME/Developer/tdt/webhook-receiver` |
| shell hooks | Match `$HOME/Developer/tdt/*` only after cutover |
| automations/prompts | Replace legacy legacy cloud paths with env vars or new root |

---

## Tooling implications

- `tools/relocate-venvs.sh`: lives in `tdt-meta/tools`, runs from root symlink `tools/`.
- `tools/legacy cloud-audit.sh`: changes from "make legacy cloud tolerable" to "detect accidental legacy cloud usage and stale generated artifacts".
- `tools/install-precommit-hooks.sh`: installs hooks from the new symlinked `tools/` path.
- `webhook-receiver/scripts/deploy.sh`: default source path becomes `$HOME/Developer/tdt/webhook-receiver`; env override remains for tests only.
- `AGENTS.md`: updated before cutover to state root is local APFS + `tdt-meta`, not legacy cloud.
- `openspec/specs/uv-runtime-management/spec.md`: updated on archive to remove hybrid fallback language.

---

## Risks and mitigations

| Risk | Mitigation |
|------|------------|
| Dirty/unpushed repo state lost by clone-based migration | Block until clean and pushed; verify HEAD match. |
| Metadata misses a top-level file | Category scan stops on uncategorized entries. |
| Secrets committed to `tdt-meta` | Explicit `.env` exclusion, secret scan, staged diff review. |
| Old absolute paths keep being used | Post-cutover path scan across docs/scripts/configs/automations. |
| GitNexus/Graphify answers use stale indexes | Required rebuild before architecture/impact work resumes. |
| IDEs keep old paths | First-open cache regeneration tasks. |
| Another machine still uses legacy cloud workspace | No hybrid writes; that machine must migrate before contributing. |
| Loss of ambient sync convenience | Replaced by Git audit trail and explicit conflict resolution. |

---

## Verification

Migration succeeds when all checks pass from `$HOME/Developer/tdt/`:

1. Root symlinks resolve into `tdt-meta/`.
2. `tdt-meta` is clean and has a pushed remote.
3. Every source repo is clean and matches expected remote HEAD.
4. All Python venv `.pth` files point to `$HOME/Developer/tdt`.
5. Python tests pass for all Python repos.
6. Jira/GitLab live smoke passes through `tdt_core` factories.
7. Webhook receiver deploys from the new source and `/health` is healthy.
8. GitNexus and Graphify indexes are rebuilt from new paths.
9. Xcode opens/builds iOS project; Android Studio Gradle-syncs Android project.
10. Docker bind mount of `$HOME/Developer/tdt` works.
11. `rg` finds no active references to the legacy legacy cloud workspace except historical docs/archive notes.
12. A machine without legacy cloud workspace enabled can read `AGENTS.md`, OpenSpec, docs, skills, and tools from Git.

---

## Decommissioning

After verification, the legacy legacy cloud workspace is not a rollback target. It may be deleted or renamed only as an inert operator backup. Shell hooks, scripts, docs, and automations must not reference it. Any future edit under the legacy path is a policy violation and should be ignored or moved to the canonical workspace.

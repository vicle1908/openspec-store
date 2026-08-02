# Workspace Relocation - Proposal

**Change ID:** workspace-relocation
**Status:** Ready
**Date:** 2026-05-23
**Author:** lekhanhvinh
**Supersedes part of:** `specs/uv-runtime-management/spec.md`
**Decision update:** complete migration, no supported rollback, all future development in `$HOME/Developer/tdt/`

---

## Problem

The active TDT workspace currently lives under legacy cloud workspace:

```text
/Users/lekhanhvinh/Developer/tdt/
```

legacy cloud workspace is designed around synchronized user documents, not high-churn source trees, Python virtual environments, code-intelligence indexes, IDE caches, Git worktrees, or build outputs. The workspace has already shown four failure classes:

1. `.pth` corruption from path-dependency/editable installs racing inside a File Provider-managed tree.
2. Dehydrated files producing spurious `ModuleNotFoundError` and stale package state.
3. Finder duplicate/conflict files such as `AGENTS 2.md` and `CLAUDE 2.md`.
4. Directory resurrection after archive/move operations on another synced machine.

The current guardrails detect and repair symptoms. They do not remove the substrate risk. The new decision is to fully remove legacy cloud from the development workflow instead of keeping a hybrid source/local + knowledge/legacy cloud model.

---

## Research grounding

- Apple File Provider docs describe synced remote-storage content as managed by a file provider and local copies/placeholders, not as a transparent substitute for local build trees.
- Apple legacy cloud file-management docs emphasize coordinated reads/writes because the legacy cloud daemon may manipulate files concurrently.
- uv docs confirm `UV_PROJECT_ENVIRONMENT` can relocate a project venv, and warn that a shared absolute path across projects can be overwritten; TDT must use one unique env path per repo.
- Docker Desktop docs state Mac file sharing includes `/Users` by default, making `$HOME/Developer/tdt` a safer Docker bind-mount root than paths outside the home tree.

References:

- https://developer.apple.com/documentation/fileprovider
- https://developer.apple.com/library/archive/documentation/FileManagement/Conceptual/FileSystemProgrammingGuide/legacy cloud/legacy cloud.html
- https://docs.astral.sh/uv/concepts/projects/config/#project-environment-path
- https://docs.docker.com/desktop/settings-and-maintenance/settings/#file-sharing

---

## Solution

Move every active workspace component out of legacy cloud and into Git-backed local development:

```text
$HOME/Developer/tdt/                  # local APFS container, not a Git repo
├── tdt-meta/                         # Git repo: docs, openspec, skills, config, tools
├── tdt-core/                         # Git repo
├── webhook-receiver/                 # Git repo
├── jira-daily-reports/               # Git repo
├── poems-mobile3-ios/                # Git repo
├── poems-mobile3-android/            # Git repo
├── AGENTS.md -> tdt-meta/AGENTS.md
├── openspec -> tdt-meta/openspec
├── docs -> tdt-meta/docs
├── .agents -> tdt-meta/.agents
└── tools -> tdt-meta/tools
```

Create a new `tdt-meta` GitLab repository for all workspace-level knowledge and shared tooling. Source-like directories without `.git/` become their own GitLab repos. Runtime/cache/secrets stay local only or move to `$HOME/.tdt/`.

---

## Scope

In scope:

- Canonical workspace: `$HOME/Developer/tdt/`
- New metadata repo: `git.ecomedic.vn/tdt/tdt-meta`
- Root symlinks from workspace container into `tdt-meta/`
- Migration script: `tdt-meta/tools/migrate-out-of-legacy cloud.sh`
- Per-repo venv relocation to `$HOME/.tdt/venvs/<repo>`
- Bytecode relocation to `$HOME/.tdt/pycache/<repo>`
- Conversion of non-Git source-like dirs (`bootstrap-nexus-for-mobile/`, `qi-bridge/`) into GitLab repos
- Removal of active references to the legacy legacy cloud workspace
- Rebuild/repoint of GitNexus, Graphify, IDE caches, shell hooks, deploy defaults, and automation refs
- Verification from the new location before cutover complete

Out of scope:

- Converting all repos into one uv workspace
- Restructuring source internals
- Moving the production runtime from `$HOME/.tdt-webhook-receiver/`
- Maintaining a supported rollback path to the old legacy cloud workspace
- Continuing development from the legacy path after cutover

---

## Why

- The current issue is structural: legacy cloud is eventually consistent and uses File Provider mechanics; source work needs local, deterministic file semantics.
- The workspace now includes multiple repos, path dependencies, mobile IDEs, code-intelligence indexes, launchd deploys, and agent-managed docs. The risk surface is larger than when legacy cloud was first used.
- A Git-backed `tdt-meta` preserves cross-machine propagation with audit history and explicit conflict resolution.
- The user has decided future development will happen only from the new location, so the spec should remove hybrid and rollback ambiguity.

---

## Expected outcome

After migration:

- Development works with legacy cloud workspace disabled.
- All source and metadata changes propagate through Git.
- `AGENTS.md`, OpenSpec, skills, docs, configs, and tools remain available at root-compatible paths via symlinks.
- Python venvs and bytecode caches live outside source and outside legacy cloud.
- The webhook receiver deploys from `$HOME/Developer/tdt/webhook-receiver` while runtime stays at `$HOME/.tdt-webhook-receiver/`.
- GitNexus and Graphify indexes reference the new path only.
- The legacy legacy cloud path is inert and unsupported.

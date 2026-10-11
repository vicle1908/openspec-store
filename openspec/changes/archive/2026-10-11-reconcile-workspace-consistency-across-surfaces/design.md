# Design

## Context

The workspace at `~/Developer/` underwent a clean-break reorganization to first-class organization namespaces (`platform/`, `tdt/`, `shb/`, `vds/`, `ascend/`, `ghtk/`, `fpt/`). While top-level code directories were consolidated and root hygiene restored, cross-surface drift remains:
- OpenSpec specs `gdrive-ios-and-deployments` and `workspace-topology-and-hygiene` still reference superseded paths (`~/Developer/mobile/poems-mobile3-ios/`, `mobile/`, `ops-tools/`).
- Agent guidance files `AGENTS.md` and `CLAUDE.md` retain legacy category paths (`mobile/poems-mobile3-android`, `ops-tools/tdt-tools`, `infra/fpt-ingenico`).
- 62 ephemeral macOS `.DS_Store` files pollute directory hierarchies.
- Canonical workspace skills (`.agents/skills/`) require continuous verification against `.agents/skills-lock.json`.

## Goals / Non-Goals

**Goals:**
- Eliminate all legacy path prefixes (`mobile/`, `ops-tools/`, `infra/fpt-ingenico/`) from specifications and agent guides.
- Keep `CLAUDE.md` in byte-for-byte synchronization with canonical `AGENTS.md`.
- Purge all ephemeral `.DS_Store` files across top-level roots.
- Validate that all 96 canonical skills remain synchronized without drift or broken symlinks.
- Strictly validate and archive the OpenSpec change with clean git commits.

**Non-Goals:**
- Moving or modifying production microservice code in Go or Python.
- Altering external git remotes or git history.

## Decisions

- **Decision 1: Direct in-spec path alignment**: Update `gdrive-ios-and-deployments` to target `tdt/poems-mobile3-ios/` directly in the delta specification.
- **Decision 2: Direct agent doc alignment**: Update `AGENTS.md` and replicate identically to `CLAUDE.md` to ensure all AI coding assistants (Claude Code, Codex, Antigravity, Pi) receive identical canonical path guidance.
- **Decision 3: Workspace .DS_Store purge**: Remove `.DS_Store` files up to maxdepth 4 to eliminate OS metadata scrap.

## Risks / Trade-offs

- **Risk**: Spec validation failure during strict checks.
  - **Mitigation**: Pre-validate delta specs using `openspec validate <change> --strict --store openspec-store`.
- **Risk**: Agent documentation desynchronization.
  - **Mitigation**: Automate verification of `AGENTS.md` == `CLAUDE.md` via `filecmp.cmp()`.

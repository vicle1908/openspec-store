# Design: Repair broken skill symlinks and upgrade toolchain

## Context

See `proposal.md` — Why. Current state and constraints relevant to the approach:

- The canonical store is `~/Developer/.agents/skills/`. This is the **official project path** for the majority of supported agents (Codex, Cursor, Gemini CLI, GitHub Copilot, Droid, OpenCode, Kilo, Cline, Zed, Universal), per the `skills` CLI supported-agents table. It held 50 real roots plus 35 orphan loops before this change.
- User-scope fanout is `~/.agents/skills/`, a **separate real directory** (not a symlink to the workspace store). It is an official global path for Cline/Dexto/Kimi/Loaf/Sarvam/Warp/Zed, and Codex additionally reads it as a compatibility root.
- Project scope is deliberately working-directory-relative: the official model defines it as `./<agent>/skills/`, and Codex resolves it from the current directory. Measured from the model-visible prompt via `codex debug prompt-input`:
  ```text
  cwd = ~/Developer    6 roots, 129 skills    r1(user ~/.agents/skills) = 55    r5(project ~/Developer/.agents/skills) = 69
  cwd = ~              5 roots,  60 skills    r1(user ~/.agents/skills) = 55    r5(project) = 0
  ```
  Project scope contributes 69 skills that **vanish** outside the workspace directory. User scope is therefore the only working-directory-independent route, which is why the fanout directory is load-bearing rather than redundant.
- The `skills` CLI (official, `vercel-labs/skills` 1.7.0) manages **project scope only**. Its `list --json` reports 94 entries, all `scope: "project"`, rooted at `~/Developer/.agents/skills`, with **zero** entries under `~/.agents/skills`. Its lockfile is `~/Developer/skills-lock.json` (43 entries).
- The official recommended install method is **symlink** — *"Creates symlinks from each agent to a canonical copy. Single source of truth, easy updates."* This is exactly the fanout shape the reconcile script produces.
- The official supported-agents table gives Codex's global path as `~/.codex/skills/`, not `~/.agents/skills/`. That directory currently holds only `.system` and `graphify`, so Codex reaches workspace skills through the compatibility root `~/.agents/skills` instead.
- `~/Developer/.agents/.skill-lock.json` lists the 35 orphaned skills; 34 of 35 are unresolvable. It is superseded by the official `~/Developer/skills-lock.json`.
- `~/Developer` is **not** a git repository, so skill content has no version history to restore from.

### Root cause (corrected)

The defect was **not** in the verifier. `scripts/sync-workspace-agent-skills.py` is context-independent: it reports identical canonical-root and broken-entry counts from the store root, from `~`, and from `/tmp`. An earlier reading of 85 roots versus 50 was a transient artifact of an in-progress repair, not a property of the script.

The verifier also correctly detects the defect: injecting a broken canonical link makes `--check` report `broken=1` and exit 1.

The actual defect was in `~/Developer/scripts/workstation-daily-update.sh` stage 6. Its form was:

```bash
python3 .../sync-workspace-agent-skills.py --check 2>&1 || {
  echo "Skills out of sync. Reconciling..."
  if [[ "${MODE}" == "apply" ]]; then
    python3 .../sync-workspace-agent-skills.py 2>&1 || true
  fi
}
```

Two properties combined to hide the breakage:

1. The `|| { ... }` handler **consumed** the non-zero exit, so the stage reported no failure.
2. Reconciliation only owns links pointing into managed roots. The orphan loops were unmanaged, so reconciliation left them broken — and its own result was discarded with `|| true`.

The stage therefore completed silently while 36 skills were dead. The scheduled run logged success at 08:01 on the failure date.

## Goals / Non-Goals

### Goals

- Restore real, resolvable content for all 36 unrecoverable skills in the canonical store.
- Keep user-scope discovery working from any working directory.
- Make the scheduled maintenance job fail closed when unresolved links remain.

### Non-Goals

- Adopting `~/.codex/skills/` (Codex's own official global directory) for workspace skills. It currently holds only `.system` and `graphify`; migrating fanout there is a separate decision.
- Introducing general skill-content version control for `~/Developer`. Recommended separately; out of scope here.
- Duplicating content into agent directories. The official single-source-of-truth model keeps one canonical copy and fans out by symlink.

## Decisions

### Decision: Restore content rather than delete the orphan loops

The loops contain no data and would be harmless to delete, which makes deletion tempting. Rejected because deletion silently reduces the workspace capability surface and destroys the only record — the lockfile entries — of what was installed. Restoration preserves both intent and capability.

**Alternative considered:** delete the 35 loops and drop the lockfile entries. Lower effort, but permanently loses Brave Search, Tavily, BrightData, DeepWiki, and Docfork skills that the operator deliberately installed.

### Decision: Restore from declared upstream sources, with a local backup fallback

35 skills restore via `skills add <owner/repo>`. `qi-hybrid-search` has no upstream source (proprietary, author `ekhanhvinh`) and is not in the lockfile, so it restores from its authoritative local backup copy at `~/My Drive/tdt/tdt-meta/.agents/skills/qi-hybrid-search/`.

**Alternative considered:** treat `qi-hybrid-search` as unrecoverable and remove it. Rejected — a complete backup existed, so removal was unnecessary.

### Decision: Fix the scheduled stage, not the verifier

The verifier was already correct and already context-independent. The change is confined to `workstation-daily-update.sh`: capture the check result, re-verify after reconciliation, and return non-zero when unresolved links survive.

**Alternative considered:** replace or extend `sync-workspace-agent-skills.py`. Rejected — the script is the documented authority, and `AGENTS.md` names it. Adding a second checker would create divergence.

### Decision: Use `skills add` with explicit agents, never `--all`

`--all` expands to `--skill '*' --agent '*' -y` and sprayed 50+ unintended agent directories (`.crush`, `.qwen`, `.trae`, `.windsurf`, `.pi`, …) into the workspace root. Only the intended surfaces are targeted.

**Alternative considered:** keep `--all` and clean up afterwards. Rejected as fragile and prone to leaving residue; the residue had to be removed twice during this change.

### Decision: Keep `--copy` for project content, symlink for fanout

`agent-device-skill-install` establishes that git-committed project skills must be regular files, because symlinks into a package cache break for other contributors. User-scope fanout is different: it is not committed, and the official tool recommends symlinks there precisely for single-source-of-truth updates.

**Alternative considered:** symlink the restored project content. Rejected — that is the mechanism that produced the original loop defect.

### Decision: Use official package identities for toolchain upgrades

The uv-installed Graphify tool is the PyPI package `graphifyy` (project `Graphify-Labs/graphify`), currently `0.9.74`, which matches its upstream latest. The unrelated npm package named `graphify` (`1.0.0`, "RGG — Random Graph Generator") is a different project and SHALL NOT be adopted as an upgrade target.

**Alternative considered:** upgrade `graphify` to the npm version `1.0.0`. Rejected — it is a name collision with a different tool.

### Decision: Remove the non-official plugin manifest directories

Eight canonical entries contained a `.cursor-plugin/` directory holding only a `plugin.json` manifest. The directory is **not** an official Agent Skills location (the official plugin manifests are `.claude-plugin/marketplace.json` and `.claude-plugin/plugin.json`), and upstream `redis/agent-skills` ships only `SKILL.md` and `references/`. Because such a directory makes an agent's catalog walk treat the skill directory as a plugin container and stop before `SKILL.md`, the eight directories were removed, making every declared skill discoverable.

**Alternative considered:** leave them and accept partial discovery. Rejected — it leaves declared skills silently unreachable and preserves a non-official artifact that upstream does not ship.

**Alternative considered:** reinstall the affected skills as copies instead of symlinks. Rejected — it breaks the single-source-of-truth model without addressing the cause.

### Decision: Detect undiscoverable entries in the verifier

`sync-workspace-agent-skills.py` now reports entries that resolve but are not discoverable. A plain existence check cannot catch either defect: a case-insensitive filesystem makes a lowercase entry point resolve as `SKILL.md`, and a plugin-container directory is invisible to a path check while still stopping the catalog walk.

**Alternative considered:** rely on the agent to report the omission. Rejected — the omission is silent, which is how it went unnoticed.

### Decision: Scope toolchain work to skill-related tooling

The change's toolchain scope is limited to tooling that participates in skill discovery, installation, or verification: the `skills` CLI, the uv-installed `graphifyy` and `tavily-cli`, the OpenSpec CLI, and the agent CLIs that consume the fanout. General application casks and pre-existing credential or model-configuration failures are excluded.

**Alternative considered:** upgrade all outdated Homebrew casks (nine were outdated, including `teamviewer`, `google-drive`, and `lark`) and repair the credential failures in this change. Rejected — those are unrelated to skill symlink integrity, several can disrupt running services, and absorbing them would silently widen a repair change into general machine maintenance. They are tracked as follow-up items instead.

### Decision: Declare the 27 undeclared fanout links rather than prune them

`~/.agents/skills/` is a real official global path (for Cline/Zed/Warp and peers) and is the only **working-directory-independent** way Codex reaches workspace skills. Project scope resolves from the current directory and contributes 69 skills under `~/Developer` but **0** from `~`. Pruning the 27 undeclared entries would remove that coverage outside the workspace directory. Declaring them records existing, working curation as intentional in the manifest the documented script already reads.

**Alternative considered:** prune them so the script exits 0 with no manifest edit. Rejected — it satisfies the checker by deleting capability, and it discards 55 skills of cwd-independent access that were deliberately created.

**Alternative considered:** migrate fanout to Codex's own official global directory `~/.codex/skills/`. Deferred as out of scope; it is a larger change to agent-specific configuration.

## Risks / Trade-offs

- **[Restored skills overwrite intentional local edits]** → `--copy` refreshes from upstream without prompting. Mitigation: the official lockfile records source and hashes; `graphify` was hash-verified identical to upstream before any overwrite.
- **[`--all` residue left behind]** → Mitigation: every created dot-directory was enumerated by timestamp against the repair window and removed; the surviving set was verified against the expected pre-repair dot-directories.
- **[Declaring 27 entries enlarges the Codex user-scope surface]** → Accepted deliberately: these links already exist and already resolve. Declaration documents current behavior rather than expanding it.
- **[Restored-from-backup content carries restrictive permissions]** → Mitigation: the backup copy had `0700`/`0600`; permissions were widened to `u+rwX,go+rX` to match sibling skills.
- **[Content provenance from a backup copy is unverified]** → Accepted for `qi-hybrid-search` only, as its sole authoritative source. The frontmatter is intact and parseable.
- **[Case-insensitive filesystem hides filename casing defects]** → APFS resolves `skill.md` as `SKILL.md`, so a lowercase entry point can pass local checks while a case-sensitive catalog walk skips it. Mitigation: `graphify` was found with a lowercase entry point and corrected; the store was then scanned for any other wrong-case or duplicate entry point, which found none.
- **[Agent-side discovery may omit some declared entries]** → A `.cursor-plugin/` directory inside a skill directory makes the agent treat it as a plugin container, so its catalog walk stops before `SKILL.md`. Mitigation: the directory is absent from upstream sources and is not an official Agent Skills location, so it was removed from the eight affected entries and both defect classes are now reported by the verifier.
- **[Two lockfiles coexist]** → The legacy `.skill-lock.json` (35 entries) and the official `skills-lock.json` (43 entries) both exist. Mitigation: this change treats the official lockfile as authoritative and notes the legacy file as superseded.

## Migration Plan

1. Snapshot the legacy lockfile and enumerate the broken entries before touching anything.
2. Remove the 35 orphan loops (no data loss — they contain no content).
3. Restore 35 skills from upstream sources; restore `qi-hybrid-search` from backup; correct its permissions.
4. Remove `--all` residue from the workspace root.
5. Verify: zero loops, all entries resolvable, `sync-workspace-agent-skills.py --check` reports `broken=0` on every surface.
6. Declare the 27 undeclared fanout links in the codex manifest and reconcile; confirm the script exits 0.
7. Upgrade the toolchain and confirm the store still validates.

**Rollback:** the legacy lockfile is preserved at `/tmp/skill-lock.backup.json`, and the removed entries contained no content, so rolling back would restore a strictly worse (broken) state. The meaningful rollback is re-running `skills add` per source repo. Manifest declaration rolls back by removing the 27 lines. Toolchain upgrades roll back through the normal per-manager mechanisms (Homebrew, npm, uv).

## Open Questions

- Should Codex's own official global directory `~/.codex/skills/` eventually replace `~/.agents/skills/` as the fanout target for this workspace? Deferrable: it changes agent configuration, not the spec or this repair, and current fanout works.
- Should `~/Developer/.agents/skills/` be brought under version control to make this class of loss recoverable? Deferrable: valuable but independent of this repair.

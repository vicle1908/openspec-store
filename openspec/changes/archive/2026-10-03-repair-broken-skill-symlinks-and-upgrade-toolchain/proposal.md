# Repair broken skill symlinks and upgrade toolchain

## Why

Thirty-six workspace skills under `~/Developer/.agents/skills/` existed only as mutually-referential symlink loops with no underlying content, making them invisible to every agent surface; the scheduled maintenance job could not detect the defect because its skills step discarded the verifier's failure status, so daily automation reported success while the skills stayed broken.

## What Changes

- Restore all 36 unrecoverable skills with real content in the canonical store `~/Developer/.agents/skills/`.
  - 35 restore from their declared upstream GitHub sources (brave, brightdata, tavily, docfork, seflless).
  - `qi-hybrid-search` restores from its authoritative local backup copy, since it is a proprietary skill with no upstream source.
- **BREAKING**: remove the `--all` install pattern from the repair path; bulk `--all` installs expand to `--skill '*' --agent '*' -y` and spray 50+ unintended agent directories into the workspace root.
- Correct the on-disk filename casing of skill entry points so case-sensitive catalog walks discover them; `graphify` shipped a lowercase entry point that only resolved because APFS is case-insensitive.
- Re-establish user-scope fanout links with the documented reconcile script `scripts/sync-workspace-agent-skills.py`.
- Declare the previously undeclared user-scope links in `config/codex-user-skill-manifest.txt` so user-scope discovery is recorded as intentional curation rather than undocumented drift.
- Make the skills step in the scheduled maintenance job fail when unresolved links remain, instead of discarding the verifier's failure status.
- Advance the toolchain to current upstream releases (Homebrew, global npm, uv tools, coding-agent CLIs, OpenSpec CLI).

## Capabilities

### New Capabilities

None. This change repairs existing behavior and introduces no new capability.

### Modified Capabilities

- `ecosystem-tooling-and-skills-upgrade`: the existing requirement "Cross-agent skills ecosystem manifest reconciliation" mandates that `sync-workspace-agent-skills.py --check` exit 0 and that the maintenance job reconcile manifests. It does not require the daily job to *fail* when unresolved links survive reconciliation, which is the gap that let 36 broken skills pass silently for weeks. The requirement must additionally mandate a fail-closed outcome and a resolvable-content guarantee for the canonical store and its user-scope fanout.

## Impact

- **Skill content**: `~/Developer/.agents/skills/` — 36 skills change from broken symlinks to real directories; canonical store grows from 50 to 94 direct roots.
- **User-scope fanout**: `~/.agents/skills/` — declared entries reconciled; 27 undeclared entries promoted to declared curation (62 entries total).
- **Manifests**: `config/codex-user-skill-manifest.txt` gains the 27 promoted entries.
- **Automation**: `~/Developer/scripts/workstation-daily-update.sh` stage 6 (now fail-closed) and `com.developer.workstation-daily-update.plist` (daily 08:00).
- **Governance**: `scripts/sync-workspace-agent-skills.py` broken-link detection.
- **Toolchain**: skill-related tooling only — the `skills` CLI, uv-installed `graphifyy` and `tavily-cli`, the OpenSpec CLI, and the agent CLIs that consume the fanout. All verified current.
- **Registries**: the official `~/Developer/skills-lock.json` (43 entries, all resolving) is current; the legacy `~/Developer/.agents/.skill-lock.json` is superseded by it.
- **Out of scope (tracked as follow-up)**: adopting Codex's own official global directory `~/.codex/skills/` for workspace skills; rewriting vendored upstream skill metadata that exceeds the TDT description budget; upgrading the nine outdated general application casks; and pre-existing Codex OAuth token and Claude model-id failures that block live-model probes. Each is unrelated to skill symlink integrity.

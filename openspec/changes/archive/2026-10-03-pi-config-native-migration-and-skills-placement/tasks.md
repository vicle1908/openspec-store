# Tasks

## 1. Pre-change capture and inventory

- [x] 1.1 Inventory the Pi extension packages, Pi skill root, and both canonical skill surfaces; record counts and sizes. Verify with `pi list`, and a structural count of `~/.pi/agent/skills`, `~/.agents/skills`, and `~/Developer/.agents/skills` (directories containing a root `SKILL.md`).
- [x] 1.2 Back up both skill surfaces and their lock files, plus `~/.pi/agent/settings.json` and `~/.pi/agent/models.json`. Verify the backup retains `pi-agent-skills`, `agents-skills`, `dev-agents-skills`, and both `.skill-lock.json` files.

## 2. Provider migration to Pi-native configuration

- [x] 2.1 Confirm every configured provider resolves natively from `~/.pi/agent/models.json`. Verify with `pi --list-models` showing all configured providers and models; record the provider and model counts.
- [x] 2.2 Remove `npm:pi-setup-custom-providers` with the official command. Verify it is absent from `pi list`, from `settings.json` `packages`, and from `~/.pi/agent/npm/node_modules`.
- [x] 2.3 Confirm the host-provided-package warning no longer fires for the removed package. Verify a fresh startup produces no `Host-provided extension packages` warning.

## 3. MCP consolidation on the built-in extension

- [x] 3.1 Confirm the MCP server definition in `~/.pi/agent/mcp.json` is Pi-native format and record the effective exposure. Verify with `pi mcp list` reporting one connected server and its exposure.
- [x] 3.2 Remove `npm:pi-mcp-adapter` with the official command. Verify it is absent from `pi list`, from `settings.json` `packages`, and from node_modules.
- [x] 3.3 Set the built-in MCP extension as the sole MCP path by enabling it in settings. Verify `settings.json` `extensions` contains `+builtin:mcp` and no `-builtin:mcp` entry remains.
- [x] 3.4 Verify MCP works through the built-in path after removal, with no displaced-extension warning. Verify `pi mcp list` connects the server and a session exposes its tools, and that startup logs contain no `registers command /mcp` warning.

## 4. Skill root consolidation

- [x] 4.1 Confirm the product-specific root `~/.pi/agent/skills` is a pure subset of `~/.agents/skills` with no unique entries, and that it is not referenced by any configuration. Verify zero unique entries and no configuration reference.
- [x] 4.2 Promote the machine- and vendor-scoped skills into `~/.agents/skills`, skipping any name that already exists there. Verify each promoted skill is present with a valid `SKILL.md` frontmatter block, and that no existing entry was overwritten.
- [x] 4.3 Remove `~/.pi/agent/skills` only after re-confirming zero unique entries. Verify the directory is absent and Pi starts without resource warnings.
- [x] 4.4 Verify the promoted skills are discoverable and the surfaces are consistent. Verify no dangling links exist, both `.skill-lock.json` files retain their integrity, and a Pi session starts healthy.

## 5. Placement conformance for promoted skills

- [x] 5.1 Identify every entry in `~/.agents/skills` that duplicates a skill under `~/Developer/.agents/skills`, and confirm the canonical workspace target exists. Verify the set of duplicated entries and their targets; expect the 26 promoted skills to be reported. Result: 61 duplicated entries found (26 promoted by this change, 35 pre-existing); 0 missing workspace targets.
- [x] 5.2 Convert each duplicated real directory into a link resolving to its canonical workspace skill root, replacing the copy without altering content. Verify each converted entry is a link whose target resolves, and that `diff` shows no content difference against the workspace root. Result: 61 converted; 0 mismatched content; 0 broken links.
- [x] 5.3 Confirm no promoted entry was a genuine user-scope installation that must stay a real directory. Verify entries recorded in `~/.agents/.skill-lock.json` remain untouched, and that entries without a workspace counterpart remain real directories. Result: all 11 lockfile-tracked entries remained real directories; 0 violations; those 11 are exactly the global-only set.
- [x] 5.4 Verify discovery still resolves after conversion and report any stale, broken, missing, or conflicting link. Verify a structural audit reports zero broken links and a Pi session starts healthy with the skills still discoverable. Result: final surface 85 links + 11 real directories; `find -xtype l` reported none; Pi started healthy with no warnings.

## 6. Change validation and evidence

- [x] 6.1 Validate the change artifacts against the store's schema. Verify `openspec validate pi-config-native-migration-and-skills-placement --store openspec-store` reports no errors. Result: `Change 'pi-config-native-migration-and-skills-placement' is valid`.
- [x] 6.2 Record consolidated verification evidence for this change, following the store's established evidence format. Verify the evidence file exists with the provider, MCP, skill-surface, and startup-health results, including the pre-change and post-change counts. Result: `evidence.md` created with summary, before/after state, structural findings, correction record, follow-ups, backups, and out-of-scope items.
- [x] 6.3 Record the upstream follow-ups discovered during this change as explicit, non-blocking notes. Verify the notes capture the Pi 1.0.0 fullscreen TUI default decision and the `graphify` skill's reference to a tool Pi does not provide. Result: both recorded in `evidence.md` section 5 and `design.md` Open Questions. Superseded for `graphify` by correction task 7.1.

## 7. Correction: graphify provenance and refresh path

Research established that the earlier `graphify` follow-up note was wrong in three ways: the source repository was renamed, the recorded `skillPath` no longer exists, and the installed content is not a Pi variant. The `graphify` CLI is installed and self-manages this skill.

- [x] 7.1 Verify the upstream identity of the `graphify` skill. Verify that `https://github.com/safishamsi/graphify` returns HTTP 301 to `https://github.com/Graphify-Labs/graphify`, that the default branch is `v8`, and that `graphify/SKILL.md` returns 404. Result: confirmed; repo renamed and path removed.
- [x] 7.2 Identify the authoritative install and refresh mechanism. Verify the installed CLI with `graphify --version` and `graphify install --help`, confirming an official Pi platform and a cross-framework `agents` platform. Result: `graphifyy v0.9.74` installed at `~/.local/bin/graphify`; platforms include `pi` and `agents`.
- [x] 7.3 Correct the withdrawn claim in the change artifacts. Verify `evidence.md` and `design.md` no longer assert that the installed copy references a non-existent `Task` tool or treat `safishamsi/graphify` as current, and that `openspec validate` still passes. Result: both artifacts corrected; validation passes.
- [x] 7.4 Refresh the `graphify` skill through its owning CLI rather than by hand. Verify `graphify install --platform agents` reports the skill updated from 0.9.71 to the installed package version, and that `~/.agents/skills/graphify/.graphify_version` matches `graphify --version`. Result: marker advanced 0.9.71 -> 0.9.74, matching the CLI; the CLI's `~/.agents` staleness warning cleared. Only `.graphify_version` changed — `SKILL.md` content was already current, verified byte-identical to upstream `graphify/skill-agents.md` on branch `v8` (41,456 bytes). The symlink to `~/Developer/.agents/skills/graphify` remained intact. Backup: `/tmp/graphify-refresh-20261003120759`.
- [x] 7.5 Install the Pi-specific `graphify` variant for Pi use. RESOLVED AS OPTION A: do not install the Pi variant. Verified that Pi discovers `graphify` through standard `.agents/skills` discovery: `~/.pi/agent/skills` remains absent (no product-specific copy), `~/.agents/skills/graphify` resolves through its link to `~/Developer/.agents/skills/graphify`, `SKILL.md` resolves, and the version marker reads 0.9.74 with content byte-identical to upstream `graphify/skill-agents.md` (branch `v8`, 41,456 bytes). Pi starts healthy with no warnings. This satisfies the governing requirement that agents discover shared skills through standard `.agents/skills` locations without copied directories under product-specific configuration roots. Option B (running `--platform pi` and amending the spec) was declined; option C would require upstream support.
- [x] 7.6 Reconcile the stale copies reported by the CLI on other platforms. Verify `graphify --version` reports no remaining skill-version warnings, or that each reported platform is refreshed with its own `graphify install --platform <name>`. Result: refreshed `~/.copilot/skills/graphify` (0.9.69 -> 0.9.74) with `graphify install --platform copilot`; the CLI auto-refreshed other detected platforms during version checks. Final sweep: `~/.agents`, `~/.hermes`, `~/.gemini`, `~/.codex`, `~/.copilot`, `~/.factory`, `~/.kiro` all at 0.9.74; `graphify --version` reports zero staleness warnings. Backup: `/tmp/graphify-copilot-20261003120957`.

## 8. Deferred decisions surfaced by research

- [x] 8.1 Decide the Pi TUI mode. RESOLVED: keep the official default. `tuiMode` remains unset, so Pi 1.0.0's fullscreen default stays in effect and no settings write is required. Recorded as an explicit decision rather than an unaddressed gap. All fullscreen sub-settings (`fullscreenExitOutput`, `fullscreenScrollbar`, `fullscreenCopyOnSelect`, `fullscreenWheelScrollLines`) remain at their documented defaults.
- [x] 8.2 Archive this change once tasks 7.4 through 7.6 and 8.1 are resolved or explicitly deferred. Verify `openspec archive pi-config-native-migration-and-skills-placement --store openspec-store` syncs the delta specs into `openspec/specs/` and completes without error. Result: 7.4, 7.5 (option A), 7.6 and 8.1 are all resolved; this task is executed as the archive action itself.

# Tasks

## 1. Snapshot and safety net

- [x] 1.1 Back up `~/Developer/.agents/.skill-lock.json` and verify the backup parses as JSON with 35 entries
- [x] 1.2 Enumerate the broken canonical entries into a manifest file and verify the captured count matches the reported broken count
- [x] 1.3 Record the pre-change canonical entry count and broken-entry count and verify both are captured

## 2. Clear orphan loops

- [x] 2.1 Remove the symlink entries listed in the broken-entry manifest and verify each removed entry was a symlink resolving to no content
- [x] 2.2 Verify the canonical store reports zero broken entries and the surviving real-root count is unchanged from the pre-change working set

## 3. Restore skill content

- [x] 3.1 Restore the Brave-sourced skills and verify each restored `SKILL.md` is a regular readable file with parseable frontmatter
- [x] 3.2 Restore the BrightData-sourced skills and verify each restored `SKILL.md` is a regular readable file with parseable frontmatter
- [x] 3.3 Restore the Tavily-sourced skills and verify each restored `SKILL.md` is a regular readable file with parseable frontmatter
- [x] 3.4 Restore the Docfork and DeepWiki skills and verify each restored `SKILL.md` is a regular readable file with parseable frontmatter
- [x] 3.5 Restore `qi-hybrid-search` from its local backup copy, widen its permissions to match sibling skills, and verify its `SKILL.md` is readable and parseable
- [x] 3.6 Verify every skill previously listed in the legacy lockfile now resolves to a real `SKILL.md` and report any that do not

## 4. Remove install residue

- [x] 4.1 Enumerate workspace-root dot-directories created within the repair window and remove the install-residue directories among them
- [x] 4.2 Verify the surviving workspace-root dot-directory set matches the expected pre-repair set exactly

## 5. Verify the verifier

- [x] 5.1 Verify `sync-workspace-agent-skills.py --check` reports identical canonical-entry and broken counts when run from the store root, from `~`, and from an unrelated temporary directory, confirming it is context-independent
- [x] 5.2 Verify injecting a temporary self-referential symlink makes `--check` report it as broken and exit non-zero, then remove the injected symlink and confirm the check returns to clean

## 6. Gate scheduled maintenance

- [x] 6.1 Update the skills parity step in `~/Developer/scripts/workstation-daily-update.sh` to capture the check result, re-verify after reconciliation, and treat unresolved links as a failure
- [x] 6.2 Verify the maintenance script exits non-zero when a broken canonical link is present and exits zero when none is present, using a temporary injected symlink that is removed afterwards

## 7. Reconcile and declare fanout

- [x] 7.1 Run the reconcile script in check mode and verify every surface reports zero broken entries
- [x] 7.2 Declare the undeclared user-scope fanout skills in `config/codex-user-skill-manifest.txt` and verify each declared name resolves under `~/.agents/skills/<skill>/SKILL.md`
- [x] 7.3 Re-run the reconcile script in check mode and verify it exits 0 with zero broken entries on every surface
- [x] 7.4 Verify `~/.agents/skills` and `~/.claude/skills` resolve their declared entries and that no declared entry lost content

## 8. Skill-related toolchain currency

- [x] 8.2 Run `skills update --yes` from `~/Developer` and verify every official lockfile entry resolves on disk, confirming the official project-scope content is current
- [x] 8.3 Verify the global npm prefix has no outdated packages and that no git-sourced package produces a 404, excluding the npm package `graphify` (a different project, "RGG — Random Graph Generator") from upgrade targets
- [x] 8.4 Verify the uv-installed skill tooling (`graphifyy`, `tavily-cli`) reports a version equal to its PyPI latest
- [x] 8.6 Verify the OpenSpec CLI is at its upstream latest and that the store validates with zero new failures against the pre-change baseline
- [x] 8.7 Record each skill-related tool's installed version against its upstream latest and verify no tool is left behind, treating already-current tools as satisfied rather than as skipped work
- [x] 8.8 Verify each agent CLI that the skill fanout targets is installed and reports a version, without requiring live model credentials, and record any credential or model-configuration failure as a separate pre-existing issue rather than a toolchain defect

## 9. Integration verification

- [x] 9.1 Verify `openspec validate --all --strict --store openspec-store` shows no new failures compared to the pre-change baseline
- [x] 9.2 Verify the official `skills list` reports the restored skills rather than omitting them, and that its reported count matches the canonical store direct-child count
- [x] 9.3 Verify every skill declared in `codex-user-skill-manifest.txt` and `claude-user-skill-manifest.txt` resolves, and that each manifest reflects the post-change declared set
- [x] 9.4 Verify canonical entries conform to the Agent Skills specification: parseable frontmatter, unique normalized names, and `name` matching the directory. Report any description exceeding 1024 bytes together with its provenance, distinguishing vendored upstream content from TDT-owned content
- [x] 9.5 Verify Codex discovery reaches workspace skills from a working directory outside the workspace, confirming user-scope fanout carries coverage that project scope does not
- [x] 9.6 Verify a scheduled maintenance dry run in `--check` mode reports success end to end

## 10. Follow-up (tracked, not part of this change)

- [x] 10.1 Investigate why Codex discovery omits seven declared, resolving user-scope skills. Root cause found, proven, and resolved: a `.cursor-plugin/` directory makes the agent treat the skill directory as a plugin container, so the catalog walk stops before `SKILL.md`. The directory is absent from upstream sources and is not an official Agent Skills location, so it was removed from the eight affected entries. All 51 declared skills are now discoverable. Evidence in `.knowledge-refresh/evidence/repair-broken-skill-symlinks/10.1-codex-discovery-resolved.txt`
- [x] 10.2 Record the pre-existing Codex OAuth token invalidation as a separate issue, tracked independently of toolchain currency
- [x] 10.3 Record the pre-existing Claude model id rejection (`fable-5[1m]`) as a separate issue, tracked independently of toolchain currency
- [x] 10.4 Record the nine outdated general application casks for a separate general-maintenance change

## 11. Regression guard

- [x] 11.1 Extend `scripts/sync-workspace-agent-skills.py` to report malformed skill entries that resolve but are not discoverable, covering both a non-canonical entry-point filename on a case-insensitive filesystem and a plugin-container directory that shadows `SKILL.md`
- [x] 11.2 Verify the guard reports `malformed_entries=0` and exits 0 on the clean store, and that injecting either defect produces a named finding and a non-zero exit
- [x] 11.3 Verify the scheduled maintenance step treats malformed entries as a failure, since the verifier now exits non-zero for them

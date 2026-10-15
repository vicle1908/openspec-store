# Tasks

## 1. Upstream Skills Installation via npx skills

- [x] 1.1 Install core official skills (`gws-calendar`, `gws-drive`, `gws-gmail`, `gws-docs`, `gws-sheets`, `gws-tasks`) using `npx skills add https://github.com/googleworkspace/cli/tree/main/skills/<name> -y` in `~/Developer/`, verifying each lands under `~/Developer/.agents/skills/`.
- [x] 1.2 Verify that `npx skills` registers all installed skills and their computed hashes in `~/Developer/.agents/skills-lock.json`.
- [x] 1.3 Verify that symlinks for installed skills are automatically established under `~/Developer/.claude/skills/` without duplicate directory copies.

## 2. Multi-Agent Discovery Manifests & Validation

- [x] 2.1 Add the adopted `gws-*` skill names to `~/Developer/platform/openspec-store/config/codex-user-skill-manifest.txt` and verify the manifest entries remain sorted and valid.
- [x] 2.2 Add the adopted `gws-*` skill names to `~/Developer/platform/openspec-store/config/claude-user-skill-manifest.txt` and verify the manifest entries remain sorted and valid.
- [x] 2.3 Run `python3 ~/Developer/platform/openspec-store/scripts/sync-workspace-agent-skills.py` to reconcile user-level links into `~/.agents/skills/` and verify that `sync-workspace-agent-skills.py --check` exits with return code 0 (`malformed_entries=0`).

## 3. Recurring Update & Runtime Verification

- [x] 3.1 Test and verify upstream update capabilities by executing `npx skills update gws-calendar` in `~/Developer/`, ensuring it cleanly checks upstream and updates the lockfile.
- [x] 3.2 Verify the `gws auth status` execution contract within the skills, ensuring that `token_valid: true` and encrypted keyring storage are checked before mutating operations.
- [x] 3.3 Execute an end-to-end read verification via `gws calendar events list --params '{"calendarId":"primary","maxResults":1}'` through the newly imported skill specification.
- [x] 3.4 Mark legacy custom scripts (`~/.hermes/skills/productivity/google-workspace/scripts/google_api.py`) as deprecated in documentation, directing agents to the canonical `gws-*` skills.

## Workflow follow-up

- Validate all OpenSpec specs and change artifacts strictly via `openspec validate adopt-official-gws-agent-skills --store openspec-store --strict`.
- Review the change artifacts and commit the reviewed store changes.

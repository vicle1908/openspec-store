# Tasks

## 1. Skill Catalog Adoption and Global Installation

- [x] 1.1 Inventory all 45 official skill manifests in `/Users/androidteam/Omniroute/skills` and verify frontmatter compliance.
- [x] 1.2 Run `npx skills add /Users/androidteam/Omniroute -g --all` to install all 45 skills globally via local symlinks.
- [x] 1.3 Verify that `omni-*` skill directories are created in `~/.agents/skills/` and are discoverable via `npx skills ls -g`.

## 2. OmniRoute Management Authorization and Scope Escalation

- [x] 2.1 Query `/app/data/storage.sqlite` inside container `omniroute` to inspect the active key record for `mac-mini-1`.
- [x] 2.2 Execute atomic UPDATE on `api_keys` in `/app/data/storage.sqlite` setting `scopes = '["self:usage","manage","admin"]'` for `mac-mini-1`.
- [x] 2.3 Send authenticated test request to `http://127.0.0.1:20128/api/monitoring/health` using Bearer token from `~/.claude/helpers/omniroute-key.sh` and assert HTTP 200 with `status: "healthy"`.
- [x] 2.4 Send authenticated test request to `http://127.0.0.1:20128/api/models` and assert HTTP 200 with JSON model array.

## 3. Environment and Shell Normalization

- [x] 3.1 Append exports for `OMNIROUTE_URL="http://localhost:20128"`, `OMNIROUTE_BASE_URL="http://localhost:20128"`, and `OMNIROUTE_KEY="$OMNIROUTE_API_KEY"` to `~/.zshenv` at line 43+ (strictly outside `# BEGIN/END shared-agent-secrets`).
- [x] 3.2 Update `~/.zshrc` line 221 to `export OMNIROUTE_BASE_URL=http://localhost:20128` (stripping trailing `/v1`), keeping `COPILOT_PROVIDER_BASE_URL=http://localhost:20128/v1` on line 223 intact.
- [x] 3.3 Verify subshell and interactive shell environment resolution to confirm `OMNIROUTE_URL="http://localhost:20128"`, `OMNIROUTE_BASE_URL="http://localhost:20128"`, and `OMNIROUTE_KEY` match across all shell invocations.

## 4. Documentation and Operational Reference Authoring

- [x] 4.1 Author operational guide `/Users/androidteam/Developer/docs/omniroute-agent-skills.md` detailing all 22 `omni-*` REST skills, HTTP endpoints, Bearer authentication, and curl recipes.
- [x] 4.2 Update `/Users/androidteam/Developer/wiki/entities/omniroute.md` to document the 45 adopted skills, management authorization model, and link to the operational reference.
- [x] 4.3 Execute end-to-end smoke test verifying an agent can discover models, check health, and inspect providers via the newly adopted skills without errors.

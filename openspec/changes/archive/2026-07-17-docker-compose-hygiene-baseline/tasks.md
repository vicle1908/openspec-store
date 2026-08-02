# Tasks: docker-compose-hygiene-baseline

## 1. Validate findings (block 1 — must complete before code edit)

- [x] 1.1 Run `docker compose config` on `jira-skill/` and `bootstrap-nexus-for-mobile/` to confirm syntax
- [x] 1.2 Audit any scripts/docs that hardcode old container names after `container_name:` removal (no script references found)
- [x] 1.3 `openspec validate --strict docker-compose-hygiene-baseline`

## 2. Fix jira-skill/docker-compose.yml

- [x] 2.1 Add `name: jira-skill` at top level
- [x] 2.2 Remove `version:` field
- [x] 2.3 Replace `GF_SECURITY_ADMIN_PASSWORD=admin` with `${GF_ADMIN_PASSWORD:-changeme}` sentinel
- [x] 2.4 Remove all `container_name:` overrides (app, postgres, redis, prometheus, grafana, nginx)
- [x] 2.5 Fix Redis healthcheck: add `-a redis_pass` to `redis-cli` command
- [x] 2.6 Run `docker compose config` to validate syntax (validated, OK)

## 3. Fix bootstrap-nexus-for-mobile/docker-compose.yml

- [x] 3.1 Add `name: nexus-mobile` at top level
- [x] 3.2 Remove `version: '3.8'` field
- [x] 3.3 Remove all `container_name:` overrides (nexus, nexus-nginx)
- [x] 3.4 Run `docker compose config` to validate syntax (validated, OK)

## 4. Update docs/scripts referencing old container names

- [x] 4.1 Search for `jira-skill-grafana`, `jira-skill-postgres`, etc. in docs and scripts (only this OpenSpec change's spec mentions these as historical references)

## 5. Wrap-up

- [x] 5.1 Run `git status` and surface dirty files to user (3 commits landed; unrelated dirty files surfaced)
- [x] 5.2 `openspec status --change docker-compose-hygiene-baseline` (apply-ready — all 4 artifacts complete, validated)

## 6. Commit summary

- `jira-skill`: `chore(jira-skill): harden docker-compose per docker-compose-hygiene-baseline` (commit `743e974`)
- `bootstrap-nexus-for-mobile`: `chore(bootstrap-nexus): modernize docker-compose per docker-compose-hygiene-baseline` (commit `1591d83`)
- `tdt-meta`: `docs(openspec): add docker-compose-hygiene-baseline change` (commit `d1857cc8`)

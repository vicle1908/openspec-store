# Spec Delta

## ADDED Requirements

### Requirement: Fresh-Shell and Non-Login Credential Availability for TypeSafe and Custom Gateways

Both login shells (`~/.zshenv`, mode `0600`) and non-login/GUI OMP processes (`~/.omp/agent/.env` mode `0600` and `~/.omp/agent/agent.db` `auth_credentials`) SHALL resolve valid `TYPESAFE_API_KEY`, `OMNIROUTE_API_KEY`, and `HERMES_CUSTOM_{COCKPIT,SHOPAPIKEY,PHANMEMVIP}_API_KEY` credentials without printing secret material, while unfunded `openrouter` credentials and retired empty `.env` keys SHALL be absent.

#### Scenario: Login shell and non-rc shell resolve TypeSafe and custom provider credentials
- **WHEN** a clean login shell (`zsh -lic`) and an un-sourced non-rc shell (`env -u TYPESAFE_API_KEY -u OMNIROUTE_API_KEY -u HERMES_CUSTOM_COCKPIT_API_KEY -u HERMES_CUSTOM_SHOPAPIKEY_API_KEY -u HERMES_CUSTOM_PHANMEMVIP_API_KEY zsh -fc`) invoke OMP model availability and uncached `omp find` checks (`OMP_JUDGMENT_CACHE_DB` set to distinct temporary files)
- **THEN** all five keys SHALL resolve as non-empty credentials in `~/.omp/agent/.env` with `~/.zshenv` and `~/.omp/agent/.env` permissions equal to `0600`, and retired `HERMES_CUSTOM_GIAODUC_API_KEY` and `HERMES_CUSTOM_OMNIROUTE_API_KEY` entries SHALL be absent
- **AND** `typesafe/jev-1.14.0` SHALL be reported available in `omp models --kind judge --json` and complete uncached `omp find` (`stats.requests > 0`, `stats.failed == 0`) in both `zsh -lic` and `zsh -fc` environments without printing secret values

#### Scenario: Unfunded OpenRouter credential removed and TypeSafe enrolled in OMP auth store
- **WHEN** `~/.omp/agent/agent.db` is queried read-only for `auth_credentials` and `auth_credential_blocks`
- **THEN** `SELECT COUNT(*) FROM auth_credentials WHERE provider='openrouter'` and `SELECT COUNT(*) FROM auth_credential_blocks WHERE provider_key GLOB 'openrouter:*'` SHALL both equal `0`
- **AND** `SELECT provider, credential_type, json_extract(data,'$.source') FROM auth_credentials WHERE provider='typesafe'` SHALL return exactly one row `typesafe|api_key|login` with a non-empty `key`

### Requirement: Supersession of Legacy Cockpit Default Role Assertions in Fresh-Shell Contract

The earlier clauses in `omp-fresh-shell-contract` asserting that OMP's `default` role resolves to `phanmemvip/gpt-5.6-sol:max` ARE SUPERSEDED by `omp-provider-routing` (`modelRoles.default: google-antigravity/gemini-4-argon`), and `/Users/androidteam/Developer/.claude/CLAUDE.md` SHALL import `@../AGENTS.md` so `/Users/androidteam/Developer/AGENTS.md` loads without `@-import: file not found` warnings or duplicate skill symlinks.

#### Scenario: Fresh-shell default role and context imports resolve cleanly without warnings
- **WHEN** `omp --no-session -p "reply only: pong"` is executed from `/Users/androidteam/Developer` in a fresh login shell
- **THEN** `modelRoles.default` SHALL resolve to `google-antigravity/gemini-4-argon` and `/Users/androidteam/Developer/.claude/CLAUDE.md` SHALL reference `@../AGENTS.md`
- **AND** the session log under `~/.omp/logs/` SHALL record zero `@-import: file not found` warnings for `/Users/androidteam/Developer/.claude/AGENTS.md` and `~/.omp/agent/skills/herdr` SHALL not duplicate `.agents/skills/herdr`

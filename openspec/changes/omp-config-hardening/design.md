## Context

OMP agent configuration runs at `~/.omp/agent/` with `config.yml` (model roles, compaction, task isolation) and `models.yml` (4 custom providers). Credentials use `HERMES_CUSTOM_*` env vars. No secrets redaction, no fallback chains, no guardrails, no tool approval, no `.env` templates.

Current state:
- **Providers**: giaoduc (local, free), shopapikey (remote, free), cockpit (local, free), omniroute (local, free) — all zero-cost today, but cost behavior is provider-owned and may change
- **Model roles**: giaoduc/Advance serves `task` + `default`, shopapikey/fable-5 serves `smol` + `commit`, cockpit/gpt-5.6-luna serves `slow` + `plan`
- **Env var pattern**: each provider uses `HERMES_CUSTOM_<PROVIDER>_API_KEY` in `models.yml` — functional but not redacted in output
- **No safety infrastructure**: no `secrets.enabled`, no `RULES.md`, no `tools.approval`, no `bashInterceptor`, no `disabledProviders`, no fallback chains

## Goals / Non-Goals

**Goals:**
- Enable secret redaction so leaked keys are masked in tool output
- Add provider fallback chains so sessions survive single-provider outages
- Create `RULES.md` with always-apply guardrails
- Gate destructive bash commands behind user approval
- Prevent accidental routing to disabled providers
- Redirect common bash commands to built-in tools via `bashInterceptor`
- Provide `.env` template for credential setup

**Non-Goals:**
- Changing model role assignments
- Modifying compaction or task isolation settings
- Changing theme or display settings
- Adding new providers

## Decisions

1. **`secrets.enabled: true`** in `config.yml` — OMP's built-in secret redaction, no external tool needed
2. **`RULES.md` location**: `~/.omp/agent/RULES.md` — standard user-level always-apply file, loaded before project-level rules
3. **Fallback chain order**: giaoduc → shopapikey → cockpit → omniroute — most capable to most free, matching cost gradient
4. **`tools.approval`**: bash deny patterns for `rm -rf`, `git push --force`, `chmod 777`, `curl | sh` — targeted at actual destructive commands, not all bash
5. **`bashInterceptor`**: redirect `cat`/`head`/`tail` → `read`, `grep`/`rg` → `grep` — saves context tokens, uses built-in tools
6. **`disabledProviders`**: disable `anthropic`, `openai`, `google` built-ins — prevent accidental routing to paid APIs when custom providers exist
7. **`.env` template**: `~/.omp/agent/.env` with placeholder values and comments — documentation, not functional (credentials stay in shell env)

## Risks / Trade-offs

- Fallback chains add latency on primary failure (acceptable: degraded is better than stalled)
- `RULES.md` guardrails are advisory (model may ignore under pressure, but establishes baseline)
- `bashInterceptor` may surprise users if intercepted commands behave slightly differently
- `disabledProviders` prevents use of built-in providers if custom ones are all down

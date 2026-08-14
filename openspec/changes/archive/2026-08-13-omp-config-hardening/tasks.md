## 1. Secret Redaction

- [x] [historical] 1.1 Add `secrets.enabled: true` to `~/.omp/agent/config.yml`
- [x] [historical] 1.2 Verify redaction works by checking a tool output containing an API key pattern

## 2. Guardrails (RULES.md)

- [x] [historical] 2.1 Create `~/.omp/agent/RULES.md` with sticky guardrails: no .env commits, no push without user confirmation, no `rm -rf` without confirmation, no destructive `chmod` without confirmation
- [x] [historical] 2.2 Verify RULES.md loads by starting a new OMP session and checking context injection

## 3. Provider Fallback Chains

- [x] [historical] 3.1 Add `retry.fallbackChains.default` to `~/.omp/agent/config.yml` with order: giaoduc → shopapikey → cockpit → omniroute
- [x] [historical] 3.2 Verify by checking that config parses without errors

## 4. Tool Approval

- [x] [historical] 4.1 Add `tools.approval.bash.deny` patterns to `~/.omp/agent/config.yml` for `rm -rf`, `git push --force`, `chmod 777`, `curl | sh`
- [x] [historical] 4.2 Verify approval prompt triggers by attempting a denied command in a session

## 5. Bash Interceptor

- [x] [historical] 5.1 Add `bashInterceptor` config to redirect `cat`/`head`/`tail` → `read` tool and `grep`/`rg` → `grep` tool in `~/.omp/agent/config.yml`
- [x] [historical] 5.2 Verify interception works by running `cat` on a file in a session

## 6. Provider Filtering

- [x] [historical] 6.1 Add `disabledProviders` to `~/.omp/agent/config.yml` listing `anthropic`, `openai`, `google` (built-in providers)
- [x] [historical] 6.2 Verify that attempting to route to a disabled provider falls back to next available

## 7. Environment Variable Template

- [x] [historical] 7.1 Create `~/.omp/agent/.env` with placeholder values and comments for all `HERMES_CUSTOM_*` variables
- [x] [historical] 7.2 Verify `.env` is not loaded automatically (documentation only)

## 8. Verification

- [x] [historical] 8.1 Run `openspec verify --change "omp-config-hardening" --json --store openspec-store` to confirm all artifacts align
- [x] [historical] 8.2 Start a new OMP session and verify all configs load without errors


---

> **Historical record:** This change was archived with 16 incomplete task(s) (0/16 completed). The remaining tasks were not implemented or were superseded by subsequent changes.

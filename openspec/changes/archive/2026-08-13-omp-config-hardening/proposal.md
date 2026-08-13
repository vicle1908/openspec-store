# omp-config-hardening

## Why

OMP agent configuration has no safety nets — no secret redaction, no guardrails, no fallback chains, no tool approval gates, and no environment variable fallback.

Four custom providers (omniroute, shopapikey, giaoduc, cockpit) handle all model routing across six role assignments, but zero fallback chains exist — if any provider goes down, sessions stall with no automatic degradation. API keys use env-var indirection (e.g. `HERMES_CUSTOM_SHOPAPIKEY_API_KEY`), but `secrets.enabled` is not set, so leaked keys are unredacted in tool output. No always-apply guardrails exist (`RULES.md` is missing), and destructive bash commands run without approval gates (`tools.approval` defaults to yolo mode). No `.env` files exist at any level, so there is no credential template for new environments or contributors.

The risk compounds: a single provider outage halts the session, a misconfigured output exposes raw API keys, and an unguarded bash invocation can mutate the filesystem with no confirmation.

## What Changes

- Enable secret obfuscation via `secrets.enabled: true` in `config.yml`
- Create `~/.omp/agent/RULES.md` with hard guardrails (no destructive git, no secret leaks, no rm -rf)
- Add `retry.fallbackChains` with cross-provider fallbacks for each model role
- Create `~/.omp/agent/.env` scaffolding with credential template for all four providers
- Add `tools.approval` config with bash deny patterns for destructive commands
- Add `disabledProviders` to prevent accidental routing to offline or expensive providers
- Add `bashInterceptor` to redirect cat/grep to built-in tools
- Create `~/.omp/agent/AGENTS.md` with cross-project conventions

## Capabilities (New)

### omp-config/secrets
Secret obfuscation and credential management. `secrets.enabled: true` redacts API key values from tool output and logs. The `.env` template provides a structured credential store for all providers.

### omp-config/guardrails
Always-apply rules and tool approval gates. `RULES.md` enforces constraints that apply to every session. `tools.approval` gates bash commands matching destructive patterns (rm, git push --force, chmod 777) behind user confirmation. `bashInterceptor` redirects filesystem reads through tools for auditability.

### omp-config/resilience
Provider fallback chains and env var scaffolding. `retry.fallbackChains` enables automatic provider switching on failure — if the primary role provider is unreachable, the session degrades gracefully to the next configured provider instead of stalling.

### omp-config/cost-control
Provider filtering and bash interception. `disabledProviders` prevents accidental routing to expensive or offline providers. `bashInterceptor` reduces unnecessary subprocess spawns by routing common commands through built-in tools.

## Non-Goals

- Changing model role assignments (smol, slow, plan, commit, task, default remain as-is)
- Modifying compaction or task isolation settings
- Changing theme or display preferences
- Adding new model providers
- Modifying the `equivalence` overrides in models.yml
- Changing the `async`, `checkpoint`, or `mcp` configuration sections

## Ownership

- **Owner**: User (OMP config is personal, lives at `~/.omp/agent/`)
- **Affected files**:
  - `~/.omp/agent/config.yml` — add secrets, retry, tools, bashInterceptor, disabledProviders
  - `~/.omp/agent/RULES.md` — new file, always-apply guardrails
  - `~/.omp/agent/.env` — new file, credential template with placeholder values
  - `~/.omp/agent/AGENTS.md` — new file, cross-project conventions
- **No repository code changes** — config files only
- **No models.yml changes** — provider definitions and equivalence mappings unchanged

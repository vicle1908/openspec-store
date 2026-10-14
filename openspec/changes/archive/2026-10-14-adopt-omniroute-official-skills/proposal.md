# Proposal

## Why

OmniRoute ships 45 official agent skills that empower AI coding agents to autonomously inspect models, configure provider connections, manage routing combos, monitor resilience, and tune caching, but none of these skills are currently installed in the workspace agent directory, and the active agent API key lacks the management scopes required to execute them. Adopting these skills now establishes a standardized, vendor-neutral control surface for our local OmniRoute gateway (`127.0.0.1:20128`), allowing agents to self-diagnose provider health and optimize model routing without manual dashboard interventions.

## What Changes

- **Adopt OmniRoute Official Agent Skills**: Install OmniRoute's complete 45-skill catalog from the local repository (`/Users/androidteam/Omniroute/skills`) globally using `npx skills add -g --all`, populating `~/.agents/skills/` and agent-specific discovery roots with canonical symlinks.
- **Grant Management Scopes to Agent Key**: Elevate the active host API key (`mac-mini-1`) in OmniRoute SQLite storage (`/app/data/storage.sqlite`) from `["self:usage"]` to `["self:usage", "manage", "admin"]`, authorizing agents to access `/api/*` management endpoints.
- **Configure Universal Agent Environment**: Export standardized environment variables (`OMNIROUTE_URL="http://localhost:20128"`, `OMNIROUTE_BASE_URL="http://localhost:20128"`, and `OMNIROUTE_KEY="$OMNIROUTE_API_KEY"`) in `~/.zshenv` appended safely outside the `standardize-zshenv-shared-secrets` block (line 43+).
- **Normalize Interactive Shell Configuration**: Update line 221 in `~/.zshrc` to `export OMNIROUTE_BASE_URL=http://localhost:20128` (stripping trailing `/v1`) to prevent interactive shells from overriding `~/.zshenv` with malformed paths, while leaving `COPILOT_PROVIDER_BASE_URL=http://localhost:20128/v1` intact.
- **Document Catalog & Operational Runbook**: Author comprehensive documentation in `/Users/androidteam/Developer/docs/omniroute-agent-skills.md` detailing all 22 `omni-*` REST skills, HTTP endpoints, permission requirements, and curl invocation patterns, and update `/Users/androidteam/Developer/wiki/entities/omniroute.md` to record the active skill surface.
- **Non-Goals (Explicitly Deferred)**:
  - Host `omniroute` CLI binary wrapper (`~/.local/bin/omniroute`) and execution runtime fixes are explicitly deferred to a separate follow-up change.
  - Modifying OmniRoute container build artifacts or Next.js standalone packaging.
  - Modifying provider connection secrets or active routing combos during this onboarding phase.

## Capabilities

### New Capabilities
- `omniroute-agent-skills`: Governance, installation, permission authorization, and runtime integration for OmniRoute official agent skills across multi-agent environments.

### Modified Capabilities
<!-- No requirement changes to existing capabilities -->

## Impact

- **Agent Surfaces**: Adds 45 OmniRoute official skills to `~/.agents/skills/` (and links to Claude Code, Antigravity, Cursor, Codex).
- **OmniRoute Storage**: Updates `scopes` column for `mac-mini-1` in SQLite table `api_keys` on Docker named volume (`omniroute-data`).
- **Shell Environment**: Normalizes `OMNIROUTE_URL`, `OMNIROUTE_BASE_URL`, and `OMNIROUTE_KEY` across both `~/.zshenv` (line 43+) and `~/.zshrc` (line 221) without modifying the protected secrets block.
- **Knowledge Base**: Adds new operational guide `docs/omniroute-agent-skills.md` and updates `wiki/entities/omniroute.md`.
- **System Compatibility**: Zero breaking changes to existing inference routing, Copilot configuration, or Claude Code launcher aliases (`omniroute()`, `cockpit()`).

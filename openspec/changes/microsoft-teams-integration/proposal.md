## Why

The TDT project has a mature DevOps automation ecosystem with Jira (via `acli`) and GitLab (via `glab`) integrations, but lacks Microsoft Teams connectivity. Teams is the primary communication channel for the engineering team, and AI agents need to read messages, post updates, search content, and manage notifications — all headlessly without browser interaction. The existing `skills/microsoft-teams.md` skill file documents the desired capabilities but has no working CLI backend installed or configured. This change fills that gap.

## What Changes

- Install and configure `ms-teams-cli` (Rust binary) as the primary Teams CLI backend
- Create Azure AD app registration "TDT Teams Agent" (already created: `04c4d3cc-6fce-43fd-9f7d-668ae8c19355`)
- Support two-tier authentication: Delegated (device code, dev testing) + Application (client credentials, production)
- Add environment variable configuration to `.env` for agent/CI/CD use
- Implement Teams skill as a proper `.agents/skills/` module with installation, usage, and troubleshooting guides
- Create integration scripts connecting Jira events and GitLab MR events to Teams notifications
- Add automated daily standup report generation and delivery to Teams channels
- Implement retry logic and error handling wrappers for agent-safe operations
- Create comprehensive testing and verification scripts

## Capabilities

### New Capabilities

- `message-operations`: Read, send, reply, pin, and react to channel/chat messages with structured JSON output and stdin piping support
- `channel-management`: List, create, delete, and manage team channels including membership operations
- `user-presence`: Search users, check presence status, mention users in messages, and manage availability
- `search-capabilities`: Full-text search across messages, users, and teams with query filters
- `notification-system`: Send targeted notifications to users, teams, or chats with activity types (taskCreated, deploymentComplete, etc.)
- `agent-integration`: Headless CLI operations with deterministic exit codes, structured JSON output, retry/backoff logic, and profile management for CI/CD and autonomous agent workflows

### Modified Capabilities

<!-- No existing specs are being modified — this is all new functionality -->

## Impact

- **New dependencies:** `ms-teams-cli` binary (Rust, single-file install to `~/.local/bin/teams`)
- **New environment variables:** `TEAMS_CLI_CLIENT_ID`, `TEAMS_CLI_CLIENT_SECRET` (prod only), `TEAMS_CLI_TENANT_ID`, optional `TEAMS_DEFAULT_TEAM_ID`, `TEAMS_DEFAULT_CHANNEL_ID`
- **New scripts:** `scripts/teams-setup.sh`, `scripts/jira-to-teams.sh`, `scripts/daily-standup-to-teams.sh`, `scripts/teams-retry.sh`
- **Modified files:** `.env.example` (add Teams config template), `webhook-receiver/actions/merge_request.sh` (add Teams notification)
- **New skill directory:** `.agents/skills/microsoft-teams-integration/` with `SKILL.md`, `INSTALLATION_GUIDE.md`, `QUICK_START.md`, `AZURE_AD_SETUP.md`
- **Azure AD:** App registration created (`04c4d3cc-6fce-43fd-9f7d-668ae8c19355`), pending IT admin consent for Application permissions
- **Tenant:** Phillip Securities Pte Ltd (`98f9bd1e-30d7-4dee-858b-be7f4540eceb`)
- **No breaking changes** — this is purely additive

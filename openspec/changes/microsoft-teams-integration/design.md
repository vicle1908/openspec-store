## Context

The TDT project already has a documented Microsoft Teams integration skill at `skills/microsoft-teams.md` but no working backend. The project uses a CLI-based automation pattern: `acli` for Jira, `glab` for GitLab, and this change introduces `teams` (ms-teams-cli) for Microsoft Teams. The ecosystem includes a webhook-receiver for GitLab events, daily Jira report scripts, and an agent-driven workflow system in `.agents/skills/`. Teams is the primary communication channel for the engineering team, and agents need to read messages, post updates, search content, and manage notifications — all headlessly without browser interaction.

**Constraints:**
- Must work on macOS (Apple Silicon — `aarch64-apple-darwin`)
- Supports both Delegated (device code) and Application (client credentials) auth flows
- Must return structured JSON with deterministic exit codes for agent parsing
- Must not break existing Jira/GitLab integrations
- Binary installation must not use Homebrew tap (not yet available)
- Phillip Securities Pte Ltd tenant requires IT admin consent for Application permissions
- Installed binary path: `~/.local/bin/teams` (user-writable, already in PATH)

## Goals / Non-Goals

**Goals:**
- Install and authenticate `ms-teams-cli` as a working CLI backend
- Enable all documented skill capabilities: read/send messages, search, mention, presence, notifications
- Integrate Teams into existing Jira and GitLab event workflows
- Provide agent-safe retry logic and error handling
- Create comprehensive documentation for setup, usage, and troubleshooting

**Non-Goals:**
- Building a Teams bot or conversational UI inside Teams
- Real-time webhook subscription management (covered by `teams listen` but not a priority)
- Adaptive Cards creation (text/HTML only for now)
- Teams app development or publishing

## Decisions

### D1: Primary Backend — ms-teams-cli (Rust) over alternatives

| Option | Stars | Agent-First | Headless | Exit Codes | Single Binary |
|--------|-------|-------------|----------|------------|---------------|
| **ms-teams-cli** | 12 | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| cli-microsoft365 (PnP) | 1,342 | ❌ No | ✅ Yes | ❌ No | ❌ No (Node.js) |
| teams-mcp (MCP server) | 99 | ⚠️ MCP-only | ✅ Yes | ❌ No | ❌ No (Node.js) |

**Rationale:** ms-teams-cli matches the existing CLI pattern (acli/glab), has deterministic exit codes for agent branching, structured JSON output, and a single Rust binary with no runtime. The small community is mitigated by pinning the version and verifying checksums.

### D2: Authentication — Two-Tier Approach

**Development/Testing:** Device code flow (`teams auth login --device-code`) with Delegated permissions. Requires one-time browser interaction per session, then tokens are cached. Good for initial setup and dev testing.

**Production/CI/CD:** Client credentials flow (`teams auth login --client-credentials`) with Application permissions. Fully headless, requires admin consent. Used by agents and automation pipelines.

**Credential Resolution:** CLI flags > environment variables > config file profiles. `TEAMS_CLI_ACCESS_TOKEN` bypasses login entirely.

**Rationale:** Admin consent for Application permissions requires IT involvement and can take days. Device code flow with Delegated permissions enables immediate dev testing while waiting for production approval. Both flows use the same app registration.

**Permission Matrix:**
| Flow | Permissions | Admin Consent | Teams Operations |
|------|-------------|---------------|------------------|
| Device code (Delegated) | User.Read, offline_access, openid | No (self-consent) | ❌ Limited to user profile |
| Device code (Delegated + consent) | All Delegated permissions | No (self-consent if allowed) | ✅ Read/send as authenticated user |
| Client credentials (Application) | All Application permissions | Yes (IT required) | ✅ Full access, cross-user operations |

### D3: Binary Installation — Direct Download (not Homebrew)

Since Homebrew tap isn't available, download pre-built binary from GitHub Releases and place in `/usr/local/bin/teams`.

**Rationale:** Simplest path. Single file, no package manager dependency. Can upgrade by replacing binary.

### D4: Skill Location — `.agents/skills/microsoft-teams-integration/`

Move the documentation from `skills/microsoft-teams.md` into a proper skill directory with `SKILL.md`, `INSTALLATION_GUIDE.md`, and `QUICK_START.md`.

**Rationale:** Matches the pattern used by other agent skills in `.agents/skills/`. Keeps documentation close to the automation code.

### D5: Integration Pattern — Shell Scripts, Not Daemon

All Teams operations are invoked via shell scripts called from existing workflows (webhook-receiver actions, cron jobs). No persistent daemon or service.

**Rationale:** Matches existing `acli` and `glab` patterns. Stateless, easy to debug, no additional infrastructure.

## Risks / Trade-offs

| Risk | Impact | Mitigation |
|------|--------|-----------|
| ms-teams-cli is young (v0.1.0, 12 stars) | Medium — bugs, breaking changes | Pin version, test thoroughly, contribute fixes upstream if needed |
| Azure AD admin consent required | High — blocks setup if admin unavailable | Document exact permission list; provide fallback to Delegated permissions for dev testing |
| Client secret expiration (24 months) | Medium — auth breaks without notice | Add calendar reminder; document rotation process in INSTALLATION_GUIDE.md |
| Rate limiting (60 msg/min) | Low — unlikely in normal use | Built-in retry with exponential backoff (`scripts/teams-retry.sh`) |
| legacy cloud workspace sync conflicts on `.env` | Low — `.env` is gitignored | Keep `.env.example` in repo with template values only |
| Binary not codesigned (macOS Gatekeeper) | Medium — may block execution | Use `xattr -dr com.apple.quarantine` if needed; verify checksum from GitHub Releases |

## Migration Plan

### Phase 1: Setup (DONE)
1. ✅ Download `ms-teams-cli` binary (v0.1.0, aarch64-apple-darwin, 2.9MB)
2. ✅ Install to `~/.local/bin/teams` (user-writable PATH location)
3. ✅ Create Azure AD app registration "TDT Teams Agent" (`04c4d3cc-6fce-43fd-9f7d-668ae8c19355`)
4. ✅ Update `.env.example` with Teams configuration template
5. ✅ Create setup documentation and scripts

### Phase 2: Authentication (IN PROGRESS)
6. ⏳ Add Delegated permissions for dev testing (User.Read, offline_access, openid, email, profile)
7. ⏳ Test device code auth flow (`teams auth login --device-code`)
8. ⏳ Add Application permissions for production (8 Graph API permissions)
9. ⏳ Request IT admin consent for Application permissions
10. ⏳ Create client secret and test client credentials flow

### Phase 3: Integration (PENDING)
11. Test verification suite (list teams, send message, search users)
12. Add Teams notifications to existing Jira/GitLab workflows
13. Create retry and error handling scripts
14. Update skill files and AGENTS.md

**Rollback:** Remove binary (`rm ~/.local/bin/teams`), unset env vars, delete Azure AD app registration. No data persistence to roll back.

## Open Questions

- **Q1:** Should we also install `teams-mcp` as a secondary backend for MCP-compatible agents (Claude Desktop)? → *Defer — can add later without breaking CLI integration.*
- **Q2:** Should Teams notifications be synchronous (block on failure) or async (fire-and-forget) in webhook-receiver? → *Async (non-blocking) — Teams failures should not block GitLab/Jira workflows.*
- **Q3:** Which specific Teams channels should receive automated notifications? → *Document as configurable via `TEAMS_DEFAULT_TEAM_ID` and `TEAMS_DEFAULT_CHANNEL_ID`; let team lead decide per environment.*

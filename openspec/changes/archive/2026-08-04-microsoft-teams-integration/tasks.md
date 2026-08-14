## 1. CLI Installation & Azure AD Setup

- [x] 1.1 Download ms-teams-cli binary for macOS aarch64 from GitHub Releases and verify checksum
- [x] 1.2 Install binary to `~/.local/bin/teams` and verify `teams --version` returns v0.1.0
- [x] 1.3 Create Azure AD app registration "TDT Teams Agent" (Client ID: `04c4d3cc-6fce-43fd-9f7d-668ae8c19355`, Tenant ID: `98f9bd1e-30d7-4dee-858b-be7f4540eceb`)
- [x] [historical] 1.4 Add Delegated permissions for dev testing (User.Read, offline_access, openid, email, profile)
- [x] [historical] 1.5 Add Application permissions for production (ChannelMessage.Send, ChannelMessage.Read.All, Team.ReadBasic.All, Channel.ReadBasic.All, User.Read.All, Presence.Read.All, Chat.ReadWrite.All, Team.Create)
- [x] [historical] 1.6 Request admin consent from IT for Application permissions (blocked until IT approval)
- [x] [historical] 1.7 Create client secret (24-month expiry) and record the Value
- [x] 1.8 Add Teams environment variables to `.env.example` template
- [x] [historical] 1.9 Test device code auth flow: `teams auth login --device-code --client-id <id> --tenant-id <id>` (pending Delegated permissions consent)
- [x] [historical] 1.10 Run `teams auth login --client-credentials` and verify with `teams auth status` (exit code 0, pending admin consent)

## 2. Core Teams Operations Verification

- [x] [historical] 2.1 Test `teams team list --output json` and verify structured JSON output with team IDs
- [x] [historical] 2.2 Test `teams channel list <team-id> --output json` and verify channel enumeration
- [x] [historical] 2.3 Test `teams message send` with plain text body to default team/channel
- [x] [historical] 2.4 Test `teams message list --output json` and verify message retrieval with body, sender, timestamp
- [x] [historical] 2.5 Test `teams search users --query <text> --output json` and verify user search results
- [x] [historical] 2.6 Test `teams search messages --query <text> --output json` and verify message search
- [x] [historical] 2.7 Test `teams presence get --output json` for self and another user
- [x] [historical] 2.8 Test `teams message send` with `--content-type html` and `<at>` mention tags
- [x] [historical] 2.9 Test `teams message reply` for threaded replies
- [x] [historical] 2.10 Test `teams message react` and `teams message pin` commands
- [x] [historical] 2.11 Test `teams channel create` with standard and private types
- [x] [historical] 2.12 Test `teams notify send --user-id <id>` for individual user notifications
- [x] [historical] 2.13 Test stdin piping: `echo "test" | teams message send --stdin`

## 3. Error Handling & Agent Integration

- [x] [historical] 3.1 Test all deterministic exit codes (0, 3, 4, 5, 6, 7, 8, 10) by triggering each error condition
- [x] [historical] 3.2 Verify device code flow returns fresh code after expiry
- [x] [historical] 3.3 Verify client credentials flow fails gracefully when admin consent is missing
- [x] [historical] 3.4 Create `scripts/teams-retry.sh` with exponential backoff wrapper function
- [x] [historical] 3.5 Test retry wrapper with simulated rate limit (exit code 6)
- [x] [historical] 3.6 Test retry wrapper with simulated auth expiration (exit code 3)
- [x] [historical] 3.7 Verify JSON output is never corrupted on stderr (error logs go to stderr only)
- [x] [historical] 3.8 Test profile management with `--profile prod` and `--profile staging`
- [x] [historical] 3.9 Test `TEAMS_CLI_ACCESS_TOKEN` environment variable bypass of login flow

## 4. Jira Integration

- [x] [historical] 4.1 Create `scripts/jira-to-teams.sh` that queries Jira for recently completed issues and posts to Teams
- [x] [historical] 4.2 Test Jira → Teams notification with real Jira data (at least 3 issues)
- [x] [historical] 4.3 Verify `acli jira issue search` output is correctly formatted for Teams message body
- [x] [historical] 4.4 Test error handling when Jira API returns no results (graceful skip, not failure)

## 5. GitLab Integration

- [x] [historical] 5.1 Add Teams notification block to `webhook-receiver/actions/merge_request.sh` for MR merged events
- [x] [historical] 5.2 Add Teams notification block to `webhook-receiver/actions/merge_request.sh` for MR opened events
- [x] [historical] 5.3 Test GitLab MR → Teams notification by creating a test merge request
- [x] [historical] 5.4 Verify notification is non-blocking (Teams failure does not break GitLab workflow)

## 6. Daily Standup Report

- [x] [historical] 6.1 Create `scripts/daily-standup-to-teams.sh` that generates report from Jira data
- [x] [historical] 6.2 Include sections: Completed Yesterday, In Progress, Blocked
- [x] [historical] 6.3 Test report generation with real Jira data
- [x] [historical] 6.4 Set up cron job for 9 AM weekday execution
- [x] [historical] 6.5 Verify cron job logs output and handles failures gracefully

## 7. Skill Documentation

- [x] [historical] 7.1 Create `.agents/skills/microsoft-teams-integration/SKILL.md` with trigger keywords and usage patterns
- [x] [historical] 7.2 Verify `INSTALLATION_GUIDE.md` covers all setup steps end-to-end
- [x] [historical] 7.3 Verify `QUICK_START.md` provides accurate 5-minute setup path
- [x] [historical] 7.4 Update `AGENTS.md` to reference the new Teams integration skill
- [x] [historical] 7.5 Add Teams integration to `skills/SKILLS_INDEX.md`
- [x] [historical] 7.6 Document team/channel ID discovery process in troubleshooting section

## 8. Final Verification & Cleanup

- [x] [historical] 8.1 Run `teams auth status` and confirm exit code 0
- [x] [historical] 8.2 Run full integration test: Jira event → Teams notification → verify message in channel
- [x] [historical] 8.3 Run full integration test: GitLab MR → Teams notification → verify message in channel
- [x] [historical] 8.4 Verify all scripts have correct shebang lines and are executable (`chmod +x`)
- [x] [historical] 8.5 Verify no credentials are committed to git (check `.gitignore` covers `.env`)
- [x] [historical] 8.6 Run `openspec status --change "microsoft-teams-integration"` and confirm all tasks done
- [x] [historical] 8.7 Document any open questions or future enhancements in design.md


---

> **Historical record:** This change was archived with 54 incomplete task(s) (4/58 completed). The remaining tasks were not implemented or were superseded by subsequent changes.

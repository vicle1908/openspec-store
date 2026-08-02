## Why

The active Hermes Agent installation should operate as a fully capable local development and automation agent from both CLI/Desktop and the authorized Telegram gateway. The earlier proposal's least-privilege tool and MCP filtering conflicts with that objective, while the current runtime configuration still needs full-access and reliability corrections. This change therefore standardizes full technical capability, unattended execution, and autonomous learning while preserving the security floors Hermes cannot or should not bypass.

## What Changes

- Verify the now-current schema v33 configuration, use the supported migration path after future schema drift, and remove any deprecated configuration reported by diagnostics.
- Keep `default` as the single shared profile for CLI, Desktop, authorized Telegram, memory, skills, sessions, cron, credentials, and MCP; enable every installed platform-applicable toolset for CLI and Telegram and persist the Kanban exception.
- Preserve the existing `mcp-router` server definition byte-for-byte and expose its currently configured complete tool surface; the change SHALL NOT pin, reinstall, reconfigure, filter, reload, or otherwise mutate that MCP server.
- Permit parallel execution of independent built-in, plugin, and MCP tool calls, including setting the existing `mcp-router` server's parallel-call capability flag without changing its command, arguments, environment, credentials, filters, or protocol feature settings.
- Configure Hermes full-access execution mode: command approvals off, dangerous cron commands approved, destructive session confirmations off, and MCP reload confirmation off.
- Permit private/local-network URLs, unrestricted browser evaluation, and allowlisted Hermes lazy dependency installation.
- Allow memory and skill writes to land without write-approval staging so the learning loop can operate autonomously.
- Preserve full local terminal/file/browser/code-execution capability and enable all available media, automation, integration, orchestration, and desktop capabilities when their runtime prerequisites are present.
- Preserve secret redaction, credential-file separation, Telegram user authorization, Hermes' immutable hardline command blocklist, protected credential paths, provider/service authorization, and repository-local policy requirements.
- Keep loop detection, explicit per-turn search/subagent caps, bounded concurrency, context compression, diagnostics, and separately verified quick/full rollback artifacts so full access does not become silent or unrecoverable.
- Preserve the all-tools policy efficiently through Tool Search progressive disclosure, offline prompt-size baselines, explicit cron delivery/model routing, token/cost trend review, and durable gateway completion/recovery checks.
- Correct the invalid timezone and unsupported `service_tier: auto` value, then verify the complete configuration through CLI, Desktop, Telegram, MCP, memory, skill, cron, browser, terminal, and delegation smoke tests.

## Capabilities

### New Capabilities

- `hermes-profile-governance`: Govern intentional shared-state use of `default` across CLI/Desktop and authorized Telegram, with source/chat-separated sessions and one gateway owner.
- `hermes-configuration-safety`: Define schema verification/migration, full-access approval bypass, autonomous writes, credential boundaries, backup, validation, and rollback behavior.
- `hermes-runtime-efficiency`: Preserve prompt caching, compression, loop detection, delegation, observability, and reliable automation under a full-access configuration.
- `hermes-mcp-exposure-control`: Preserve the existing MCP Router setup unchanged while exposing all current operations and permitting parallel invocation.

### Modified Capabilities

- None. No existing TDT product capability requirement changes; this is a local Hermes operational-governance contract.

## Impact

- **Primary target:** the existing `/Users/lekhanhvinh/.hermes/` default profile and its launchd-managed `ai.hermes.gateway` service during an explicitly authorized apply phase.
- **Planning repository:** `tdt-meta/openspec/changes/optimize-hermes-agent-configuration/`.
- **Behavioral impact:** Both authorized Hermes surfaces can invoke destructive local commands, mutate files and repositories, access private network services, install supported optional dependencies, mutate memory and skills, manage cron jobs, and call every enabled MCP operation without Hermes approval prompts.
- **Expected state changes:** default-profile `config.yaml`, CLI/Telegram tool settings, the single `mcp-router.supports_parallel_tool_calls` flag, restart of the existing launchd gateway, and backup/evidence artifacts. No profile is created and no Telegram-token ownership transfer occurs.
- **Repositories:** No application source, API, database, dependency lockfile, or deployment manifest change is planned by this proposal itself.
- **External dependencies:** Missing optional capabilities may require separately approved package installation or credential/service setup during apply. The local backend remains the execution backend unless separately changed. This change does not execute a candidate MCP Router package, install or pin it, or alter the existing `npx -y @mcp_router/cli@latest connect` definition.
- **Operational risk:** **CRITICAL**. Prompt injection or model error can cause destructive host, repository, network, service, or shared-state actions with no Hermes approval prompt. The Telegram authorization boundary and credential hygiene are therefore mandatory prerequisites.
- **Blast radius:** The owning macOS user account, every file and CLI credential visible to that account, private/local network targets, enabled MCP services, configured messaging destinations, cron automation, and any external service reachable through installed tools.

## Non-Goals

- Do not disable secret redaction, expose credential values, make Telegram public, or set global/platform allow-all user authorization.
- Do not remove or attempt to bypass Hermes' immutable hardline blocklist, protected credential-path guards, provider/service permissions, runtime prerequisite checks, or repository-local authority rules.
- Do not treat `approvals.mode: off` as authorization to commit, push, publish, deploy, delete shared state, install packages, or perform other outward/destructive operations outside the user's contemporaneous request and applicable repository policy.
- Do not update Hermes source, install packages, rotate credentials, restart services, or mutate external systems while revising this proposal.
- Do not modify the existing MCP Router command, package reference, arguments, environment, secret scope, tool/resource/prompt filters, sampling, elicitation, timeout, or reload behavior. Only the Hermes-side parallel-call declaration is in scope.
- Do not create, clone, activate, or install a gateway for a named Telegram profile. Reconsider profiles only if identity, credentials, memory, skills, cron, provider policy, users, or bot tokens must diverge.
- Do not delete existing sessions, memories, skills, logs, caches, checkpoints, cron jobs, or profiles as part of optimization.
- Do not change unrelated OpenSpec changes or pre-existing dirty files in `tdt-meta`.

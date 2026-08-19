## Context

See `proposal.md` for motivation. The target is the installed Hermes Agent v0.20.3 (2026.8.16.2) on macOS, a launchd-managed Telegram gateway, local terminal execution, a current v37 configuration, and one MCP router currently exposing all tools through an unpinned package reference. (2026-08-18 host reconciliation: this change was authored against a v0.19.0/schema-v33 baseline on `/Users/lekhanhvinh/`; the live machine is v0.20.3/schema-v37 on `/Users/androidteam/`. Scattered inline references to v0.19.0 remain from the original baseline and are superseded by this note where they describe version-specific behavior.) CLI and Telegram already expose most core capabilities. The final design intentionally expands this to every installed and platform-applicable capability and removes Hermes approval gates for the authorized user.

Full access is a capability decision, not a public-access decision. Telegram remains restricted to the configured allowed user(s). Secrets stay in Hermes credential stores and remain redacted. Repository instructions, service permissions, platform authorization, and action-specific approvals remain authority even though Hermes' own shell approval prompt is disabled.

## Goals / Non-Goals

**Goals:**

- Give CLI/Desktop and the authorized Telegram gateway every installed, usable Hermes tool and MCP operation.
- Permit terminal, file, browser, private-network, code-execution, autonomous learning, lazy-install, cron, nested delegation, media, desktop, integration, and shared-service operations without Hermes approval prompts.
- Separate interactive and Telegram state without reducing either profile's technical capability.
- Retain prompt-cache discipline, compression, diagnostics, hardline protections, authorization, backups, and rollback.
- Make unavailable capabilities observable as missing prerequisites rather than silently treating them as enabled.

**Non-Goals:**

- No public/open Telegram bot.
- No secret-redaction bypass or credential-value disclosure.
- No attempt to bypass immutable Hermes hardline blocks or protected credential paths.
- No application code or Hermes source-code changes.
- No implicit package installation, credential provisioning, service mutation, gateway restart, or shared-state mutation during planning.

## Decisions

### 1. Use supported Hermes commands as the only configuration mutation boundary

Apply uses `hermes config`, `hermes profile`, `hermes tools`, `hermes mcp`, `hermes gateway`, and supported auth/setup commands. Direct YAML editing is excluded because migration/default logic and secret routing belong to Hermes.

**Alternative considered:** direct edits for speed. Rejected because stale keys, secret misplacement, indentation errors, and live-gateway reload races are more likely.

### 2. Keep one shared default profile and one existing gateway

The existing `default` profile remains the single Hermes identity for CLI, Desktop, Telegram, cron, memory, skills, credentials, MCP, logs, and backups. CLI/Desktop instantiate local agent processes directly and do not need a gateway. The existing `ai.hermes.gateway` launchd process remains the sole Telegram adapter, cron ticker, and Telegram-token owner. No named profile, gateway multiplexer, second launchd service, profile clone, credential copy, OAuth reauthentication, or token transfer is introduced.

Sharing is intentional: configuration, provider credentials, SOUL, curated memory, skills, cron, and MCP remain common across surfaces, while active conversations remain separated by CLI session IDs or Telegram platform/chat/topic keys in the shared `state.db`. This supplies one learned agent across local and remote surfaces without claiming that a profile is a filesystem sandbox. The local backend continues to expose the real OS-user `HOME` and its Git, SSH, cloud, npm, and developer CLI identities.

**Alternative considered:** a dedicated Telegram profile and gateway. Deferred because there is one trusted user, one bot token, one desired capability policy, and useful memory/skill sharing. Revisit only if Telegram needs a different identity, model/provider, credentials, tools, memory, skills, cron fleet, users, or bot token.

### 3. Enable every installed platform-applicable toolset

The target is not a curated coding bundle. Apply explicitly enables every platform-applicable entry shown by `hermes tools list --platform cli` and `--platform telegram`: web, browser, terminal, file, code execution, vision, video, image/video generation, X search, TTS, skills, todo, memory, session search, clarify, delegation, cron, Home Assistant, Spotify, Yuanbao, computer use, plus installed plugin toolsets. STT is configured through its own `stt.enabled` and provider settings because it is config-only, not a model toolset.

Hermes v0.19.0 has no supported `all`/`*` non-interactive toolset wildcard: `hermes tools enable` accepts concrete configurable names only. Project tools are GUI-only and deliberately excluded from CLI/messaging schemas. Kanban is a valid static toolset but is not accepted by `hermes tools enable`; the installed runtime exposes it to ordinary profile sessions only when `kanban` is explicitly present in that platform's stored toolset list. Apply therefore enables every concrete configurable name, then uses the supported generic config setter to replace one existing list element with `kanban` and re-runs `hermes tools enable` so the replaced configurable entry is restored while the non-configurable `kanban` entry is preserved. The configurable `context_engine` entry is enabled, but it supplies tools only when a non-default context engine is active. Project remains verified only in Desktop/GUI because changing that narrow-waist placement requires Hermes source modification, which is out of scope.

**Alternative considered:** enable only the `coding` composite or disable unavailable media tools. Rejected because the user explicitly chose full capability rather than least privilege.

### 4. Disable Hermes approval gates for authorized default-profile sessions

The effective target is:

- `approvals.mode: off`
- `approvals.cron_mode: approve`
- `approvals.mcp_reload_confirm: false`
- `approvals.destructive_slash_confirm: false`
- no user-defined deny rules
- `memory.write_approval: false`
- `skills.write_approval: false`
- `delegation.subagent_auto_approve: true`
- `approvals.deny`, `command_allowlist`, and `agent.disabled_toolsets` absent so their schema defaults resolve to empty lists

This removes command, cron, subagent-thread, destructive-session, MCP-reload, memory-write, and skill-write prompts/staging. `command_allowlist` is unnecessary in `off` mode and remains empty to avoid stale policy.

**Alternative considered:** smart/manual approval with a broad allowlist. Rejected because it does not satisfy the requested prompt-free all-operations behavior and is harder to audit than one explicit mode.

### 5. Permit private-network and unrestricted browser operations

Both `security.allow_private_urls` and `browser.allow_private_urls` are enabled. `browser.allow_unsafe_evaluate` is enabled and `browser.restrict_evaluate` is disabled. The gateway may therefore navigate localhost, RFC1918, and other private-network applications and evaluate page JavaScript using the current browser context. Hermes' unconditional cloud-metadata/link-local credential-endpoint floor remains blocked even under this full-access setting and is reported as an immutable exception rather than falsely claimed as reachable.

**Alternative considered:** keep SSRF and browser-evaluation guards. Rejected because they block classes of local development and administration operations included in the full-access goal.

### 6. Allow autonomous self-improvement and supported lazy installs

Memory and skill write-approval gates remain off. Hermes may add, replace, remove, create, patch, or delete its profile-local memory and skills through its normal learning loop. `security.allow_lazy_installs` remains true so bundled allowlisted optional dependencies may install into the Hermes virtual environment on first use.

This does not authorize arbitrary package specifications: Hermes lazy installs remain venv-scoped, package-name-only, and restricted to the in-tree allowlist. Other package installation paths remain separately authorized operations.

### 7. Expose every operation from verified MCP servers

The existing `mcp-router` server definition is an immutable input to this change. Apply SHALL NOT alter its command, `@latest` package reference, arguments, environment, credential references, timeout/connect policy, tool/resource/prompt filters, sampling, elicitation, reload behavior, or any other MCP server setting. It records a redacted structural fingerprint before default-profile work and verifies the same fingerprint afterward; no `hermes mcp add`, `remove`, `configure`, `test`, package probe, or reload is part of apply.

All currently registered MCP Router operations remain exposed. Hermes-side parallel dispatch is explicitly enabled with `mcp_servers.mcp-router.supports_parallel_tool_calls=true`, while `agent.parallel_tool_call_guidance=true` remains enabled for all tools. This does not filter or serialize MCP calls: when a model emits independent calls in one turn, Hermes may dispatch them concurrently, including calls from the same MCP Router server. The runtime still preserves result association and underlying hooks for each real tool name. This is an accepted CRITICAL-risk concurrency choice: operations that race over shared mutable state can conflict, duplicate effects, or observe non-serializable state.

No tool-call quota, per-server call denylist, operation-class filter, or MCP-specific serialization gate is introduced. Tool Search's `max_search_limit=20` limits only the number of discovery results returned by one catalog search; it does not limit how many tools may be described or called, and it does not remove any operation from the granted session surface.

Runtime evidence uses the installed double-underscore name form `mcp__<server>__<tool>`. The current transport remains the accepted unpinned baseline for this change; supply-chain pinning is explicitly deferred rather than coupled to the full-access/profile work.

### 8. Preserve reliability controls that do not selectively deny valid operations

Automatic compression remains enabled. Tool-loop warnings and hard stops remain enabled for repeated failure/no-progress patterns. The v0.19.0 per-turn cap keys are `tool_loop_guardrails.loop_caps.max_web_searches` and `.max_subagents`; apply retains the finite value 50 for each unless the baseline demonstrates a lower reviewed limit is required. Delegation uses `max_concurrent_children=3`, `orchestrator_enabled=true`, `max_spawn_depth=2`, `child_timeout_seconds=0`, and `max_iterations=50`. Timeout zero disables only the child wall-clock timeout, so the iteration, concurrency, loop, and stuck-child controls remain the bound. These controls block pathological repetition, not operation categories.

The all-tools policy does not require every MCP/plugin schema to be eager on every turn. Hermes Tool Search is explicitly configured as `tools.tool_search.enabled=auto`, `threshold_pct=5`, `search_default_limit=5`, `max_search_limit=20`, `listing=auto`, and `listing_max_tokens=20000`. Core Hermes tools remain eager; every deferred MCP/plugin capability remains discoverable through the embedded manifest or server summary and callable through `tool_search` → `tool_describe` → `tool_call`. Apply records offline `hermes prompt-size --platform cli --json` and `--platform telegram --json` baselines before and after MCP exposure, then verifies representative deferred read-only and mutating schemas by exact name in fresh sessions. This addresses community evidence of high fixed tool-schema overhead without removing capability.

The user-stories corpus supplies anecdotal evidence—not configuration authority—that long-running cron, self-learning skills, isolated profiles, completion notifications, and multi-agent observability are real operating patterns. Every agent-backed cron job therefore uses an explicit delivery target, workdir, and provider/model policy; global-model drift must fail closed for unpinned jobs. Fixed-output watchdogs use script-only `no_agent` mode to avoid unnecessary inference. `attach_to_session` is enabled only for conversational briefings that should accept follow-up replies. Review uses `hermes insights`, session statistics, cron history, and offline prompt-size output. Hermes v0.19.0 has no verified built-in monetary hard cap, so any future provider/proxy budget limit remains a separate integration change rather than an undeclared prerequisite.

Autonomous skill creation remains enabled, while installed curator defaults remain conservative and explicit: `curator.enabled=true`, `consolidate=false`, `stale_after_days=30`, `archive_after_days=90`, and `backup.enabled=true` with five retained snapshots. Apply runs `hermes curator run --dry-run` and verifies a labeled manual backup/list operation before relying on automatic archival. It does not force consolidation, rollback, or a mutating curator pass during activation. This preserves learning while making community-reported skill growth/rot observable and recoverable without introducing automatic aux-model spend.

### 9. Preserve unavoidable and intentional security floors

Full access does not change:

- secret redaction;
- protected credential paths for `write_file`/`patch`;
- the immutable catastrophic-command hardline blocklist;
- context/memory/skill injection scanning;
- gateway user authorization;
- provider and service credentials/scopes;
- runtime availability checks;
- repository-local rules and required outward/destructive approvals.

The local terminal still runs with the OS user's permissions and can reach far more state than `write_file`/`patch`; this is an accepted CRITICAL-risk property of the selected design.

### 10. Back up, validate, activate, and rollback atomically

Routine updates use `updates.pre_update_backup: quick` because Hermes home is large. Before the CRITICAL-risk in-place activation, apply also creates (1) `hermes backup --quick --label pre-full-access-activation` for critical default-profile state and (2) a full `hermes backup --output <outside-HERMES_HOME>` archive. The quick manifest MUST show no `failed_dbs` or `oversized_skipped` entries and copied SQLite databases MUST pass integrity checks. The full archive MUST complete without skipped-file warnings and pass zip integrity/marker checks. Quick rollback uses classic CLI `/snapshot restore <id>` with all gateway/Desktop/TUI processes stopped; `hermes snapshot ...` is not a valid top-level command in v0.19.0. Full rollback uses `hermes import <archive>` only after all Hermes processes stop and with explicit destructive-restore approval.

No gateway cutover occurs. After backup and read-only validation, configuration is applied to `default`; fresh CLI sessions validate local behavior, then the existing `ai.hermes.gateway` service is restarted in place under explicit service-mutation approval. Activation verifies the same launchd label, default profile home, one Telegram-token owner, a new supervised PID, platform health, logs, and an authorized round-trip. Rollback restores prior default-profile state if needed and restarts the same service; it never installs or uninstalls another gateway.

Gateway long-turn/recovery settings remain explicit at bounded v0.19.0 values: `agent.gateway_timeout=1800`, `agent.gateway_timeout_warning=900`, `agent.gateway_notify_interval=180`, `agent.gateway_auto_continue_freshness=3600`, `agent.gateway_startup_restore_drain_timeout=30`, `agent.build_wait_timeout=600`, `agent.restart_drain_timeout=0`, and `gateway.delivery_ledger=true`. Active work receives periodic feedback; stale interruptions do not revive unrelated old tasks; startup restore cannot block every inbound channel indefinitely; restart interrupts rather than entering an unbounded drain; and a finalized response not acknowledged before a crash is retried at least once with duplicate ambiguity visible. Activation verifies these semantics through supported state/status surfaces and authorized round-trips, never by editing the ledger database or corrupting live state.

The deterministic gateway starting directory is `/Users/androidteam/Developer`: it exists and is not itself a Git repository. Each task MUST enter a verified target repository before running Git.

### 11. Exact common configuration target

All scalar mutations use profile-scoped `hermes config set`; list-valued deny/allow/disabled overrides use `hermes config unset` so schema defaults resolve to empty lists rather than accidentally storing the literal string `[]`.

```text
timezone=Asia/Ho_Chi_Minh
agent.service_tier=fast
approvals.mode=off
approvals.cron_mode=approve
approvals.mcp_reload_confirm=false
approvals.destructive_slash_confirm=false
memory.memory_enabled=true
memory.user_profile_enabled=true
memory.write_approval=false
skills.write_approval=false
security.allow_private_urls=true
security.redact_secrets=true
security.allow_lazy_installs=true
security.website_blocklist.enabled=false
browser.allow_private_urls=true
browser.allow_unsafe_evaluate=true
browser.restrict_evaluate=false
tools.tool_search.enabled=auto
tools.tool_search.threshold_pct=5
tools.tool_search.search_default_limit=5
tools.tool_search.max_search_limit=20
tools.tool_search.listing=auto
tools.tool_search.listing_max_tokens=20000
tool_loop_guardrails.warnings_enabled=true
tool_loop_guardrails.hard_stop_enabled=true
tool_loop_guardrails.loop_caps.max_web_searches=50
tool_loop_guardrails.loop_caps.max_subagents=50
delegation.inherit_mcp_toolsets=true
delegation.max_iterations=50
delegation.max_concurrent_children=3
delegation.max_spawn_depth=2
delegation.orchestrator_enabled=true
delegation.child_timeout_seconds=0
delegation.subagent_auto_approve=true
agent.parallel_tool_call_guidance=true
compression.enabled=true
agent.gateway_timeout=1800
agent.gateway_timeout_warning=900
agent.gateway_notify_interval=180
agent.gateway_auto_continue_freshness=3600
agent.gateway_startup_restore_drain_timeout=30
agent.build_wait_timeout=600
agent.restart_drain_timeout=0
gateway.delivery_ledger=true
mcp_servers.mcp-router.supports_parallel_tool_calls=true
curator.enabled=true
curator.consolidate=false
curator.stale_after_days=30
curator.archive_after_days=90
curator.backup.enabled=true
curator.backup.keep=5
updates.pre_update_backup=quick
updates.backup_keep=5
terminal.backend=local
terminal.home_mode=auto
terminal.cwd=/Users/androidteam/Developer
```

The common unset set is `approvals.deny`, `command_allowlist`, `agent.disabled_toolsets`, and the deprecated `delegation.max_async_children`. No MCP Router setup field is changed except `supports_parallel_tool_calls=true`; existing absence or presence of tool/resource/prompt filters, sampling, elicitation, timeouts, transport, and credentials is preserved exactly. The concrete configurable platform target is: `web browser terminal file code_execution vision video image_gen video_gen x_search tts skills todo memory context_engine session_search clarify delegation cronjob homeassistant spotify yuanbao computer_use`, plus installed plugin toolset names. After enabling it, apply inserts and preserves `kanban` as the one supported non-configurable exception. STT follows its separate provider-specific setup and MUST NOT be represented as a model toolset.

`skills.inline_shell=false` remains a load-time provenance boundary, not a capability denial: authorized sessions retain full terminal/code execution and can run reviewed skill scripts explicitly. Hermes' pre-exec scanner remains enabled, but `approvals.mode=off` bypasses its prompt gate for non-hardline commands; immutable hardline and sudo-stdin guards still apply. The website blocklist remains disabled.

### 12. Use explicit action-class checkpoints during apply

The apply workflow is not one blanket authorization. It pauses separately before credential rotation, package/network execution, configuration mutation, backup generation, restart of the existing launchd service, reversible local writes, provider/private-network calls, and any shared-service mutation. Read-only inventory success does not authorize a later mutation, and technical tool exposure does not grant standing permission for an outward or destructive action.

## Risks / Trade-offs

- **[Prompt injection leads to host compromise]** Full local terminal/browser/MCP access plus approvals off can execute attacker-controlled actions. → Restrict Telegram users, retain injection scanning/redaction, inspect logs, keep backups, and use only trusted conversations/sources.
- **[Private-network access]** Private URL access can reach local services and authenticated administrative applications. → Accept explicitly for full access; do not expose the bot publicly. Cloud-metadata/link-local credential endpoints remain immutably blocked.
- **[Autonomous persistent mutation]** Memory and skills can change without review. → Preserve notifications/audit logs and verify profile-local state during maintenance.
- **[Supply-chain execution]** Lazy installs and MCP stdio packages execute third-party code. → Keep Hermes lazy-install allowlisting, pin MCP versions, and separately approve non-Hermes package installs.
- **[Destructive cron]** Headless jobs can auto-approve dangerous commands. → Require self-contained reviewed prompts, explicit workdirs, pinned providers/models, execution history, and backups.
- **[Shared-service mutation]** All MCP operations can alter or delete external state. → Service credentials/scopes and current user instructions remain the authorization boundary; do not interpret tool availability as standing permission.
- **[Parallel shared-state races]** Parallel MCP operations may conflict, duplicate outward effects, or observe intermediate state. → Accept explicitly for unrestricted calling; preserve per-call IDs/results and require current user authority for each outward mutation, but do not serialize calls by policy.
- **[Capability/tool-schema cost]** Exposing all tools increases system-prompt size and may reduce tool selection accuracy. → Accept as the full-access trade-off; preserve prompt caching and use fresh sessions only when schemas change.
- **[Unattended cost drift]** Community reports show recurring jobs and large fixed prompts can consume meaningful tokens overnight. → Retain the requested unlimited budget policy, but pin cron inference routing, fail closed on model drift, prefer `no_agent` watchdogs, record `prompt-size`/`insights` trends, and require a separate approved provider/proxy change for any future monetary cap.
- **[Autonomous skill growth and rot]** Community stories show skills reduce repeated work while accumulating stale trust surface. → Keep autonomous writes, audit shared-profile usage, and require curator dry-run plus backup verification before archive or consolidation; do not enable paid consolidation implicitly.
- **[Shared-profile blast radius]** CLI, Desktop, Telegram, memory, skills, cron, credentials, and MCP share one profile; bad configuration or autonomous state can affect every surface. → Accept for one trusted agent, retain source/chat-separated sessions, immutable security floors, backups, and an in-place rollback path.
- **[Gateway interruption]** Restarting the existing gateway briefly interrupts Telegram and cron ticking, but not independent local CLI/Desktop processes. → Validate `default` before restart and verify the same service after activation.
- **[Credential exposure]** A credential-like value was previously observed in non-secret configuration. → Rotate it separately, store replacement through Hermes secret routing, and never reproduce it in artifacts.
- **[Unverified custom context capacity]** `/v1/models` requires authorization and did not expose metadata to the read-only probe; Hermes falls back to 256,000 and then applies a 1,050,000-token catalog heuristic, while the provider has returned `context_too_large`. → Do not set `model.context_length` until the custom endpoint owner supplies or an authenticated non-destructive probe establishes the actual limit.

## Migration Plan

1. Capture a redacted baseline of version, schema, profiles, gateway, tools, MCP, approvals, private URL settings, memory/skill gates, permissions, storage, and warning counts.
2. Complete separately authorized rotation of any credential found outside the supported secret store.
3. Create and verify both the pre-activation quick snapshot and full off-root backup described above; record exact restore commands before mutation.
4. Verify the installed schema (v37) with the supported configuration checks, run migration only if the installed runtime later reports further schema drift, and correct the invalid timezone and unsupported `service_tier: auto` value.
5. Configure the default profile's full-access settings and explicitly enable every concrete platform-applicable CLI toolset and MCP operation; validate special GUI/dispatcher/context-engine surfaces only where supported.
6. Enable the same full-access tool policy for CLI and Telegram in `default`, preserving shared memory, skills, credentials, cron, MCP, and source/chat-separated sessions.
7. Discover unavailable capabilities and record their exact missing credential/binary/platform prerequisite. Stop before unapproved package installation or external credential provisioning.
8. Validate `default` with config, doctor, status, CLI/Telegram tool inventories, MCP, permissions, memory, skills, cron, browser, terminal, and delegation checks before touching the gateway.
9. With service-mutation approval, restart the existing `ai.hermes.gateway` service in place and verify the default profile home, sole token owner, supervised PID, platform health, and authorized Telegram round-trip.
10. Record prompt-size and Tool Search evidence, unchanged MCP Router fingerprint plus parallel declaration, cron routing, gateway progress, bounded restoration, and durable final delivery.
11. Run separately approved read-only, reversible-local-write, network/provider/private-URL, and shared-state smoke classes.
12. If validation fails, restore prior default-profile configuration/state as needed, restart the same gateway, and preserve failed-state evidence.

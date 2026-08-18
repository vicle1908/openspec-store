# Proposal: Integrate Grok Build CLI

## Why

The workspace already has three operational model gateways—`shopapikey`, `giaoduc`, and `cockpit`—but Grok Build is not installed or verified as an independent coding-agent CLI. Grok Build supports interactive, headless, and ACP execution plus custom model providers, so a controlled integration can add another optional developer-agent surface without changing application routing.

## What Changes

- Install the official stable Grok Build CLI from `https://x.ai/cli/install.sh`, after capturing and reviewing the installer plus pre-install user state. (Live state 2026-08-18: `1.0.3` is already installed; the pinned-version plan is reconciled against the live binary rather than running the installer anew.)
- Reconcile the live five-alias config (adds `cockpit-terra`) against the planned four env-referenced aliases: `shopapikey-fable-5`, `giaoduc-advance`, `cockpit-sol`, and `cockpit-luna`. Remediate the credential form per `tasks.md` §3.5.
- Verify official configuration conformance, exact request URL construction, authentication behavior, bounded headless inference, workspace instructions and skills, ACP, permissions, and mcp-router integration.
- Record sanitized evidence, explicit fail-closed gates, a touched-surface inventory, and a tested rollback procedure.

## Current-State Evidence

Collected 2026-08-09 before installation:

- `https://docs.x.ai/build/overview` identifies the product as Grok Build, the binary as `grok`, the config as `~/.grok/config.toml`, and the headless form as `grok -p`.
- `https://github.com/xai-org/grok-build` documents `[model_providers.<id>]`, `[model.<alias>]`, `model_provider`, `env_key`, and `api_backend` values `chat_completions`, `responses`, and `messages`.
- `https://x.ai/cli/stable` returned `1.0.0` at exploration time; `grok` was absent from PATH. No installer was executed during exploration or review. (2026-08-18 addendum: stable now resolves to `1.0.3`; grok `1.0.3` is installed and on PATH; `~/.grok/config.toml` is populated with literal keys, pending §3.5 remediation.)
- Authenticated `/v1/models` probes returned HTTP 200 and exposed the requested IDs: shopapikey `fable-5`, giaoduc `Advance`, cockpit `gpt-5.6-sol` and `gpt-5.6-luna`.
- Direct `/v1/responses` and `/v1/messages` probes returned HTTP 200. These results establish only pre-install protocol compatibility; they do not prove Grok config parsing, URL joining, request shape, authentication, sentinel output, or clean process exit.

## Scope

### In scope

- User-level Grok binary and `~/.grok/config.toml` used for development in `~/Developer`.
- The four exact Grok aliases and upstream model IDs listed above.
- Read-only provider catalog checks, native Grok inference checks, `AGENTS.md` and canonical Agent Skills discovery, ACP verification, and mcp-router-only MCP routing.
- Sanitized review and implementation evidence retained under this change.

### Out of scope

- Changes to `agent-core`, `~/.tdt/config.yaml`, Hermes provider configuration, gateway endpoints, or production application behavior.
- Direct registration of downstream MCP servers when mcp-router can provide the aggregate route.
- Making Grok mandatory in current review orchestration.
- Committing binaries, shell profiles, user configuration, credentials, raw authorization headers, or request bodies.

## Ownership Boundaries

- **OpenSpec store:** owns this plan and sanitized evidence.
- **User runtime:** `~/.grok/`, installer-created symlinks/completions, and installer-added shell blocks; mutated only during the approved apply phase.
- **Protected existing surfaces:** `~/.tdt/config.yaml`, `~/.hermes/config.yaml`, provider endpoints, and unrelated repository worktrees remain unchanged.

## Success Criteria

Completion is governed by `design.md` and `tasks.md`. No provider or capability is accepted until its named native Grok evidence exists. Unknown or unsupported capabilities remain explicitly classified rather than inferred from direct HTTP compatibility.

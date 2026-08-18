# Design: Grok Build CLI Integration

## Architecture and Boundaries

Grok Build SHALL remain an optional developer CLI. It SHALL consume the existing gateways only through its own user-level `~/.grok/config.toml`; no application request path, `agent-core` provider factory, Hermes provider configuration, or TDT provider contract is changed.

```text
Grok Build (`grok`)
  |-- shopapikey-fable-5 -> https://api.phanmemvip.shop/v1 -> Responses -> fable-5
  |-- giaoduc-advance    -> https://api.giaoduc.online    -> Messages  -> Advance
  |-- cockpit-sol        -> http://localhost:51006/v1     -> Responses -> gpt-5.6-sol
  `-- cockpit-luna       -> http://localhost:51006/v1     -> Responses -> gpt-5.6-luna
```

The left-hand values are Grok catalog aliases. The right-hand values are exact upstream model IDs observed through authenticated model-list probes.

## Official Configuration Contract

The official source and docs establish these surfaces:

- `~/.grok/config.toml`
- `[models]`, `[model_providers.<id>]`, and `[model.<alias>]`
- `model`, `name`, `base_url`, `env_key`, `api_backend`, `model_provider`, `context_window`
- `extra_headers`, `env_http_headers`, and `query_params`
- backends `chat_completions`, `responses`, and `messages`

The source demonstrates that provider defaults are inherited by models and that unresolved provider references fail closed without leaking Grok session credentials to custom endpoints.

## Proposed Configuration

```toml
[models]
default = "shopapikey-fable-5"

[model_providers.shopapikey]
base_url = "https://api.phanmemvip.shop/v1"
env_key = "HERMES_CUSTOM_SHOPAPIKEY_API_KEY"
api_backend = "messages"
context_window = 1000000

[model.shopapikey-fable-5]
model = "fable-5"
name = "fable-5 (shopapikey)"
model_provider = "shopapikey"

[model_providers.giaoduc]
base_url = "https://api.giaoduc.online/v1"
env_key = "HERMES_CUSTOM_GIAODUC_API_KEY"
api_backend = "messages"
context_window = 1000000

[model.giaoduc-advance]
model = "Advance"
name = "Advance (giaoduc)"
model_provider = "giaoduc"

[model_providers.cockpit]
base_url = "http://localhost:51006/v1"
env_key = "HERMES_CUSTOM_COCKPIT_API_KEY"
api_backend = "responses"
context_window = 1000000

[model.cockpit-sol]
model = "gpt-5.6-sol"
name = "gpt-5.6-sol (cockpit)"
model_provider = "cockpit"

[model.cockpit-luna]
model = "gpt-5.6-luna"
name = "gpt-5.6-luna (cockpit)"
model_provider = "cockpit"
```

This is a proposed baseline. Reasoning, tool-streaming, backend-search, and model-specific capability flags remain unset until native Grok evidence proves them.

**2026-08-18 live-state reconciliation note:** the live `~/.grok/config.toml` differs from this baseline in several ways, each resolved by a `tasks.md` decision or edit: installed version `1.0.3` (not `1.0.0`); `default = "cockpit-terra"` (not `shopapikey-fable-5`); a fifth alias `cockpit-terra` → `gpt-5.6-terra`; shopapikey `api_backend = "messages"` (not the originally proposed `responses`); `base_url` includes `/v1` on all three providers; extra `anthropic-version` headers; literal `api_key` values instead of `env_key` (see §3.5); and unplanned `[cli]`/`[models]`/`[marketplace]`/`[ui]` sections including `yolo = true`.

## URL Construction Gate

The direct probes succeeded at `/v1/responses` and `/v1/messages`, but native Grok URL joining has not been observed. Before provider inference, implementation MUST use official source inspection plus a redacted request observer to establish the exact final URL for each alias. Acceptance rejects missing `/v1`, duplicated `/v1/v1`, malformed trailing slashes, and unexpected paths. Base URLs SHALL be adjusted only from that evidence.

## Authentication and Secrets

- Credentials are intended to remain referenced by environment-variable name; literal values SHALL NOT be written to config, commands, logs, process arguments, or evidence. Live config currently violates this (literal `api_key` + `MCPR_TOKEN`); grok supports `env_key` and `${VAR}` expansion, so the remediation decision in `tasks.md` §3.5 MUST resolve this before archive.
- Preflight records only presence/absence for all three variables.
- The Giaoduc gateway accepted both Bearer and `x-api-key` in direct probes, but Grok's `messages` behavior is unresolved. Native verification records only header name/scheme and redacted presence.
- If `env_http_headers` is required, it SHALL reference the existing variable name and SHALL be added only after proving that `env_key` is insufficient.
- Evidence SHALL be scanned for secret-shaped values before commit.

## Installation and Integrity

The official installer supports a positional version and installs under `~/.grok/`. The apply phase SHALL:

1. Fetch and retain a reviewed copy of `https://x.ai/cli/install.sh`.
2. Confirm `https://x.ai/cli/stable` still resolves to `1.0.3` or stop for plan amendment.
3. Reconcile against the already-installed `1.0.3`, not an unpinned moving channel.
4. Record artifact URL, platform/architecture, installed binary path, executable hash, and `grok --version`.
5. If xAI publishes a checksum/signature, verify it. If none is published, record that limitation and rely on TLS, installer review, explicit version, and post-download executable/hash evidence; do not fabricate a checksum.

## Verification Classes

1. **Official-source conformance:** docs/source URLs and exact config fields.
2. **Direct compatibility:** current gateway catalogs and HTTP protocol probes.
3. **Native Grok acceptance:** config parsing, alias selection, final URL/auth shape, exact sentinel, usage metadata, and clean native exit.

A lower class never satisfies a higher-class task.

## Workspace, MCP, and ACP

- Run `grok inspect` from a disposable clone/worktree under `~/Developer`, where workspace `AGENTS.md`, repository instructions, and canonical `~/.agents/skills` discovery can be observed without source edits.
- Confirm CLI/subcommand availability from installed `grok --help` before invoking any planned command. Unsupported capabilities are marked `UNSUPPORTED` and removed or deferred rather than guessed.
- MCP routes through one existing mcp-router bridge. Do not register downstream servers directly. The read-only canary SHALL list tools or invoke a harmless metadata query without persistence or external mutation.
- ACP verification is bounded and read-only. Its exact invocation is taken from installed help/source, not assumed from another agent.

## Permissions, Isolation, and Concurrency

- Installation and config writes are serialized and require explicit apply authorization.
- Provider inference probes run serially with one turn, small output limit where supported, a 60-second external timeout, and no tools.
- Mutating agent probes run only in a disposable git worktree with synthetic content, then verify no outside-root changes and remove the worktree.
- Review agents run in batches of at most three. Grok is not added to mandatory review orchestration in this change.

## Rollback Transaction

Before mutation, capture existence, mode, hash, and backup path for `~/.grok/config.toml`, shell startup files, installer blocks, and any pre-existing `~/.grok/` state. After acceptance testing:

1. Stop only Grok processes started by this change.
2. Restore the exact pre-change config backup, or remove only the added provider/model blocks when a full restore is inappropriate.
3. Remove installer-created symlinks/binary/completion files only after verifying their targets and ownership.
4. Remove only the installer-delimited shell block, preserving unrelated lines.
5. Verify pre-change hashes/modes where applicable, PATH resolution, absence of added aliases, and byte-for-byte stability of protected surfaces.
6. Reapply the intended integration from the retained manifest if the rollout is to remain installed; otherwise leave the verified pre-change state.

Rollback SHALL be rehearsed first in an isolated temporary HOME. Real-user rollback evidence is required before completion if user-level installation is retained.

## Acceptance Matrix

| Gate | Pass condition |
|---|---|
| Identity | Product, executable, config, URLs, aliases, and model IDs match official/current evidence |
| Config | Native parser reports aliases and no unknown/invalid entry warnings |
| Providers | Four exact sentinels, correct upstream model IDs, expected URL/auth metadata, clean exits |
| Secrets | No literal credential in tracked files, output, process arguments, or retained evidence |
| Workspace | Intended AGENTS.md and shared skills discovered; no duplicate maintained skill tree |
| MCP/ACP | Exact installed interfaces verified or honestly classified unsupported |
| Isolation | Disposable agent test produces no outside-root mutation |
| Rollback | Touched-surface manifest and restore rehearsal pass |
| OpenSpec | Focused and full validation, diff check, review finding disposition, clean intended status |

## Open Questions

- Exact stable-1.0.3 URL-joining behavior for each backend.
- Exact Giaoduc authentication emitted by the Grok `messages` backend.
- Whether all planned MCP/ACP/worktree controls exist in stable 1.0.3 under the assumed names.
- Credential-form remediation decision (§3.5): env_key/`${VAR}` migration vs. accepted literal keys.
- Fate of the live fifth alias `cockpit-terra` and the `[ui] yolo=true` section.
- Whether xAI publishes a checksum/signature for the pinned artifact.

These remain gates, not completion claims.

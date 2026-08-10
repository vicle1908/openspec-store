# harden-goose-runtime-configuration

## Why

Goose v1.45.0 is installed at `/opt/homebrew/bin/goose` and is functional but over-broad and drift-prone. Evidence gathered on 2026-08-09 proves:

- **nhà cung cấp dịch vụ AI** (`fable-5`) and **Shopapikey** (`fable-5`) providers are healthy (verified with isolated `--no-profile` probes).
- **Giaoduc** (`Advance`) provider is healthy.
- **Omniroute** (`dlg/fable-5`) is configured but probe status varies.
- **MCP Router** works at the protocol boundary from Goose, but Goose startup has failed intermittently.
- The default profile enables 17 extensions and uses a mutable MCP package selector (`@mcp_router/cli@latest`).
- Goose returns **exit code 0** for runtime/provider/tool failures — automation MUST inspect `metadata.status` and validate output content, never trust exit code alone.
- `goose doctor` is **model-backed** (launches a session, consumes tokens/time) and is NOT safe for cron health checks.
- Shopapikey provider outputs `thinking` before `text` in assistant content — automation must select content entries where `type == "text"`.

A follow-up hardening change is needed to make the configuration least-privilege, reproducible, cost-aware, and accurately documented.

## Ownership

This change owns Goose binary configuration, provider health matrix, and offline documentation. It does NOT own Graphify, GitNexus, agentmemory, or MCP Router internals. References `docs/cli-agent-tooling-contract.md` for shared conventions.

## What Changes

1. Establish a durable provider health matrix and remove stale all-provider-healthy claims.
2. Classify MCP Router as healthy transport with intermittent Goose initialization; pin the reviewed CLI version only after compatibility testing.
3. Define and verify least-privilege invocation profiles for chat/docs, coding, and MCP-dependent work.
4. Harden offline-doc updates with explicit tag fetch, `npm ci`, staging validation, deletion-aware deployment, and rollback.
5. Tighten config and deployment permissions after checking app compatibility.
6. Add deterministic runtime probes that validate expected output and artifacts, not only exit code or `metadata.status`.
7. Reconcile Goose skills and verification references with retained evidence.

## Automation Requirements

Any tooling that invokes Goose noninteractively MUST:

- Use `-q` for machine-readable output (suppresses banner prefix that breaks `json.loads()`).
- Validate `metadata.status == "completed"` AND content `type == "text"` (not `thinking`).
- Never use `goose doctor` in automated checks (model-backed, expensive).
- Pin mutable MCP package references (`@mcp_router/cli@latest`) only after compatibility testing.
- Acquire workspace-wide lock if modifying shared config files.
- Redact all tokens/credentials in committed evidence.
- Set bounded timeouts (60s per probe, 300s per session).

## Non-Goals

- No provider credential changes in the planning phase.
- No live extension enable/disable mutation before approval.
- No network listener exposure changes.
- No rewriting historical archive evidence; this change supersedes stale claims transparently.

## Compatibility and Rollback

All future mutations SHALL be separately gated. Preserve a timestamped redacted config backup and the prior `/opt/goose-docs` tree before any cutover. Rollback restores the prior config and docs directory, then reruns provider, MCP, and offline-doc probes.

## Evidence

Before execution:
- Binary: `/opt/homebrew/bin/goose` v1.45.0
- Config mode: 0644
- Active provider: nhà cung cấp dịch vụ AI
- Extensions: 17 enabled
- Context limit: 1,000,000
- MCP package: `@mcp_router/cli@latest` (mutable)
- Goose doctor: model-backed, not safe for automation

After execution:
- Provider health matrix documented and accurate
- MCP package version pinned
- Config mode tightened (after compatibility verification)
- Offline docs built from explicit tag with `npm ci`
- All probes use content validation, not exit code

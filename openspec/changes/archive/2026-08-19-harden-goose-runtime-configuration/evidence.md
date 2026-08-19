# Goose Runtime Configuration Audit Evidence

Date: 2026-08-09

## Baseline

- Binary: `/opt/homebrew/bin/goose`
- Version: `1.45.0`
- Config: valid YAML, mode `0644`
- Active provider: `openai`
- Context limit: 1,000,000
- Planner context limit: 1,000,000
- Thinking effort: `max`
- Telemetry: disabled
- Extensions: 17 enabled
- Gateways: none configured
- Scheduled jobs: none configured
- Desktop ACP server: loopback TLS listener

## Provider Probes

| Provider | Model | Result | Usage | Notes |
|---|---|---|---|---|
| openai | gpt-5.6-luna | PASS | 7,778 tokens; ~$0.0078 | Exact sentinel; isolated no-profile probe |
| custom_shopapikey | fable-5 | PASS | 4,921 tokens | Exact sentinel; isolated no-profile probe |
| custom_giaoduc | Advance | PASS in this probe | 4,647 tokens | Exact sentinel; isolated no-profile probe |
| custom_omniroute | dlg/deepseek-v4-pro | FAIL | 0 tokens | 404: no active `dlg` credentials; exit 0 and status `completed` |

## Offline Docs

- Config root: `/opt/goose-docs`
- Source checkout: exact tag `v1.45.0`, commit `4dc0420f5704a92806c6628c8f0a3497d7a88759`, clean, shallow tag-only refspec
- Runtime trace: goose resolved `/opt/goose-docs`, read `/opt/goose-docs/goose-docs-map.md`, then read `/opt/goose-docs/docs/guides/offline-docs.md`
- Page heading: `# Offline / Air-gapped Docs`
- Returned quote matches local Markdown after whitespace normalization
- Map validation: 60 unique mapped links; 60 exist
- Deployment: 1,481 files; source build has one additional `.nojekyll`
- Docs map SHA-256 matches source build

## MCP Router

- Login-shell token presence: true (value not printed)
- Direct stdio initialize: PASS
- Server: MCP Router v0.2.0
- Protocol: 2025-11-25
- `tools/list`: 132 tools
- Real goose read-only MCP call: PASS (`list_directory`)
- Separate goose starts have also reported process exit before initialization
- Classification: healthy transport and successful call path; intermittent/degraded goose initialization
- Config risk: mutable `@mcp_router/cli@latest`; current latest 0.2.0

## Least-Privilege Probe

Invocation used `--no-profile --with-builtin developer`. Goose created and verified `/tmp/goose-least-privilege/marker`; external read confirmed `LEAST_PRIVILEGE_OK`.

## Cost Observations

| Probe | Observed usage |
|---|---|
| Isolated provider sentinels | 4.6K–7.8K tokens; ~36–54 seconds |
| Developer-only write/read | 26K tokens; ~$0.0204 |
| Full-profile MCP call | 37K tokens; ~$0.0395 |
| Full-profile offline-doc proof | 193K tokens; ~$0.157 |

## Operational State

- Request logs: 367 files, ~3MB
- Long-lived desktop goose serve process: loopback TLS, scheduler enabled
- No configured goose gateways
- No scheduled jobs
- Multiple long-lived MCP Router bridge processes exist; parentage/resource pressure requires follow-up

## Integrity Rule

A successful goose task requires the expected exit behavior, structured status, exact response or artifact, absence of error text, appropriate nonzero usage, and external artifact verification. Exit code or `metadata.status` alone is insufficient.

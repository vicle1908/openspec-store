# Evidence Manifest: harden-grok-cli-mcp-credentials

Date: 2026-08-29 · Applied and verified in one session. All evidence sanitized — no credential values retained anywhere in this file.

## 1. Preparation (tasks 1.1–1.3)

### 1.1 zshenv export

- `export GROK_MCPR_TOKEN` added inside the `~/.zshenv` shared-agent-secrets block (immediately before `# END shared-agent-secrets`)
- Presence: SET (length 37, value withheld); shell init verified clean; file mode preserved at 600
- zshenv pre-edit backup: `~/.zshenv.bak-harden-grok-cli-mcp-credentials.20260829T094036` (sha256 `50cb13c455eb0c6becfea7c439e3eed32c8298b5c54206e46f405ecd0a40a620`, mode 600)
- **Incident and resolution during insert**: the first insertion script wrote an invalid hyphenated variable name, which zsh rejected (`export: not valid in this context`) on shell startup; it was replaced in place with the valid `GROK_MCPR_TOKEN` name within the same session and shell-init cleanliness was re-verified. No other lines were touched; the value never appeared in any command output.

### 1.2 Wrapper

- `~/.grok/mcp-router-launch.sh` — mode 700, contains no credential values (sources `~/.zshenv`, maps `GROK_MCPR_TOKEN` onto `MCPR_TOKEN`, execs `npx -y @mcp_router/cli connect`)
- Smoke test (stdin closed, 8s window): clean exit, no auth error; `npm notice run 'mcpr' connect` observed
- Shellcheck advisory on the wrapper is historical/benign (non-constant `source`); no action required

### 1.3 Config backup

- `~/.grok/config.toml.bak-harden-grok-cli-mcp-credentials.20260829T094623` — mode 600, sha256 `d60fdaf97e7117ad0be9bcb84a608fe642a9a9f72a0401447b54b56e0de9397c` (byte-identical to the `correct-grok-cli-provider-routing` corrected-state baseline; `cmp` identical)

## 2. Mutation and verification (tasks 2.1–2.4)

### 2.1 Config mutation

- `[mcp_servers.mcp-router]` repointed: `command = "npx"` + args array → `command = "/Users/androidteam/.grok/mcp-router-launch.sh"`; `[mcp_servers.mcp-router.env]` sub-table with the literal `MCPR_TOKEN` removed; timeouts and enabled flag preserved
- Config parses; `grok models` output unchanged (8 models, default `cockpit-sol`)
- New config sha256 baseline: `8626abe9ec687fcf4261d117814b1b88d25925f52246a2d73d0791f080dfa4b6`
- First mutation attempt was safely rejected by its own pre-write assertions (regex captured only the main table, not the env sub-table) — no partial state was written; the corrected pattern spanned both tables
- Structural proof: redacted diff (backup → current) shows ONLY the mcp_servers block changed; provider/model routing sections byte-identical

### 2.2 Regression gate

- Provider-routing contract assertions re-run on the mutated config: **18/18 PASS**

### 2.3 MCP round trip

- Fresh `grok -p` session (default model) → wrapper spawn → zshenv source → MCPR_TOKEN mapping → `npx @mcp_router/cli connect` → tool call: **PASS, exit 0** — "MCPOK — mcp-router reported an active mcp-router client (version 1.0.0) running on macOS with zsh, server version 0.2.47, and telemetry enabled."

### 2.4 Credential scan

- Token value ABSENT from `~/.grok/config.toml` — PASS
- Token value ABSENT from both change artifact directories and the main specs — PASS
- Pattern scan (`mcpr_` value prefixes) over both change dirs — clean
- Expected presence: zshenv SET (mode 600, by design); wrapper contains only the variable reference; pre-mutation backups retain the literal as the rollback path (outside git, mode 600)

## 3. End-to-end sweep (post-mutation; every session exercised wrapper-based MCP startup)

| Check | Result |
| --- | --- |
| shopapikey-claude-fable sentinel | PASS, exit 0, 17s, exact match |
| phanmemvip-sol sentinel | PASS, exit 0, 15s, exact match |
| cockpit-sol sentinel | PASS, exit 0, 17s, exact match |
| cockpit-luna sentinel | PASS, exit 0, 19s, exact match |
| cockpit-terra sentinel | PASS, exit 0, 18s, exact match |
| omniroute-sol sentinel | PASS, exit 0, 18s, exact match |
| omniroute-claude-fable sentinel | PASS, exit 0, 19s, exact match |
| Default-model tool call (`echo TOOLCALL_OK`) | PASS, exit 0, 23s, exact marker |
| MCP round trip (§2.3) | PASS |

7/7 sentinels + tool call + MCP round trip: zero serialization, auth, reconnect, or MCP startup errors across all four providers.

## 4. Delivery

- Strict OpenSpec validation: passed (task 3.1)
- Committed to the store after operator-approved apply (task 3.2); see git log for the exact commit
- Cross-reference: the `correct-grok-cli-provider-routing` evidence §3 wording updated to name this change and the wrapper mechanism (separate commit on that change)

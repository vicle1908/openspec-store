# Proposal: add-claude-code-omniroute-pm-launcher

## Why

Claude Code currently has two provider launchers (shopapikey direct,
cockpit via the local adapter). OmniRoute — the workspace AI gateway on
127.0.0.1:20129 — exposes a native Claude-Fable Messages endpoint
(`/v1/messages`) with a phanmemvip channel (`pm/Claude-Fable`,
`pm/Claude-Sonnet`, `pm/Claude-Fable`, `pm/default`). Verified live:

- `POST /v1/messages?beta=true` accepts the full Claude Code payload
  (`output_config`, `thinking`, `tools`, `context_management`, `system`,
  `metadata`) and returns a native `message` object.
- `POST /v1/messages/count_tokens` works (`{"input_tokens":N,"source":"local"}`).
- Claude Code 2.1.251 end-to-end through OmniRoute returns PONG with exit 0;
  the `[1m]` suffix is stripped before the wire model is sent.
- Loopback `/v1/*` is keyless today (`REQUIRE_API_KEY=false`), so the
  launcher needs no credential at runtime — but the helper keeps the
  credential-free profile contract and starts working automatically if
  keying is re-enabled.

## What Changes

Config/tooling-only additions following the established three-provider
pattern (`claude-code-provider-routing` + `claude-code-provider-profile-resolution`):

1. `~/.claude/helpers/omniroute-key.sh` — env-first helper for
   `OMNIROUTE_API_KEY` with restricted single-key parse fallback (never
   sources `.zshenv`).
2. `~/.claude/profiles/omniroute-pm.json` — credential-free profile,
   mode 600: `ANTHROPIC_BASE_URL=http://127.0.0.1:20129`, model
   `pm/Claude-Fable[1m]`, `modelOverrides` self-mapping for the gateway
   alias, `apiKeyHelper` pointing at the new helper.
3. `omniroute()` launcher in `~/.zshrc` — guards, unsets
   `ANTHROPIC_AUTH_TOKEN`, sets the base URL, and launches
   `claude --settings ~/.claude/profiles/omniroute-pm.json`.

No application source changes; no other launchers touched.

## Impact

- New capability spec: `claude-code-omniroute-pm-routing`
- Existing specs unaffected (profile-resolution and provider-routing
  surfaces unchanged; the new launcher follows their contracts).

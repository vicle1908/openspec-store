# Tasks: correct-grok-cli-provider-routing

All verification calls are real but bounded: one sentinel turn and one disposable tool-call turn per model, spaced to respect the observed phanmemvip.shop rate limit. Never record credential values, authorization headers, request bodies, or raw responses in evidence.

## 1. Backup and baseline

- [x] 1.1 Copy `~/.grok/config.toml` to a mode-600 backup in the `~/.grok` backup lineage (kept outside the git-tracked store because the config embeds a pre-existing MCP server token), record its sha256 in the change's evidence, and verify the backup restores byte-identically (`cmp` succeeds)
- [x] 1.2 Record sanitized baseline: `grok --version`, `grok models` output (seven custom models + default), and a redacted provider table (backends, base URLs, `env_key` names only)

## 2. Configuration contract validation

- [x] 2.1 Verify all four providers in `~/.grok/config.toml` declare `api_backend = "chat_completions"`, and OmniRoute alone uses `base_url = "http://localhost:20128/v1"` with `env_key = "OMNIROUTE_API_KEY"`; verify providers, model entries, and the default model are otherwise unchanged
- [x] 2.2 Run a credential-value scan over `config.toml` and every artifact in this change; verify no literal API key or token values are present (names of env vars are allowed)
- [x] 2.3 Fetch a fresh `GET http://localhost:20128/v1/models` with the environment-backed key and verify the registered `sh/*` IDs (`sh/Claude-Fable`, `sh/Claude-Fable`) exist and their catalog context lengths match the per-model `context_window` values (1050000, 200000)

## 3. Verification matrix (real calls)

- [x] 3.1 Run a one-turn sentinel call per model for all seven models (`shopapikey-claude-fable`, `phanmemvip-sol`, `cockpit-sol`, `cockpit-luna`, `cockpit-terra`, `omniroute-sol`, `omniroute-claude-fable`); each SHALL exit 0 with the exact sentinel string and no serialization, auth, or reconnect error, with rate-limit spacing between calls
- [x] 3.2 Run one disposable tool-call probe per provider (bash `echo` marker through at least one model of each of `shopapikey`, `phanmemvip`, `cockpit`, `omniroute`); each SHALL return the exact marker with no outside-root mutation
- [x] 3.3 Classify any failing probe as serialization, auth, rate-limit, or service-unavailable — recording only the category, model ID, and endpoint; a persistent 429 is an environment gate, not a routing failure

## 4. Evidence and constraints

- [x] 4.1 Write a sanitized evidence manifest in the change directory covering every probe: status, exit code, model ID, backend, duration, and outcome; no headers, bodies, or key material
- [x] 4.2 Record the known-broken protocol combinations as routing constraints in the evidence manifest: Messages on phanmemvip.shop (missing `signature`), Responses on phanmemvip.shop and OmniRoute (missing `model` in streaming events; malformed heartbeat), and non-streaming chat completions on OmniRoute `sh/*` (`upstream_empty_response`)

## 5. Validation and delivery

- [x] 5.1 Run `openspec validate correct-grok-cli-provider-routing --strict --store openspec-store` and confirm it passes
- [x] 5.2 Run `git diff --check` in the store and stage only this change's artifacts; confirm the scoped diff contains no credential values and no unrelated files
- [x] 5.3 Commit the OpenSpec store change with a message referencing `correct-grok-cli-provider-routing`

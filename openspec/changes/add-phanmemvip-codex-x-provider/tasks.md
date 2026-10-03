# Tasks

## 1. Codex provider inventory

- [ ] 1.1 Back up `~/.codex/config.toml` (to `~/.codex/config.toml.bak-pre-phanmemvip-codex-x`) and add a `[model_providers.phanmemvip]` block with `name = "Phanmemvip"`, `base_url = "https://api.phanmemvip.shop/v1"`, `wire_api = "responses"`, `requires_openai_auth = true`, and `env_key = "HERMES_CUSTOM_PHANMEMVIP_API_KEY"`; verify the file still parses (TOML) and that `codex_local_access` and `omniroute` blocks are unchanged.

## 2. Swapable phanmemvip profile

- [ ] 2.1 Create `~/.codex/phanmemvip.config.toml` with `model = "codex-x"`, `model_provider = "phanmemvip"`, `model_reasoning_effort = "xhigh"`, `model_reasoning_summary = "detailed"`, and the matching `[model_providers.phanmemvip]` block; verify it mirrors the shape of `omniroute.config.toml` and contains no literal secret. Follow the `omniroute.config.toml` pattern of leaving the main `config.toml` inventory intact and applying the profile by copying it over `config.toml`.
- [ ] 2.2 Verify the swap is reversible: apply the profile, then restore the backup, and confirm `~/.codex/config.toml` regains its original provider inventory and defaults with no block lost.

## 3. Claude Code home defaults

- [ ] 3.1 In the home `~/.claude/settings.json` (NOT the project-level file), change the top-level `model` and the `env` model values (`ANTHROPIC_MODEL`, `ANTHROPIC_DEFAULT_FABLE_MODEL`, and the other `ANTHROPIC_DEFAULT_*_MODEL` aliases) from `Claude-Fable[1m]` to `codex-x`; keep `ANTHROPIC_BASE_URL=https://api.phanmemvip.shop`, `CLAUDE_CODE_EFFORT_LEVEL=xhigh`, and the `apiKeyHelper` unchanged. Verify the file remains valid JSON, contains no `[1m]` suffix, and contains no `ANTHROPIC_AUTH_TOKEN`/secret in its `env` block.

## 4. Integration verification

- [ ] 4.1 With the phanmemvip profile applied, run a real Codex turn and verify it completes on `model_provider = "phanmemvip"` / `model = "codex-x"` (not falling back to another provider). If the Responses wire is rejected, fall back to `wire_api = "chat"` and record the outcome.
- [ ] 4.2 Verify `codex-x` resolves from the gateway by confirming `GET https://api.phanmemvip.shop/v1/models` (with `HERMES_CUSTOM_PHANMEMVIP_API_KEY`) lists `codex-x`, and only if a real Codex session fails to list it, add a `codex-x` entry to `~/.codex/cockpit-model-catalog.json` as the fallback.
- [ ] 4.3 Verify a bare `claude` session (home defaults) reports the model as `codex-x` on `https://api.phanmemvip.shop`; confirm the selected model carries no `[1m]` suffix and no secret appears in any modified JSON.

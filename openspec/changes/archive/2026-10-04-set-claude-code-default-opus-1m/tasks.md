# Tasks

## 1. Claude Code home default

- [x] 1.1 Back up the home `~/.claude/settings.json` (to `settings.json.bak-pre-opus-1m`) and set the top-level `model` plus every `ANTHROPIC_*_MODEL` alias (`ANTHROPIC_MODEL`, `ANTHROPIC_DEFAULT_FABLE_MODEL`, `ANTHROPIC_DEFAULT_OPUS_MODEL`, `ANTHROPIC_DEFAULT_SONNET_MODEL`, `ANTHROPIC_DEFAULT_HAIKU_MODEL`, `CLAUDE_CODE_SUBAGENT_MODEL`) to `Claude-Fable[1m]` in a single edit; keep `ANTHROPIC_BASE_URL=https://api.phanmemvip.shop`, `CLAUDE_CODE_EFFORT_LEVEL=xhigh`, and `apiKeyHelper` unchanged. Verify the file is valid JSON, every model field reads `Claude-Fable[1m]`, and no half-edited `codex-x`/`opus` model value remains.
- [x] 1.2 Verify the `env` block contains no `ANTHROPIC_AUTH_TOKEN`, `API_KEY`, `TOKEN`, or `SECRET`, and that the default selector carries the `[1m]` suffix.

## 2. Codex surface stays unchanged

- [x] 2.1 Verify `~/.codex/phanmemvip.config.toml` still sets `model = "codex-x"` with `model_provider = "phanmemvip"`, and `~/.codex/config.toml` still carries the additive `[model_providers.phanmemvip]` block; confirm no `[1m]` suffix appears anywhere in the Codex config. (This change must not alter the Codex surface.)

## 3. Integration verification

- [x] 3.1 Launch a bare `claude` session (home defaults) and confirm it reports the model as `Claude-Fable[1m]` on `https://api.phanmemvip.shop`, and that a request completes (Claude Code strips `[1m]` before transmit). If the provider rejects it, fall back to `Claude-Fable` or `opus` and record the outcome.
- [x] 3.2 Confirm the Claude Code launcher set (`shopapikey`, `cockpit`, `omniroute`) and their profiles are unchanged, and that the Codex `codex-x` selection still works.

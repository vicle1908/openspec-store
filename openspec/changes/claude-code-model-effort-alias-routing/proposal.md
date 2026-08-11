# Proposal: claude-code-model-effort-alias-routing

## Why

The completed `claude-code-three-provider-routing` change established three Claude Code launchers, but its launcher contract predates the current Claude Code model and effort configuration. The live `~/.zshrc` still uses literal model IDs for every launcher and does not set `CLAUDE_CODE_EFFORT_LEVEL` or model capability metadata. Claude Code's current model configuration distinguishes the built-in `fable` alias from provider-specific model IDs, and sends effort as `output_config.effort` in Anthropic Messages requests.

The cockpit adapter currently drops `output_config` while translating Messages to OpenAI Responses. Consequently, a cockpit request can return text successfully while silently losing the requested effort level.

Additionally, the launchers should use the `[1m]` suffix to request the 1 million token context window on supported models.

## Ground Truth Collected Before Authoring

All evidence below was collected from the live workstation before this proposal was written. Credential values were not printed or stored.

| Gate | Result | Evidence |
|---|---|---|
| Claude Code version | PASS | `claude --version` -> `2.1.227` |
| Official effort field | PASS | Local capture of Claude Code request: `output_config: {"effort":"xhigh"}` or `{"effort":"max"}`; beta includes `effort-2025-11-24` |
| Official `fable` alias | PASS | Local capture with `ANTHROPIC_MODEL=fable` and `ANTHROPIC_DEFAULT_FABLE_MODEL=fable-5` sent `model: fable-5` |
| `[1m]` suffix normalization | PASS | Local capture with `ANTHROPIC_MODEL=fable[1m]` and `ANTHROPIC_DEFAULT_FABLE_MODEL=fable-5[1m]` sent wire `model: fable-5` (suffix stripped) |
| `[1m]` suffix for custom models | PASS | Local capture with `ANTHROPIC_MODEL=Advance[1m]` and `ANTHROPIC_MODEL=gpt-5.6-luna[1m]` sent wire `model: Advance` and `model: gpt-5.6-luna` respectively (suffix stripped) |
| Custom `Advance` model | PASS (local shape) | Local capture sent `model: Advance` and `output_config.effort=xhigh` |
| Custom `gpt-5.6-luna` model | PASS (local shape) | Local capture sent `model: gpt-5.6-luna` and `output_config.effort=max` |
| shopapikey live smoke | PASS | Real `claude --print --output-format json` returned `SHOP_XHIGH_GROUND_TRUTH`; `modelUsage` contained `fable-5` |
| giaoduc live smoke | BLOCKED | Real request resolved to `Advance` but provider returned HTTP 429: account burst lock, reported remaining lock time 52 minutes |
| cockpit direct Responses | PASS | Real `POST /v1/responses` with `model=gpt-5.6-luna` and `reasoning.effort=max` returned HTTP 200, `status=completed`, exact sentinel |
| cockpit adapter transport | PASS | Real `claude --print` through healthy container returned `COCKPIT_CLAUDE_ADAPTER_GROUND_TRUTH` |
| cockpit effort propagation | FAIL | `_build_responses_body()` probe showed `output_config` and `reasoning` are absent from the translated body; current adapter silently drops effort |
| Adapter runtime | PASS | `127.0.0.1:8787` is served by the healthy `claude-code-provider-adapter` container; cockpit listens on `127.0.0.1:51006` |
| Existing settings isolation | PASS | `~/.claude/settings.json` has no provider-specific `ANTHROPIC_*` or effort variables |

At authoring time, the giaoduc 429 was an external provider-account gate. It was not evidence that the desired request shape was accepted, so the change was required to remain unarchived until a post-lock HTTP 200 smoke was captured. That post-lock smoke is now recorded in the Phase 3 evidence.

## What Changes

1. Update the three shell launchers in `~/.zshrc`:
   - `shopapikey()` uses the official `fable[1m]` alias pinned to `fable-5[1m]` and sets `xhigh` effort.
   - `giaoduc()` uses the custom `Advance[1m]` model option and sets `xhigh` effort.
   - `cockpit()` uses the custom `gpt-5.6-luna[1m]` model option and sets `max` effort.
2. Update `claude_reset()` to unset all variables owned by the provider launchers.
3. Update the cockpit adapter to map Anthropic `output_config.effort` to OpenAI Responses `reasoning.effort` without forwarding unrelated Anthropic-only fields.
4. Add regression tests for the mapping and launcher request-shape evidence.
5. Re-run live acceptance for all three providers and record fresh success evidence for each.

## Explicit Alias Contract

| Profile | Claude Code selector | Pinned/custom value | Wire model (provider sees) | Effort |
|---|---|---|---|---|
| shopapikey | `ANTHROPIC_MODEL=fable[1m]` | `ANTHROPIC_DEFAULT_FABLE_MODEL=fable-5[1m]` | `fable-5` | `xhigh` |
| giaoduc | `ANTHROPIC_MODEL=Advance[1m]` plus `ANTHROPIC_CUSTOM_MODEL_OPTION=Advance[1m]` | `Advance[1m]` | `Advance` | `xhigh` |
| cockpit | `ANTHROPIC_MODEL=gpt-5.6-luna[1m]` plus `ANTHROPIC_CUSTOM_MODEL_OPTION=gpt-5.6-luna[1m]` | `gpt-5.6-luna[1m]` | `gpt-5.6-luna` | `max` |

The `[1m]` suffix (lowercase) is a Claude Code context-window selection hint. Claude Code strips it before transmitting the model ID to the provider. The wire model IDs are the bare base names without the suffix.

`Advance` and `gpt-5.6-luna` are custom model IDs, not built-in Claude aliases. `fable` is the built-in family alias; `ANTHROPIC_DEFAULT_FABLE_MODEL` is the correct pinning variable.

## Security and Rollback

- Launchers reference existing environment variables only; no credential values are added to source, OpenSpec, logs, or tests.
- The adapter MUST NOT log request or response bodies.
- `claude_reset()` remains a subshell launcher and restores the default process environment by unsetting provider-owned variables.
- Rollback is removal of the new launcher variables and adapter mapping, followed by restoring the existing settings backup if needed. The separate container lifecycle remains managed by `cockpit_up` and `cockpit_down`.

## Post-Implementation Status

Implementation is complete and verified for the launcher contract, adapter mapping, all three live providers, streaming/non-streaming paths, and deterministic validation. Independent semantic review returned `APPROVE_WITH_BLOCKER` with no functional defect; its remaining recommendation is a durable CI/deployment guard for launcher and routing contracts.

## Readiness

The implementation is operational, and all three live provider acceptance gates, deterministic validation, and independent semantic review are green for runtime behavior. The review verdict is `APPROVE_WITH_BLOCKER`: no functional defect was found, but it recommends durable CI/deployment guards for the launcher contracts and direct-versus-adapter routing. Commit and archive remain separate pending gates; OpenSpec tasks 4.5 and 4.6 are intentionally unchecked until that release-governance disposition and operator approval are complete.

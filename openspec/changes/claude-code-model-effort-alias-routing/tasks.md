# Tasks: claude-code-model-effort-alias-routing

## Phase 0: Ground Truth (complete before mutation)

- [x] 0.1 Verify Claude Code version and official settings/model-config references.
  - Evidence: `claude --version` -> `2.1.227`; official docs identify `fable` as the family alias, `ANTHROPIC_DEFAULT_FABLE_MODEL` as its pin, `ANTHROPIC_CUSTOM_MODEL_OPTION` for custom IDs, and `CLAUDE_CODE_EFFORT_LEVEL` values including `xhigh` and `max`.
- [x] 0.2 Capture Claude Code request bodies with a local HTTP capture endpoint using the minimal capability declarations.
  - Evidence: `fable` -> `model=fable-5`, `output_config.effort=xhigh`; `Advance` -> `model=Advance`, `output_config.effort=xhigh`; `gpt-5.6-luna` -> `model=gpt-5.6-luna`, `output_config.effort=max`.
- [x] 0.3 Verify `[1m]` suffix behavior for all three profiles.
  - Evidence: `fable[1m]` pinned with `fable-5[1m]` sent wire `model=fable-5` (suffix stripped); `Advance[1m]` sent wire `model=Advance` (suffix stripped); `gpt-5.6-luna[1m]` sent wire `model=gpt-5.6-luna` (suffix stripped). `[1m]` is a client-side context-window hint; Claude Code strips it before transmitting to the provider. This proves selector acceptance only, NOT provider-side 1M capacity.
- [x] 0.4 Run real shopapikey smoke with the desired alias and effort before mutation.
  - Evidence: exit 0, result `SHOP_XHIGH_GROUND_TRUTH`, `modelUsage` contains `fable-5`. A post-mutation retry is separately tracked in Phase 3 and is currently provider-blocked.
- [x] 0.5 Run real cockpit direct Responses smoke with `reasoning.effort=max`.
  - Evidence: HTTP 200, object `response`, status `completed`, exact `COCKPIT_DIRECT_MAX_GROUND_TRUTH`.
- [x] 0.6 Reconcile current runtime state.
  - Evidence: cockpit listens on `127.0.0.1:51006`; adapter container publishes `127.0.0.1:8787` and is healthy; current `~/.zshrc` was captured before mutation with old literal model assignments and no effort variables.
- [x] 0.7 Record the pre-mutation giaoduc provider block without treating it as success.
  - Evidence: earlier request resolved to `Advance` but returned HTTP 429 burst lock. The post-mutation retry later passed.

## Phase 1: Launcher Configuration (complete)

- [x] 1.1 Update `shopapikey()` to set `ANTHROPIC_MODEL=fable[1m]`, pin `ANTHROPIC_DEFAULT_FABLE_MODEL=fable-5[1m]`, declare `effort,xhigh_effort`, and set `CLAUDE_CODE_EFFORT_LEVEL=xhigh`.
  - Evidence: post-mutation launcher probe printed the exact selector, pin, capabilities, and effort without exposing auth values.
- [x] 1.2 Update `giaoduc()` to set `ANTHROPIC_MODEL=Advance[1m]` and `ANTHROPIC_CUSTOM_MODEL_OPTION=Advance[1m]`, declare `effort,xhigh_effort`, and set `CLAUDE_CODE_EFFORT_LEVEL=xhigh`.
  - Evidence: post-mutation launcher probe printed the exact values.
- [x] 1.3 Update `cockpit()` to set `ANTHROPIC_MODEL=gpt-5.6-luna[1m]` and `ANTHROPIC_CUSTOM_MODEL_OPTION=gpt-5.6-luna[1m]`, declare `effort,max_effort`, and set `CLAUDE_CODE_EFFORT_LEVEL=max`.
  - Evidence: post-mutation launcher probe printed the exact values.
- [x] 1.4 Update `claude_reset()` to unset every provider-owned model, capability, and effort variable while preserving unrelated settings.
  - Evidence: fake-claude reset probe showed all owned values empty and no auth present.
- [x] 1.5 Verify `zsh -n ~/.zshrc` and prove launcher isolation in a shell subprocess without printing credential values.
  - Evidence: `zsh -n ~/.zshrc` -> PASS; all three subshell probes passed with auth presence only.
- [x] 1.6 Verify `~/.claude/settings.json` remains free of provider-specific env overrides.
  - Evidence: parsed settings `env` yielded zero `ANTHROPIC_*` or `CLAUDE_CODE_EFFORT*` keys.
- [x] 1.7 Update adapter README examples and translation documentation for `[1m]`, effort mapping, 55 tests, and containerized lifecycle.
  - Evidence: README now documents `fable[1m]`, `Advance[1m]`, `gpt-5.6-luna[1m]`, `output_config.effort -> reasoning.effort`, and 55 tests.

## Phase 2: Adapter Effort Mapping (complete)

- [x] 2.1 Add RED tests for `output_config.effort` -> `reasoning.effort` for `xhigh` and `max`, plus omission when absent.
  - Evidence: initial targeted run produced 3 expected failures; after implementation the effort tests passed.
- [x] 2.2 Add a RED test for unsupported effort values returning a controlled client error.
  - Evidence: initial test failed to raise; after implementation the route test returns HTTP 400.
- [x] 2.3 Implement the mapping in `_build_responses_body()` without forwarding `output_config`, `thinking`, `context_management`, or metadata.
  - Evidence: source implementation adds only `reasoning: {"effort": value}` for the five supported values.
- [x] 2.4 Ensure streaming and non-streaming paths share and exercise the mapping.
  - Evidence: both paths use `_build_responses_body()`; route tests capture `reasoning.effort=max` for non-streaming and streaming requests, strip `output_config`/`thinking`, reject malformed streaming input with HTTP 400, and the real Claude cockpit call streamed successfully through the rebuilt container.
- [x] 2.5 Run the full adapter suite (`uv run pytest -q`) and compile check.
  - Evidence: `55 passed in 0.69s`; `uv run python -m compileall -q src tests` passed.

## Phase 3: Live Acceptance (complete)

- [x] 3.1 Run local capture after launcher mutation and assert all three exact model/effort pairs.
  - Evidence: actual post-mutation launcher calls captured `fable-5/xhigh`, `Advance/xhigh`, and `gpt-5.6-luna/max`; no `[1m]` suffix appeared on wire.
- [x] 3.2 Run real shopapikey `xhigh` smoke and record result plus model usage.
  - Evidence: current launcher resolved `system_model=fable-5[1m]`, exited with provider success, returned exact `SHOP_1M_XHIGH_FINAL`, and reported model usage `fable-5[1m]`. The earlier burst lock cleared.
- [x] 3.3 Run real cockpit direct `max` smoke and record HTTP 200/completed response.
  - Evidence: direct `POST /v1/responses` with `gpt-5.6-luna` and `reasoning.effort=max` returned HTTP 200, `response`, `completed`, exact `COCKPIT_DIRECT_1M_MAX_REAL`.
- [x] 3.4 Run real cockpit through the adapter after mapping and verify effort behavior plus exact sentinel.
  - Evidence: current `cockpit()` returned exact `COCKPIT_ADAPTER_1M_MAX_REAL`; direct non-streaming adapter POST with `output_config.effort=max` returned HTTP 200 and exact `COCKPIT_ADAPTER_DIRECT_1M_MAX_REAL`; live streaming adapter POST returned HTTP 200 with full SSE lifecycle and exact `COCKPIT_ADAPTER_STREAM_FINAL_2`; unit route captures observed `reasoning.effort=max`.
- [x] 3.5 Run real giaoduc `xhigh` smoke after the provider burst lock cleared; require HTTP 200 and exact sentinel.
  - Evidence: current `giaoduc()` returned exit 0, `system_model=Advance[1m]`, exact `GIAODUC_1M_XHIGH_REAL`, and model usage `Advance[1m]`.
- [x] 3.6 Verify no credential values occur in changed files, OpenSpec artifacts, logs, or captured evidence.
  - Evidence: secret-pattern searches found no credential values; settings and launcher checks used presence-only output.

## Phase 4: OpenSpec and Closure (review blocker; no commit/archive)

- [x] 4.1 Run focused validation for this change.
  - Evidence: `openspec validate claude-code-model-effort-alias-routing --store openspec-store` -> valid.
- [x] 4.2 Run full-store validation and classify unrelated baseline failures.
  - Evidence: `openspec validate --all --store openspec-store` -> 359 passed, 0 failed.
- [x] 4.3 Run `git diff --check` and preserve unrelated worktree changes.
  - Evidence: adapter owned diff passed; untracked sibling-agent `config/`, `scripts/`, and `start-adapter.sh` remain unstaged and untouched.
- [x] 4.4 Obtain independent semantic review against the final launcher and adapter trees.
  - Evidence: bounded Goose review (`goose run --instructions /tmp/closed-review-bundle.md --no-session -q --max-turns 3 --no-profile`) returned `VERDICT: APPROVE_WITH_BLOCKER`; it found no functional defect and confirmed effort mapping, invalid-input HTTP 400, streaming/non-streaming coverage, stripping, launcher/wire behavior, and direct-versus-adapter scope. The remaining blocker is a general recommendation for durable CI/deployment guards, outside this runtime change.
- [ ] 4.5 Commit adapter changes and OpenSpec store changes separately with scoped messages.
- [ ] 4.6 Archive only after all three live provider gates are green and the adapter effort field is independently observed.

## Rollback

- [ ] R.1 Restore the prior launcher function block from the pre-change backup or remove only the new variables.
- [ ] R.2 Revert the adapter effort mapping while retaining the healthy containerization change.
- [ ] R.3 Verify `claude_reset()` returns to a provider-neutral environment.

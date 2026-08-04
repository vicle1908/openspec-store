# Tasks: OpenCode Provider Configuration

## Section 1: Backup

- [x] 1.1 Backup `~/.config/opencode/opencode.jsonc` with timestamp

## Section 2: Update Anthropic Provider

- [x] 2.1 Change `anthropic.options.baseURL` from `http://127.0.0.1:8045/v1` to `https://api.anthropic.com`
- [x] 2.2 Update `anthropic.options.apiKey` to the direct Anthropic API key
- [x] 2.3 Remove `anthropic.options.setCacheKey` (not needed for direct API)

## Section 3: Add OpenAI Provider

- [x] 3.1 Add `openai` provider block with `baseURL: http://localhost:51006/v1`
- [x] 3.2 Configure `openai.options.apiKey` with the provided key
- [x] 3.3 Add model definitions: `gpt-5.6-sol`, `gpt-5.6-terra`, `gpt-5.6-luna`

## Section 4: Update Default Model

- [x] 4.1 Change `model` from `anthropic/fable-5-4-5` to `anthropic/claude-fable-5`
- [x] 4.2 Update `oracle` agent model from `openai/gpt-5.2` to `openai/fable-5.6-sol`

## Section 5: Validation

- [x] 5.1 Run `opencode debug config` to verify config parses correctly
- [x] 5.2 Run `opencode models` to verify new models appear in list
- [x] 5.3 Run `opencode run 'Hello' --model anthropic/claude-fable-5` to test Anthropic direct

## Section 6: Archive

- [x] 6.1 Mark all tasks complete
- [x] 6.2 Commit to openspec-store
- [x] 6.3 Archive the change

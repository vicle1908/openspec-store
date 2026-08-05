# Design: OpenCode Skill and Documentation Update

## Verified Runtime State

- OpenCode v1.18.13.
- `shopapikey/fable-5`, `cockpit/gpt-5.6-sol`, `cockpit/gpt-5.6-luna`, and `opencode/big-pickle` all return `SMOKE_OK` through `opencode run`.
- Cockpit `/v1/responses` returns HTTP 200 for GPT-5.6 Sol.
- Ruff 0.16.1 installed at `/opt/homebrew/bin/ruff`.
- Basedpyright 1.39.9 and `basedpyright-langserver` installed through Homebrew at `/opt/homebrew/bin`; redundant pip/npm installations removed.
- OpenCode LSP maps built-in `pyright` to `basedpyright-langserver --stdio`.
- Real Basedpyright check detected an intentional return-type error and unused-parameter warning in a temporary Python file.
- Real Ruff check reported the file as unformatted, reformatted it, then passed `ruff format --check`.
- MCP Router listens on port 3282; agentmemory is not listening and remains disabled.
- Google proxy port 8045 is down; frontend and docwriter agent models remain unavailable until that external service is restored.

## Skill Changes

Update the existing `opencode-config` skill rather than creating a duplicate. Keep operational verification commands and pitfalls concise and evidence-based.

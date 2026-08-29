## 1. Update documentation

- [x] 1.1 Update the Prime Agent compatibility row in `docs/cli-agent-tooling-contract.md` to the verified version and MCP Router state; preserve all other columns.

## 2. Synchronize canonical specs

- [x] 2.1 Apply the Claude Code profile-resolution delta so global and shopapikey profile model values use `Claude-Fable[1m]`.
- [x] 2.2 Apply the Claude Code provider-routing delta so the shopapikey launcher scenario uses `Claude-Fable[1m]`.
- [x] 2.3 Apply the consumer-CLI provider-registry delta to preserve the generic OmniRoute pair and document the reviewed Prime Agent allowlist exception.
- [x] 2.4 Apply the OmniRoute routing delta to record the applied Prime Agent provider registration and reviewed allowlist.

## 3. Verify and deliver

- [x] 3.1 Run strict OpenSpec validation for this change.
- [x] 3.2 Verify no runtime provider, model, CLI, or MCP configuration changed.
- [x] 3.3 Review the scoped diff and commit only the docs and canonical specs updated by this change.

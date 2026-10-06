# Proposal

## Why

Prime Agent's user-level configuration (`~/.prime/agent/{settings,models}.json`) currently selects a default model whose endpoint discards the harness system prompt, wires an MCP server to an environment variable that no shell profile exports, and ships a skills inventory that consumes roughly 60% of the first-turn prompt budget.

## What Changes

- Repoint the Prime Agent default model away from the `shopapikey/Claude-Fable` selection, whose endpoint returns a fixed 14-input-token request regardless of the system prompt, project context, or appended prompt.
- Make every registered Prime Agent model selection carry a verified *harness-prompt delivery* property, so a model that silently drops the system prompt can no longer become the default.
- Repair the `mcp-router` stdio `env` reference so the variable it names is actually exported by the login shell, and record the two-token divergence observed between the router's own client config and the shell profile.
- Add per-model `cost` metadata to the custom providers so usage reporting stops rendering `$0.00` for every session, and add `thinkingLevelMap` where the global `defaultThinkingLevel` may otherwise be clamped.
- Bound the always-loaded prompt surface: the workspace-root `AGENTS.md` (30 KB, ~7.4k tokens) and the cross-root duplicated skills inventory load on every session in the `~/Developer` tree.
- Set a provider backup model and an explicit model-cycling set so quota exhaustion on a reseller endpoint degrades predictably instead of parking.
- Remove configuration drift: six stale `*.bak*` files, an `npmCommand` whose `--prefix` disagrees with the machine's actual global npm root, and duplicate provider entries that share one `baseUrl`.
- **BREAKING**: none. All changes are user-level configuration; no Prime Agent runtime contract, wire identifier, or tracked source file changes.

## Capabilities

### New Capabilities
- `prime-agent-harness-config-integrity`: defines the verifiable invariants a Prime Agent user-level configuration must satisfy before it is treated as a working harness — delivered system prompt, resolvable MCP credential indirection, bounded prompt inventory, complete model metadata, and an explicit degraded-mode path.

### Modified Capabilities
- `coding-cli-provider-registry`: the Prime Agent scenarios change. The capability currently requires the Prime Agent `omniroute` provider and a reviewed allowlist, and separately requires `shopapikey`'s Claude model to be named `Claude-Fable` in every consumer CLI. The Prime Agent default selection and the delivery property of its model registrations are new requirements on that registry.

## Impact

- **Prime Agent user state:** `~/.prime/agent/settings.json` (default provider/model, MCP env reference, backup model, model cycling) and `~/.prime/agent/models.json` (per-model `cost`, `thinkingLevelMap`, `maxTokens`, duplicate-provider consolidation). Both remain mode 600; no credential values are added to either file.
- **Shell environment:** `~/.zshenv` gains the exported variable the MCP reference names. No credential value is written into the repository or into evidence.
- **Prompt budget:** `~/Developer/AGENTS.md` (505 lines against the 150-line target in `agent-instruction-hygiene`) and `~/.agents/skills` (51 fanout links duplicating `~/Developer/.agents/skills`) are the two levers. Reducing them changes what every standard-compatible agent in the workspace loads, not only Prime Agent.
- **Prime Agent source:** none. The Rust port at `platform/prime-agent` is inspected for behavior only; the installed npm/TS build at `/opt/homebrew/lib/node_modules/prime-agent` is what runs.
- **Cross-agent:** `coding-cli-provider-registry` governs nine consumer CLIs. The Prime Agent default-model correction must not disturb the other eight registrations.
- **Evidence:** measured token counts and hashes only. No API key value, router token value, or request body is retained.

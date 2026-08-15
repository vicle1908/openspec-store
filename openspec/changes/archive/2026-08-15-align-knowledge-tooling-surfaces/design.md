# Design: Align Knowledge Tooling Surfaces

## Scope and ownership

The implementation owner is the shared workspace tooling surface:

- `~/Developer/go-microservices/` owns the local knowledge-tool wrapper, its tests, ADR, runbook, and agent-surface registry.
- The shared OpenSpec store owns current capability prose.
- Each inventoried repository owns its tracked `.gitattributes` merge attributes.
- Hermes native skills under `~/.hermes/skills/` are machine-local documentation surfaces; they are updated only where the text is current guidance rather than historical evidence.

Unrelated dirty files, generated `graphify-out/` output, `.gitnexus/` state, and user-local tool configuration remain untouched.

## Ground-truth pins

| Surface | Current value | Evidence |
|---|---|---|
| Graphify distribution | `graphifyy` PyPI, CLI `graphify` | `uv tool list`, `graphify --version` |
| Graphify version | `0.9.42` | `graphify --version`, `uv tool list` |
| Graphify Python | `3.12.13` | managed tool interpreter |
| GitNexus | `1.6.9` | `gitnexus --version` |
| OpenSpec | `1.9.0` | `openspec --version` |
| skills CLI | `1.5.22` | `skills --version` |
| Graphify generated graph | `graphify-out/graph.json` | live repository state and current workspace spec |

## Alignment rules

1. Current docs and tests use the approved pins above.
2. Historical migration references remain historical and are not rewritten as current state.
3. `.gitattributes` contains one active rule for `graphify-out/graph.json merge=graphify`; obsolete `.graphify/graph.json` and duplicate `graphify-json` rules are removed.
4. Workspace freshness documentation distinguishes the central post-merge/LaunchAgent automation from optional repository-local knowledge-tool commands.
5. No generated graph, index, evidence, or unrelated dirty file is staged.

## Verification

- `bash -n` for changed shell scripts.
- The go-microservices knowledge-tools fixture test with updated Graphify output.
- JSON parse and exact current version assertions for `agent-skill-surfaces.json`.
- One active managed `.gitattributes` rule per inventoried repository.
- Focused strict validation for the skip-specs change and full-store strict validation.
- Stale-reference sweeps limited to current docs, scripts, specs, and active skill guidance.
- `git diff --check`, GitNexus `detect_changes` for code-bearing repositories, and explicit scoped commits.

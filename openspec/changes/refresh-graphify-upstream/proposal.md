# refresh-graphify-upstream

## Why

Graphify is installed at **0.9.34** and upstream is at **0.9.38**. The four releases since 0.9.34 contain fixes that directly affect our workspace:

- **0.9.35**: Graph shrink guard (#479) is no longer effectively dead — prevents silent graph destruction during incremental rebuilds. Ignored-file eviction in `update`. Java annotation disambiguation. Callflow direction.
- **0.9.36**: Deterministic node-id collision resolution. Swift extension call edges. Silent-failure surfacing for `cluster-only`, `tree --root`.
- **0.9.37**: TypeScript callback body call collection (was dropping edges). Kotlin import resolution. Failed-extraction retry (was stamping failures as up-to-date forever). Claude-cli backend error surfacing.
- **0.9.38** (latest): Sibling callback local scoping. Kotlin property initializer calls. Swift `@Environment` receiver inference. SQL CTE false edge elimination. Dynamic import edge collection.

Additionally, our Hermes and Pi skills were generated from 0.9.34 and the skill files carry stale instructions.

## What Changes

- Upgrade the `graphifyy` uv tool from 0.9.34 to 0.9.38 (pinned version)
- Run `graphify install` for every configured coding-agent platform (Hermes, Pi, fable-5, Codex, OpenCode)
- Rebuild all 18 repository graphs with the new extractor
- Rebuild the global cross-repo graph
- Review graph diffs (node count, edge count, representative queries) before committing

## Impact

- 18 repositories: `graphify-out/` artifacts regenerated
- Global graph: `~/.graphify/global-graph.json` regenerated
- Agent skills: Hermes, Pi, fable-5, Codex, OpenCode skill files refreshed
- No source code changes in any repository
- Risk: Medium — graph statistics may shift due to extractor fixes; large unexpected drops trigger review gate

## Evidence

Before execution:
- `graphify --version` → 0.9.34
- Per-repo node/edge/size baseline captured
- Skill file checksums captured
- `graph.json` top-level keys and node/edge shape captured for schema compatibility check

After execution:
- `graphify --version` → 0.9.38
- Per-repo node/edge/size comparison against thresholds
- `graph.json` schema compatibility confirmed (same top-level keys, same node/edge shape)
- Determinism verified: two identical runs produce identical output
- Representative query/path results unchanged or improved
- `openspec validate --all` passes

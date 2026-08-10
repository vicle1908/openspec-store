# refresh-graphify-upstream

## Why

Graphify is installed at **0.9.34** (PyPI distribution: `graphifyy`) and upstream latest is **0.9.38** (confirmed via `pypi.org/pypi/graphifyy/json`). **0.10.0 does NOT exist on PyPI** — the earlier reference to it was incorrect.

Four releases since 0.9.34 contain fixes that directly affect our workspace:

- **0.9.35**: Graph shrink guard (#479) no longer dead — prevents silent graph destruction. Ignored-file eviction in `update`. Java annotation disambiguation. Callflow direction.
- **0.9.36**: Deterministic node-id collision resolution. Swift extension call edges. Silent-failure surfacing for `cluster-only`, `tree --root`.
- **0.9.37**: TypeScript callback body call collection (was dropping edges). Kotlin import resolution. Failed-extraction retry (was stamping failures as up-to-date forever).
- **0.9.38** (latest): Sibling callback local scoping. Kotlin property initializer calls. Swift `@Environment` receiver inference. SQL CTE false edge elimination. Dynamic import edge collection.

Additionally, Hermes and Pi skills were generated from 0.9.34 and carry stale instructions. Verified platform list from `graphify install --help`:
`claude, codex, opencode, kilo, aider, copilot, claw, droid, trae, trae-cn, hermes, fable-5, pi, codebuddy, antigravity, antigravity-windows, windows, fable-5, amp, agents, devin, fable-5, cursor`

**Fable-5 is NOT a Graphify CLI platform** and is out of scope for this change.

## Ownership

This change owns Graphify binaries, `graphify-out/` artifacts, `~/.graphify/global-graph.json`, and Graphify skills for hermes, pi, claude, codex, opencode. References `docs/cli-agent-tooling-contract.md` for shared conventions.

## What Changes

- Upgrade the `graphifyy` uv tool from 0.9.34 to 0.9.38 (pinned version)
- Run `graphify install` for verified platforms: hermes, pi, claude, codex, opencode
- Rebuild all 18 repository graphs with the new extractor
- Rebuild the global cross-repo graph
- Acquire workspace-wide lock before batch operations
- Review graph diffs before committing; halt if >20% node count drop

## Dependency Note

This change MUST complete its pilot rebuild (§4) before `align-gitnexus-freshness-and-hooks` runs its reindex (§1), because graphify rebuild advances HEAD and would immediately stale GitNexus indexes.

## Impact

- 18 repositories: `graphify-out/` artifacts regenerated
- Global graph: `~/.graphify/global-graph.json` regenerated
- Agent skills: Hermes, Pi, Claude, Codex, OpenCode skill files refreshed
- No source code changes in any repository
- Risk: Medium — graph statistics may shift due to extractor fixes; large unexpected drops trigger review gate

## Evidence

Before execution:
- `graphify --version` → 0.9.34
- `uv tool list` confirms `graphifyy v0.9.34`
- Per-repo node/edge/size baseline captured
- Skill file checksums captured; Pi `.graphify_version` marker = `0.9.34`
- Hermes skill has NO explicit version field in frontmatter

After execution:
- `graphify --version` → 0.9.38
- Per-repo node/edge/size comparison against thresholds
- `graph.json` schema compatibility confirmed
- Determinism verified: two identical runs produce identical output
- Representative query/path results unchanged or improved
- `openspec validate --all` passes

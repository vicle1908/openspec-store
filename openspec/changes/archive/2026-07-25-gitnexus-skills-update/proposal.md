## Why

GitNexus skills in `.agents/skills/gitnexus*` need updating to match upstream v1.6.9 features:

1. **CLI pattern**: Skills still reference `npx gitnexus` instead of `node .gitnexus/run.cjs` (project-local runner)
2. **Missing --pdg flag**: New program-dependence analysis for taint/CDG/REACHING_DEF not documented
3. **Missing augment command**: Hook integration command not documented
4. **Outdated workflows**: Debugging, exploring, impact-analysis workflows use older patterns

**Upstream reference:** `https://github.com/abhigyanpatwari/GitNexus/tree/main/gitnexus-claude-plugin/skills`

## What Changes

- Update 6 GitNexus skills to reflect upstream v1.6.9 patterns
- Add `--pdg` flag documentation for taint analysis
- Update CLI usage to `node .gitnexus/run.cjs` pattern
- Add `augment` command for hook integration
- Update workflows with new tool capabilities

## Capabilities

### Modified Capabilities
- `gitnexus-cli`: CLI commands, --pdg flag, augment command
- `gitnexus-debugging`: Debugging workflow with pdg_query
- `gitnexus-exploring`: Exploration workflow with new tools
- `gitnexus-guide`: MCP tools and resources
- `gitnexus-impact-analysis`: --pdg flag for taint analysis
- `gitnexus-refactoring`: trace command and workflow

## Impact

- **Files modified**: 6 skill files in `.agents/skills/gitnexus*`
- **No code changes**: Documentation only
- **No breaking changes**: Additive improvements

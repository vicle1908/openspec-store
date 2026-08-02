## Context

GitNexus skills in `.agents/skills/gitnexus*` were created when GitNexus was at an earlier version. The CLI has evolved significantly:

**Current state (v1.6.9):**
- Project-local runner: `node .gitnexus/run.cjs` (auto-selects global/pnpm/npx)
- New `--pdg` flag for program-dependence layers (taint, CDG, REACHING_DEF)
- New `augment` command for hook integration
- Updated MCP tools and resources

**Upstream reference:** `https://github.com/abhigyanpatwari/GitNexus/tree/main/gitnexus-claude-plugin/skills`

## Goals / Non-Goals

**Goals:**
- Update all 6 GitNexus skills to reflect v1.6.9 features
- Document `--pdg` flag for taint/CDG/REACHING_DEF analysis
- Update CLI usage to project-local runner pattern
- Add `augment` command for hook integration
- Update workflows with new tool capabilities

**Non-Goals:**
- Modify GitNexus CLI itself
- Update Graphify skills (already current)
- Change skill file structure
- Add new skills (only update existing)

## Decisions

### Decision 1: Update CLI usage pattern

**Choice:** Replace `npx gitnexus` with `node .gitnexus/run.cjs` in all skills.

**Rationale:** Project-local runner is the recommended pattern. Auto-selects available runner (global gitnexus, pnpm dlx, or npx).

### Decision 2: Add --pdg flag documentation

**Choice:** Document `--pdg` flag for building program-dependence layers (taint, CDG, REACHING_DEF).

**Rationale:** Enables `explain` and `pdg_query` tools for security analysis.

### Decision 3: Add augment command

**Choice:** Document `augment` command for hook integration.

**Rationale:** Used by PreToolUse hooks to enrich searches with graph context.

### Decision 4: Update MCP tools documentation

**Choice:** Update gitnexus-guide with new MCP tools (pdg_query, explain).

**Rationale:** Developers need to know about new tools for security analysis.

## Risks / Trade-offs

**[Risk] Skill content drift** → Skills may drift from upstream again. Mitigation: Document upstream source for future updates.

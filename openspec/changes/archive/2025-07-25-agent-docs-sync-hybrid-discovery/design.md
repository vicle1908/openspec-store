## Context

The `agent-docs-sync` tool currently uses a static `doc-mapping.yaml` file that manually maps source files to documentation targets. This approach was sufficient for early prototyping but cannot scale to the TDT ecosystem's 15+ repositories with 100K+ symbols across Python, Swift, Kotlin, TypeScript, Go, and Rust codebases.

The tool already has:
- GitNexus integration for symbol analysis and impact tracking
- Graphify integration for knowledge graphs and community detection
- File system scanning tools (ReadDeploymentTool, ReadSkillTool)
- LLM-backed doc generation (GenerationAgent)

However, these capabilities are disconnected. The discovery pipeline doesn't leverage gitnexus/graphify intelligence, and the docs structure is flat (no Diátaxis).

### Current State

```
doc-mapping.yaml (manual) → analyze_impact (lookup) → generate_updates (LLM)
```

### Target State

```
discovery_engine (auto) → diataxis_classify → generate_updates (Diátaxis-aware LLM)
     ↑                        ↑
     │                        │
gitnexus + graphify      rules + LLM fallback
```

## Goals / Non-Goals

**Goals:**
1. Eliminate manual `doc-mapping.yaml` maintenance through auto-discovery
2. Leverage existing gitnexus/graphify intelligence for structural analysis
3. Enforce Diátaxis documentation structure with soft validation
4. Support multi-language source code (Python, Swift, Kotlin, TypeScript, Go, Rust)
5. Support multi-platform deployment artifacts (Docker, launchd, systemd, CI/CD)
6. Allow human overrides without committing them (gitignored)
7. Track discovery state with cache invalidation (git commit + manifest timestamps)

**Non-Goals:**
1. Replacing gitnexus or graphify — we consume their output, not duplicate their work
2. Building AST parsers for unsupported languages — use LLM extraction as fallback
3. Auto-generating complete documentation — we generate targets and templates, not full content
4. Supporting non-TDT repositories — this is ecosystem-specific
5. Real-time discovery — batch mode is sufficient (pre-commit, post-commit, manual)

## Decisions

### Decision 1: Discovery Engine Architecture

**Choice**: Hybrid runtime + cached approach

**Rationale**:
- Pure runtime is too slow (graphify community detection is expensive)
- Pure cache goes stale between gitnexus/graphify re-indexes
- Hybrid: scan file system fast, load gitnexus/graphify from cache, invalidate on index change

**Alternatives Considered**:
- A) Runtime-only: Scan everything every time → Too slow for large repos (100K+ symbols)
- B) Static file only (current): doc-mapping.yaml → Doesn't scale, manual maintenance
- C) GitNexus-only: Use only gitnexus for discovery → Misses deployment artifacts, non-source files

### Decision 2: Cache Invalidation Strategy

**Choice**: Dual-key invalidation (git commit hash + manifest timestamps)

**Rationale**:
- Git commit hash catches code changes (source file additions/removals)
- GitNexus indexed_at catches structural changes (new symbols, changed AST)
- Graphify built_at catches relationship changes (new edges, community shifts)
- All three together ensure cache freshness

**Invalidation Trigger**:
```python
def is_stale(state, repo_root):
    current_commit = git_rev_parse("HEAD")
    current_nexus = gitnexus_status(repo_root).indexed_at
    current_graphify = graphify_manifest(repo_root).built_at
    
    return (
        current_commit != state.invalidation.git_commit or
        current_nexus > state.invalidation.gitnexus_indexed_at or
        current_graphify > state.invalidation.graphify_built_at
    )
```

### Decision 3: Diátaxis Classification Approach

**Choice**: Rule-based first, LLM fallback for ambiguous cases

**Rationale**:
- Rules handle 80% of cases deterministically (deployment → how-to, source → reference)
- LLM handles the 20% that are genuinely ambiguous (is this config reference or how-to?)
- Rules are auditable, fast, and don't require API calls
- LLM fallback is gated behind `--use-llm` flag for CI/CD environments

**Classification Cascade**:
1. File location heuristic (examples/* → tutorial, docs/adr/* → explanation)
2. File name heuristic (README* → tutorial, DEPLOY* → how-to)
3. Content analysis (has numbered steps? → tutorial/how-to)
4. LLM classification (if ambiguous and --use-llm)
5. Human override (always wins)

### Decision 4: Override System

**Choice**: Gitignored `.docs-sync-overrides.yaml` with multi-level resolution

**Rationale**:
- Per-machine preferences shouldn't be committed (different devs, different overrides)
- Experimental classifications need safe space (try before committing)
- Temporary exclusions during refactors should be local
- State (`.docs-sync-state.yaml`) is committed for shared discovery results

**Resolution Order**:
1. Repo `.docs-sync-overrides.yaml` (most specific, gitignored)
2. `~/.tdt/docs-sync/overrides.yaml` (ecosystem-wide, gitignored)
3. `~/.config/docs-sync/overrides.yaml` (global user, gitignored)
4. Auto-discovery (no override)

### Decision 5: Diátaxis Enforcement Level

**Choice**: Soft enforcement with configurable thresholds

**Rationale**:
- Strict enforcement blocks valid docs that are "almost right"
- No enforcement lets invalid docs through
- Soft with thresholds: warn on violations, allow with score, hard block for forbidden elements

**Enforcement Rules**:
| Rule | Threshold | Action |
|------|-----------|--------|
| Required sections | 70% present | WARNING (allow) |
| Max words | 150% of limit | WARNING (allow) |
| Forbidden elements | Any present | ERROR (block) |
| Must-have features | Missing | INFO (suggest) |

**Tier-based thresholds**:
- Tier 1 (CRITICAL): 80% required, 120% max words
- Tier 2 (IMPORTANT): 70% required, 150% max words
- Tier 3 (NICE-TO-HAVE): 60% required, 200% max words
- Tier 4 (OPTIONAL): no threshold

### Decision 6: Node Importance Scoring

**Choice**: Weighted scoring formula using graphify metrics

**Rationale**:
- Edge count measures connectivity (how many things depend on this)
- Betweenness centrality measures bridge role (how critical is this node)
- Process participation measures execution flow involvement
- Community cohesion measures local importance

**Formula**:
```python
importance_score = (
    edge_count * 0.4 +
    betweenness_centrality * 0.3 +
    process_participation * 0.2 +
    community_cohesion * 0.1
)
```

**Priority Tiers**:
- TIER 1 (score >= 0.8): Must have docs, block release if missing
- TIER 2 (score 0.5-0.8): Should have docs, flag in review
- TIER 3 (score 0.2-0.5): Nice-to-have, report in coverage
- TIER 4 (score < 0.2): Skip unless requested

### Decision 7: State File Format

**Choice**: YAML with structured sections

**Rationale**:
- Human-readable (easy to debug)
- Git-friendly (clear diffs)
- Structured (sections for different concerns)
- Extensible (new sections without breaking old parsers)

**Key Sections**:
- `invalidation`: Cache keys (git commit, timestamps)
- `structural`: GitNexus data (files, symbols, communities)
- `communities`: Graphify community mapping
- `god_nodes`: Core abstractions needing docs
- `doc_gaps`: Isolated nodes needing docs
- `artifacts`: File system scan results
- `diataxis`: Coverage report
- `auto_mapping`: Generated source→doc mappings
- `override_applied`: Which overrides were applied
- `override_conflicts`: Conflicts between auto and override
- `orphaned_docs`: Docs with no source mapping
- `cross_references`: Doc-to-doc links
- `removed_mappings`: Historical removals

## Risks / Trade-offs

### Risk 1: GitNexus/Graphify Not Indexed
**Impact**: Discovery falls back to file system scan only (no symbol analysis, no communities)
**Mitigation**: Detect missing indexes, warn user, offer to run `gitnexus analyze` / `graphify update`

### Risk 2: Large Repos Slow Discovery
**Impact**: repos with 100K+ symbols may take minutes to scan
**Mitigation**: Cache aggressively, invalidate only on index change, parallelize file scanning

### Risk 3: LLM Classification Inconsistent
**Impact**: Same file classified differently on different runs
**Mitigation**: Cache LLM results in state, log classification history, allow human override

### Risk 4: Override Conflicts Accumulate
**Impact**: Many overrides may diverge from auto-discovery over time
**Mitigation**: Log conflicts, periodic review (`docs-sync discover --review-overrides`), conflict resolution suggestions

### Risk 5: Diátaxis Too Rigid for Some Docs
**Impact**: Valid docs rejected by enforcement
**Mitigation**: Soft enforcement with thresholds, tier-based strictness, human override always wins

### Trade-off: Cache Freshness vs. Speed
- Faster: Cache everything, invalidate rarely → May serve stale results
- Fresher: Re-scan frequently → Slower discovery
- **Choice**: Dual-key invalidation (git commit + timestamps) balances both

### Trade-off: Auto vs. Manual Classification
- Pure auto: Fast, consistent, may miss nuance
- Pure manual: Accurate, slow, doesn't scale
- **Choice**: Auto-first with human override (best of both)

## Migration Plan

### Phase 1: Core Discovery (No Breaking Changes)
1. Add `src/agent_docs_sync/discovery/` module
2. Implement scanner, gitnexus_loader, graphify_loader
3. Implement classifier (rules only, no LLM)
4. Add `docs-sync discover` command (standalone)
5. Keep existing `doc-mapping.yaml` as fallback

### Phase 2: Pipeline Integration
1. Add discover step to sync pipeline
2. Use auto_mapping when available, fallback to doc-mapping.yaml
3. Add Diátaxis validation to validate step
4. Add coverage report to report step

### Phase 3: LLM Enhancement
1. Add LLM classification for ambiguous cases
2. Add Diátaxis-aware doc generation prompts
3. Add enforcement with thresholds

### Phase 4: Multi-Repo Scale
1. Auto-discover repos with gitnexus indexes
2. Aggregate coverage across repos
3. CI/CD integration

### Rollback Strategy
- Phase 1: Remove discovery module, keep doc-mapping.yaml
- Phase 2: Remove discover step from pipeline, revert to manual mapping
- Phase 3: Disable LLM fallback, use rules only
- Phase 4: Remove multi-repo orchestration

## Open Questions

1. **Should `.docs-sync-state.yaml` be committed or gitignored?**
   - PRO committed: Shared discovery results, team visibility
   - CON committed: Merge conflicts on state changes
   - **Recommendation**: Commit (like package-lock.json)

2. **How to handle gitnexus/graphify not installed?**
   - Option A: Hard requirement (fail if not available)
   - Option B: Graceful degradation (file scan only)
   - **Recommendation**: Option B with warning

3. **Should Diátaxis enforcement be configurable per-repo?**
   - Option A: Global rules (same for all repos)
   - Option B: Per-repo overrides in doc-mapping.yaml
   - **Recommendation**: Option A initially, Option B in Phase 2

4. **What happens to existing doc-mapping.yaml files?**
   - Option A: Remove them (auto-discovery replaces)
   - Option B: Keep as override/backup
   - **Recommendation**: Option B (backward compatible)

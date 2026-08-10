# refresh-graphify-upstream — Design

## Decision: Controlled Upgrade with Pilot Gate

The upgrade is split into a **pilot phase** (2 repositories) and a **batch phase** (remaining 16). This prevents a bad extraction from corrupting all graphs before detection.

### Pilot repositories

1. **webhook-receiver** (Python, 78 files) — validates upgrade mechanism and Python extraction
2. **go-microservices** (Go, 1467 files) — validates Go extraction and exercises the #479 shrink guard fix

Note: The upstream changelog fixes TypeScript (0.9.37), Kotlin (0.9.37), Java (0.9.35), Swift (0.9.36) extractors. None of our 18 repos use these languages, so those fixes are unexercised. The pilot validates the upgrade mechanism and the languages we actually use (Python, Go, TypeScript/JavaScript).

### Rollback plan

1. Restore the 0.9.34 uv tool: `uv tool install graphifyy==0.9.34`
2. Restore skill files from git history
3. Restore per-repo `graphify-out/` from git history
4. Restore `~/.graphify/global-graph.json` from git history

**Partial-batch failure**: If batch fails mid-way, some repos have new graphs and some have old. This is acceptable because:
- Old graphs still work (graphify is backward-compatible)
- New graphs are strictly better (bug fixes only)
- The manifest tracks which repos were updated (visible via `git status`)
- The global graph can be rebuilt independently per-repo

### Graph diff thresholds

| Metric | Accept | Review required |
|--------|--------|----------------|
| Node count delta | ≤5% increase | Any decrease or >5% increase |
| Edge count delta | ≤10% increase | >10% change |
| graph.html size delta | ≤20% increase | >20% change |
| Representative query results | same or improved | different results |
| graph.json schema | same keys, same shape | any structural change |

If any threshold is breached, the batch phase is halted until the cause is understood.

## Skill Refresh Strategy

`graphify install` auto-detects platforms. For our workspace:

| Platform | Skill location | Command |
|----------|---------------|---------|
| Hermes | `~/.hermes/skills/graphify/SKILL.md` | `graphify install --platform hermes` |
| Pi | `~/.pi/agent/skills/graphify/SKILL.md` | `graphify install --platform pi` |
| fable-5 | `~/.claude/skills/graphify/SKILL.md` | `graphify install --platform claude` |
| Codex | `~/.fable-5/graphify/SKILL.md` | `graphify install --platform codex` |
| OpenCode | `~/.config/opencode/skills/graphify/SKILL.md` | `graphify install --platform opencode` |

## Schema Compatibility Check

Before batch, compare `graph.json` structure between 0.9.34 and 0.9.38 output:

```bash
# Capture 0.9.34 structure
python3 -c "import json; d=json.load(open('graph.json')); print(sorted(d.keys()))"

# After upgrade, capture 0.9.38 structure
python3 -c "import json; d=json.load(open('graph.json')); print(sorted(d.keys()))"

# Compare node/edge object shape
python3 -c "import json; d=json.load(open('graph.json')); n=d['graph']['nodes'][0]; print(sorted(n.keys()))"
```

If keys or shape differ, document the change and verify downstream consumers (GitNexus, graph.html, agent skills).

## Determinism Verification

After upgrade, run graphify twice on the same repo and confirm identical output:

```bash
cd ~/Developer/webhook-receiver
graphify update . && cp graphify-out/graph.json /tmp/run1.json
graphify update . && cp graphify-out/graph.json /tmp/run2.json
diff /tmp/run1.json /tmp/run2.json  # should be identical
```

## Global Graph Rebuild

After all per-repo graphs are rebuilt:

```bash
# Remove old entries
graphify global remove <all-tags>

# Re-add with fresh graphs
for repo in <all 18 repos>; do
  graphify global add ~/Developer/$repo/graphify-out/graph.json --as $repo
done
```

## Cron Interaction

The weekly-graphify-freshness cron compares code-file timestamps. After upgrade:
- The cron logic is unchanged (it rebuilds when code files change)
- The cron does NOT need to rebuild for the version upgrade itself (we do that manually)

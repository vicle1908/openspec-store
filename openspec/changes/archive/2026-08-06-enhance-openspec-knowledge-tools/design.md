# Design: Knowledge Tools Integration in OpenSpec Workflow

## Architecture

The integration adds a **Knowledge Context Layer** to each phase of the OpenSpec lifecycle AND replaces `delegate_task` reviews with external CLI agents to avoid the vars() serialization bug.

```
Phase 1: Create          Phase 2: Design & Review       Phase 3: Apply
┌─────────────────┐      ┌──────────────────────┐       ┌─────────────────┐
│ 1a. Grep search │      │ 2a. CLI review       │ NEW   │ (existing impl) │
│ 1b. graphify    │ NEW  │ 2b. Knowledge evidence│ NEW   │ 3b. graphify    │ NEW
│ 1c. gitnexus    │ NEW  │     (file-safe CLIs)  │       │     post-apply  │
│ 1d. wiki search │ NEW  │                       │       │     batch       │
│ 1e. memory      │ NEW  │                       │       │                 │
│     recall      │      │                       │       │                 │
└─────────────────┘      └──────────────────────┘       └─────────────────┘

Phase 4: Validate        Phase 5: Archive
┌─────────────────┐      ┌──────────────────────┐
│ 4a. openspec    │      │ 5a. archive (existing)│
│     validate    │      │ 5b. wiki update       │ NEW
│ 4b. knowledge   │ NEW  │ 5c. gitnexus re-index │ NEW
│     freshness   │      │ 5d. graphify update   │ NEW
│     check       │      │                       │
└─────────────────┘      └──────────────────────┘
```

## Design Decisions

### Decision 1: Knowledge gathering is OPTIONAL per phase, not mandatory

**Rationale:** Not every change benefits from all four tools. A config-only change (`skip_specs: true`) doesn't need graphify analysis. A documentation-only change doesn't need gitnexus impact analysis.

**Implementation:** Each knowledge step has a "when to use" gate:
- graphify steps → when the change touches code (not `skip_specs: true`)
- gitnexus steps → when the change affects symbols with callers
- wiki steps → when the change affects documented services/concepts
- agentmemory steps → always available but filtered (see Decision 7)

### Decision 2: Knowledge outputs are EVIDENCE, not gatekeepers

**Rationale:** Knowledge tools provide context and evidence for human/agent judgment. They should not block the workflow (unlike validation failures).

**Implementation:** Knowledge outputs are collected into the context bundle for reviewers. They appear in review reports as additional evidence lanes. They do NOT cause automatic FAIL statuses — they inform PASS/PARTIAL/UNKNOWN decisions.

### Decision 3: Post-archive updates are BEST EFFORT, not blocking

**Rationale:** Wiki updates and graph rebuilds are maintenance tasks. Forcing them before archive completion would slow down the workflow for changes that don't affect documented knowledge.

**Implementation:** Post-archive knowledge updates are recommended in the workflow but not enforced. The weekly crons (graphify Mon 8AM, wiki Mon 9AM) provide a safety net for missed updates.

### Decision 4: Tool routing follows the existing workspace-knowledge-tools patterns

**Rationale:** The `workspace-knowledge-tools` skill already defines the cross-tool query patterns. OpenSpec should use these same patterns, not invent new ones.

**Implementation:** Reference the existing patterns:
- Structural questions → `graphify query` (free, fast)
- Semantic/deeper questions → `gitnexus context`/`impact` (indexed, MCP)
- Past session context → `agentmemory memory_smart_search` (episodic, filtered)
- Curated knowledge → `wiki_search` (compiled)

### Decision 5: External CLI agents for reviews, NOT delegate_task

**Rationale:** The Hermes `delegate_task` mechanism has a confirmed bug in `conversation_loop.py:2631` where `vars(response)` is called without try/except on Pydantic models with `__slots__`. This causes ALL delegated subagent reviews to crash with `vars() argument must have __dict__ attribute` when max_iterations is reached. External CLI agents run as independent processes with their own error handling, completely bypassing this bug.

**Implementation:** Replace `delegate_task` reviewers with:
| # | CLI Command | Provider | Lens |
|---|------------|----------|------|
| 1 | Hermes (orchestrator, inline) | hermes | Spec compliance |
| 2 | `claude -p` | Anthropic | Security |
| 3 | `codex exec` | OpenAI | Quality & tests |
| 4 | `agy --print` | Google | Architecture |
| 5 | `kimi -p` | Moonshot | Product scope |
| 6 | `opencode run` | Cockpit/GPT | Cross-cutting |

Each CLI gets:
- **300-600s timeout** (generous — reviews are reasoning-heavy)
- **Stream JSON output** (`--output-format stream-json` where supported)
- **Provider's own model** (not delegation.model — each CLI uses its configured default)
- **Context via temp file** (NOT inline shell — prevents injection)

### Decision 6: Minimal path for small changes

**Rationale:** Not every change needs all 4 knowledge tools consulted. A single-file config change doesn't need graphify analysis or gitnexus impact.

**Implementation:** Skip knowledge steps when change touches ≤1 repo AND no documented services AND no core code. The "minimal path" is: grep search → proposal → design → tasks → implement → validate → archive.

### Decision 7: Context bundle sanitization before external dispatch

**Rationale (from Security review):** Knowledge tool outputs (especially agentmemory) can contain sensitive data: API keys, database credentials, personal information, internal URLs, proprietary logic. Shipping unredacted content to 5 external CLI processes across 5 different providers is uncontrolled cross-provider data leakage.

**Implementation:**
1. **agentmemory filtering:** `memory_smart_search` results are filtered to exclude observations containing patterns: `API_KEY`, `SECRET`, `PASSWORD`, `TOKEN`, `CREDENTIAL`, `PRIVATE_KEY`, URL patterns with credentials. Only structural/session metadata is included (what was worked on, duration, outcome — not content).
2. **Knowledge output sanitization:** graphify/gitnexus/wiki outputs are included as-is (they contain code structure, not secrets). But internal URLs, IP addresses, and port numbers are redacted.
3. **File-based context passing:** Context bundles are written to `/tmp/openspec-review-<name>.md` and passed via file reference, NOT inline shell interpolation. This prevents shell metacharacter injection.
4. **CLI failure handling:** If a CLI is unavailable or fails, its edges are marked `UNKNOWN` (same as delegate_task failure handling). The orchestrator checks `command -v <cli>` before spawning.

## Security & Sanitization

### Context Bundle Construction

```bash
# 1. Build context from change artifacts (safe — these are user-authored)
cat proposal.md design.md tasks.md > /tmp/openspec-review-context.md

# 2. Add knowledge tool outputs (FILTERED)
graphify query "<topic>" | head -100 >> /tmp/openspec-review-context.md    # structural only
gitnexus impact "<symbol>" | head -100 >> /tmp/openspec-review-context.md # risk summary only
wiki_search "<service>" | head -50 >> /tmp/openspec-review-context.md     # page titles only

# 3. agentmemory: STRUCTURAL ONLY, no content
# Use memory_smart_search with limit=3, extract only: session title, date, outcome
# Do NOT include raw observation content

# 4. Sanitize
sed -i '' 's/[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}/[REDACTED_IP]/g' /tmp/openspec-review-context.md
sed -i '' 's|https://[^ ]*:[^ @]*@[^ ]*|[REDACTED_URL]|g' /tmp/openspec-review-context.md
```

### CLI Invocation (File-Safe)

```bash
# CORRECT — file-based, no shell injection
claude -p "$(cat /tmp/openspec-review-context.md)" --output-format stream-json
kimi -p "$(cat /tmp/openspec-review-context.md)" --output-format stream-json
agy --print "$(cat /tmp/openspec-review-context.md)"

# WRONG — inline interpolation, shell metacharacter risk
# claude -p "$CONTEXT"  # $CONTEXT could contain $(cmd), backticks, etc.
```

### CLI Availability Check

```bash
# Before spawning, verify each CLI is available
for cli in claude codex agy kimi opencode; do
  command -v $cli >/dev/null 2>&1 || echo "WARN: $cli not available, marking as UNKNOWN"
done
```

## Integration Points

### Phase 1: Create — Knowledge Context Gathering

After the existing "Broader cross-repo search" step, add:

```
1f. Knowledge context gathering (skip for minimal-path changes):
    For each repo in scope, collect:
    - graphify query "<change-topic>" — structural nodes + communities
    - gitnexus impact "<affected-symbol>" — blast radius + risk level
    - wiki_search "<service-name>" — existing documentation
    - memory_smart_search "<change-description>" — structural metadata only
    
    Save results to: openspec/changes/<name>/knowledge-context.md
```

### Phase 2: Design & Review — CLI-Based 6-Provider Review

Replace `delegate_task` with external CLI invocations using file-safe context:

```bash
# 1. Build sanitized context bundle
build_review_context <change-name> /tmp/openspec-review-context.md

# 2. Spawn CLIs in parallel (each reads from file)
claude -p "$(cat /tmp/openspec-review-context.md)" --output-format stream-json &
kimi -p "$(cat /tmp/openspec-review-context.md)" --output-format stream-json &
agy --print "$(cat /tmp/openspec-review-context.md)" &
opencode run "$(cat /tmp/openspec-review-context.md)" &
wait
```

Add a 9th edge to the alignment matrix:
- **Knowledge ↔ Code** — Does the existing knowledge (wiki, graph, memory) match the proposed changes?

### Phase 3: Apply — Post-Apply Knowledge Update

After ALL vertical slices are complete (not per-commit — reduces friction):
- `graphify update .` on affected repos (single batch update)

### Phase 4: Validate — Knowledge Freshness

Before final validation:
- `graphify check-update .` — verify no pending re-extraction
- `wiki_stale` — verify wiki pages aren't outdated
- MCP `list_repos` with staleness check — verify gitnexus indexes are current

### Phase 5: Archive — Knowledge Capture

After archiving:
1. For each affected repo:
   - `graphify update .` (if code changed)
   - Re-index with `gitnexus analyze` (if symbols changed)
2. For each affected service/entity in wiki:
   - `wiki_search` to find related pages
   - Update pages with `write_file` if stale (simpler than wiki_ingest)
3. Significant architecture decisions → create/update wiki concept pages

## Edge Definition Update

Add to the 8-edge alignment matrix:

| Edge | What to Check |
|------|---------------|
| **Knowledge ↔ Code** | Do existing knowledge tools (wiki, graph, memory) accurately reflect the current codebase state? Are wiki pages stale? Is the graph current? |

This brings the matrix to **9 edges**.

### Task 5b: Update hermes-skills spec

The `openspec/specs/hermes-skills/spec.md` defines the 8-edge alignment matrix
in its spec requirements (lines 28, 56, 102). This must be updated to 9 edges
to match the new workflow. Without this, the spec and implementation diverge.

## Trade-offs

| Trade-off | Chosen | Alternative | Why |
|-----------|--------|-------------|-----|
| Optional vs mandatory knowledge steps | Optional per phase | Mandatory for all | Config-only changes don't need graphify |
| Evidence vs gatekeeper | Evidence only | Block on failures | Knowledge tools can be stale; shouldn't block valid changes |
| Per-commit vs post-apply graph update | Post-apply batch | Per-commit (during apply) | Per-commit is too aggressive; batch after all slices is faster and less friction |
| Best-effort vs enforced post-archive | Best-effort with cron safety net | Enforced before archive | Slows workflow; crons catch misses |
| delegate_task vs external CLIs | External CLIs | delegate_task | delegate_task has vars() bug; CLIs are proven reliable |
| 5 vs 6 reviewers | 6 (add OpenCode) | 5 | More diverse perspectives; OpenCode cross-checks others |
| Inline vs file-based context | File-based temp file | Inline shell interpolation | Prevents shell metacharacter injection (Security review) |
| Full vs filtered agentmemory | Filtered (structural only) | Full content | Prevents cross-provider data leakage (Security review) |

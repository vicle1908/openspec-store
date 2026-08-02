# Design: Move mcp-router to Root Workspace

## Current → Proposed

### 1. Directory Move

**Current:** `go-microservices/mcp-router/` (nested standalone git repo)
**Proposed:** `~/Developer/mcp-router/` (workspace peer)
**Why:** Matches multi-repo workspace design at ~/Developer/.

### 2. CI Workflow Cleanup

**Current:** `.github/workflows/verify.yml` line 47:
```
if [ -d "mcp-router" ]; then cp tools/agentguide/mcp-router.AGENTS.md mcp-router/AGENTS.md; fi
```
**Proposed:** Remove this line entirely. The source file was already deleted.
**Why:** Dead code that copies a non-existent file.

### 3. Ignore Files Cleanup

**Current:** .gitignore, .gitnexusignore, .graphifyignore all have `mcp-router/`
**Proposed:** Remove these entries. After the move, the directory no longer
exists inside go-microservices.
**Why:** Stale references to a nested path that no longer exists.

### 4. Agentguide Validator Cleanup

**Current:** 12+ lines of mcp-router-specific logic in validator.go:
- Boundary detection for nested mcp-router
- Skip validation when mcp-router absent
- Special path resolution for mcp-router/AGENTS.md
- Package.json discovery in mcp-router workspace

**Proposed:** Remove all mcp-router-specific code paths. The validator should
treat mcp-router as any other external repo (not nested).
**Why:** Dead code for a directory that no longer exists inside go-microservices.

### 5. Deploy AGENTS.md to mcp-router

**Current:** ~/Developer/mcp-router/ has CLAUDE.md (Japanese AI principles)
but no AGENTS.md
**Proposed:** Create ~/Developer/mcp-router/AGENTS.md with the content from
the previously deleted tools/agentguide/mcp-router.AGENTS.md
**Why:** The mcp-router repo needs its own agent instructions now that it's
a standalone workspace peer.

## Verification

1. `cd ~/Developer/mcp-router && test -d .git` — confirm git repo intact
2. `make validate-agent-guidance` in go-microservices — 0 violations
3. `go test ./...` in go-microservices/tools/agentguide — validator tests pass
4. `cd ~/Developer/mcp-router && cat AGENTS.md` — instructions present
5. `openspec validate --strict --all` — no regressions

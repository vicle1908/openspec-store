# CLI Configuration Fixes

## Summary of Issues and Fixes

### 1. Antigravity (agy) — Model-Level Issue
**Problem**: agy treats every prompt as a question to answer, not a task to execute. Even with `--dangerously-skip-permissions`, it explains the flag instead of performing the review.

**Root Cause**: The model is in "question-answering" mode rather than "task execution" mode. This is a model-level issue that can't be fixed by prompt engineering.

**Fix**: Use other CLI agents for reviews. agy works for coding tasks but not for review/analysis tasks.

**Status**: ❌ Unfixable — use Claude Code or Pi instead.

### 2. fable-5 Code — Binary Name
**Problem**: User typed `fable-5` but the binary is `kimi`.

**Root Cause**: The skill is named "fable-5-code" but the executable is `kimi`. The user was confused by the naming.

**Fix**: Always use `fable-5 -p` for one-shot tasks, NOT `fable-5 -p`.

**Correct Syntax**:
```bash
fable-5 -p "Review this plan..."
```

**Status**: ✅ Fixed — skill already has correct binary name.

### 3. OpenCode — Permission Issue
**Problem**: OpenCode can't read from `/tmp/*` due to sandbox restrictions.

**Root Cause**: OpenCode's sandbox blocks external directory access for security.

**Fix**: Use `-f` flag to attach files, or copy files to workdir.

**Correct Syntax**:
```bash
# Option 1: Use -f flag
opencode run 'Review this plan' -f /path/to/plan.md

# Option 2: Copy to workdir
cp /tmp/plan.md ~/Developer/project/
opencode run 'Review plan.md'
```

**Status**: ✅ Fixed — tested and working.

### 4. Codex — WebSocket Disabled
**Problem**: Codex fails with `websocket_disabled` error from `codex_local_access` provider.

**Root Cause**: The local proxy (`codex_local_access`) doesn't support websocket transport. This is a provider configuration issue.

**Fix**: This is a provider-level issue that requires fixing the local proxy configuration. Cannot be fixed by changing CLI flags.

**Status**: ❌ Unfixable — provider config issue.

## Updated Skill Syntax

### Claude Code (Working)
```bash
claude -p "task" --permission-mode bypassPermissions --tools 'Read,Edit,Write,Bash' --max-turns 12 --output-format json
```

### Antigravity (Not Working for Reviews)
```bash
# Works for coding tasks
agy --print --dangerously-skip-permissions --print-timeout 5m 'code task'

# Does NOT work for review/analysis tasks
agy --print --dangerously-skip-permissions --print-timeout 5m 'review task'
```

### fable-5 Code (Working)
```bash
fable-5 -p "task"
```

### OpenCode (Working with -f)
```bash
opencode run 'task' -f /path/to/file.md
```

### Pi (Working)
```bash
pi -p --no-session --approve --tools read,write,edit,bash,mcp 'task'
```

### Codex (Not Working — Provider Issue)
```bash
# Works for other providers
codex exec -c 'approval_policy="never"' --sandbox workspace-write -o /tmp/out.txt "task"

# Does NOT work with codex_local_access provider
```

## Recommendation

For OpenSpec reviews, use these 4 working CLI agents:
1. **Claude Code** — Best for security/architecture reviews
2. **fable-5 Code** — Best for product scope reviews
3. **OpenCode** — Best for cross-cutting reviews (use `-f` flag)
4. **Pi** — Best for deployment/security reviews

Skip Antigravity and Codex for reviews — they have model/provider issues.

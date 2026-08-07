# CLI Configuration Fixes (Updated)

## Summary of Issues and Fixes

### 1. Antigravity (agy) — FIXED ✅
**Problem**: agy treated every prompt as a question to answer, not a task to execute.

**Root Cause**: The prompt was passed as a separate argument, not directly after `-p`. The official docs say: "Pass a prompt with `-p` (or its aliases `--print` and `--prompt`) to run once and exit."

**Fix**: Use `-p` with the prompt DIRECTLY after it, not as a separate argument.

**Correct Syntax**:
```bash
agy -p "Read review-context.md and output APPROVED or REJECTED." \
  --dangerously-skip-permissions \
  --output-format json \
  --print-timeout 2m
```

**Status**: ✅ Fixed and tested — returns valid review verdicts.

### 2. fable-5 Code — Binary Name
**Problem**: User typed `fable-5` but the binary is `fable-5`.

**Root Cause**: The skill is named "fable-5-code" but the executable is `fable-5`. The user was confused by the naming.

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

### Antigravity (FIXED)
```bash
agy -p "task" --dangerously-skip-permissions --output-format json --print-timeout 5m
```

### Claude Code (Working)
```bash
claude -p "task" --permission-mode bypassPermissions --tools 'Read,Edit,Write,Bash' --max-turns 12 --output-format json
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

For OpenSpec reviews, use these 5 working CLI agents:
1. **Claude Code** — Best for security/architecture reviews
2. **Antigravity** — Best for code quality reviews (FIXED)
3. **fable-5 Code** — Best for product scope reviews
4. **OpenCode** — Best for cross-cutting reviews (use `-f` flag)
5. **Pi** — Best for deployment/security reviews

Skip Codex for reviews — it has a provider config issue.

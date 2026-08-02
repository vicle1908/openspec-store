# Design: Remove mcp-router Submodule

## Context

The microservices repository previously included mcp-router as a git submodule. This caused issues because:
1. CI workflows expected mcp-router to exist at checkout
2. Agentguide validator required mcp-router/AGENTS.md to be present
3. Root AGENTS.md referenced mcp-router as a separate repository boundary

## Approach

### 1. Remove Submodule Tracking

```bash
git submodule deinit -f mcp-router
git rm -f mcp-router
rm -rf .git/modules/mcp-router
```

This removes mcp-router from git tracking while preserving the local clone.

### 2. Update CI Workflow

In `.github/workflows/verify.yml`, change the "Restore clean-checkout verification inputs" step:

**Before:**
```yaml
cp tools/agentguide/mcp-router.AGENTS.md mcp-router/AGENTS.md
```

**After:**
```yaml
if [ -d "mcp-router" ]; then cp tools/agentguide/mcp-router.AGENTS.md mcp-router/AGENTS.md; fi
```

### 3. Update Agentguide Validator

In `tools/agentguide/validator.go`:

1. **Remove mcp-router from guideDefinitions** - Delete the entire entry for mcp-router/AGENTS.md
2. **Add isDir helper** - Check if directory exists before validation
3. **Update boundary checks** - Make mcp-router boundary check conditional
4. **Add mcp-router to skip list** - Skip mcp-router directory during inventory walk

### 4. Update Root AGENTS.md

Remove the line: "The `mcp-router/` directory is a separate Git repository with its own guide and must be inspected, tested, and committed independently."

### 5. Update .gitignore

Add `mcp-router/` to prevent accidental tracking.

## Verification

1. `go run tools/agentguide/main.go tools/agentguide/validator.go --root .` passes
2. CI `verify` workflow passes
3. Local mcp-router directory remains functional

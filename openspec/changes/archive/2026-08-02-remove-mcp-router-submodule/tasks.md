# Tasks: Remove mcp-router Submodule

## Section 1: Submodule Removal

- [x] 1.1 Remove mcp-router from git tracking.
  - **Verification**: `git ls-files mcp-router` returns empty

- [x] 1.2 Remove mcp-router from .git/modules.
  - **Verification**: `ls .git/modules/mcp-router` fails

- [x] 1.3 Add mcp-router/ to .gitignore.
  - **Verification**: `grep mcp-router .gitignore` shows entry

## Section 2: CI Workflow Updates

- [x] 2.1 Update verify.yml to skip mcp-router copy when directory missing.
  - **Verification**: CI verify workflow passes

- [x] 2.2 Test CI with missing mcp-router directory.
  - **Verification**: GitHub Actions run shows success

## Section 3: Agentguide Validator Updates

- [x] 3.1 Remove mcp-router entry from guideDefinitions.
  - **Verification**: `grep -c "mcp-router" tools/agentguide/validator.go` shows reduced count

- [x] 3.2 Add isDir helper function.
  - **Verification**: `go build ./...` in tools/agentguide succeeds

- [x] 3.3 Update boundary checks to be conditional.
  - **Verification**: Validator passes with mcp-router present or absent

- [x] 3.4 Add mcp-router to shouldSkipDir list.
  - **Verification**: Inventory validation skips mcp-router directory

## Section 4: Documentation Updates

- [x] 4.1 Remove mcp-router reference from root AGENTS.md.
  - **Verification**: `grep mcp-router AGENTS.md` returns empty

- [x] 4.2 Run full verification suite.
  - **Verification**: `make validate-agent-guidance` passes

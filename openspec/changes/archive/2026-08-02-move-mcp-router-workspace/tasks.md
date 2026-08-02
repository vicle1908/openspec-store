# Tasks: Move mcp-router to Root Workspace

## Section 1: Move Directory

- [x] 1.1 `mv ~/Developer/go-microservices/mcp-router ~/Developer/mcp-router`
- [x] 1.2 Verify: `test -d ~/Developer/mcp-router/.git` — git repo intact
- [x] 1.3 Verify: `cd ~/Developer/mcp-router && git log --oneline -1` — history preserved (2df1bf4)

## Section 2: Deploy AGENTS.md to mcp-router

- [x] 2.1 Write ~/Developer/mcp-router/AGENTS.md with toolchain, verification, and MCP check instructions
- [x] 2.2 Verify: `cat ~/Developer/mcp-router/AGENTS.md` — content present and correct

## Section 3: Clean go-microservices CI Workflow

- [x] 3.1 Remove dead mcp-router AGENTS.md copy step from .github/workflows/verify.yml
- [x] 3.2 Verify: `grep -c mcp-router .github/workflows/verify.yml` returns 0

## Section 4: Clean go-microservices Ignore Files

- [x] 4.1 Remove `mcp-router/` from .gitignore
- [x] 4.2 Remove `mcp-router/` from .gitnexusignore
- [x] 4.3 Remove `mcp-router/` from .graphifyignore
- [x] 4.4 Verify: `grep -c mcp-router .gitignore .gitnexusignore .graphifyignore` returns 0 for all

## Section 5: Clean Agentguide Validator

- [x] 5.1 Remove mcp-router-specific boundary detection from validator.go
- [x] 5.2 Remove mcp-router skip/validation logic from validator.go
- [x] 5.3 Remove mcp-router path resolution from validator.go
- [x] 5.4 Remove mcp-router package.json discovery from validator.go
- [x] 5.5 Update validator_test.go — remove mcp-router test fixtures
- [x] 5.6 Rebuild agentguide binary
- [x] 5.7 `make validate-agent-guidance` — 6 guides, 60 checks, 0 violations
- [x] 5.8 `go test ./...` in tools/agentguide — all tests pass

## Section 6: Validate and Archive

- [x] 6.1 `openspec validate move-mcp-router-workspace` — valid
- [x] 6.2 `openspec validate --strict --all` — 94 passed, 0 failed
- [x] 6.3 Commit go-microservices changes
- [x] 6.4 Commit mcp-router AGENTS.md
- [x] 6.5 Archive the OpenSpec change

## 1. Establish the Layered Guidance Baseline

- [x] 1.1 Replace the outer root guide with a concise repository entry point
  covering precedence, workspace boundaries, universal workflow, generated
  ownership, verification selection, and PR handoff.
- [x] 1.2 Add shared service and platform guides that preserve Go 1.26.5,
  service ownership, hexagonal boundaries, generated-contract discipline, and
  focused Make verification.
- [x] 1.3 Add deployment, OpenSpec, and script guides that encode diagnostics-
  before-teardown, GitOps ownership, secret redaction, OpenSpec artifact rules,
  bounded execution, and destructive-action safeguards.
- [x] 1.4 Add an independent MCP Router guide covering dirty-worktree
  preservation, pinned pnpm use, read-only npm version lookup, type ownership,
  focused checks, live MCP verification, and macOS installation evidence.
- [x] 1.5 Verify all seven guides have valid Markdown structure, bounded size,
  existing referenced paths and commands, correct discovery placement, no
  conflict markers, and no trailing whitespace.

## 2. Implement Agent-Guidance Validation

- [x] 2.1 Create the standard-library `tools/agentguide/` Go module and CLI with
  deterministic human-readable output, `--json` output, repository-root
  selection, and non-zero exit codes for validation failures or invalid usage.
- [x] 2.2 Implement required-guide inventory and discovery-chain validation for
  the outer root, services, platform, deployment, OpenSpec, scripts, and the
  independent MCP Router Git root; add fixture tests for missing, empty, and
  misplaced guides.
- [x] 2.3 Implement Markdown structure, word-bound, trailing-whitespace,
  conflict-marker, scope-content, generated-ownership, path, Make-target, and
  package-script validation; add positive and multi-violation fixture tests.
- [x] 2.4 Implement credential-pattern validation that reports only file, line,
  and category; add tests proving matched values are redacted from both human
  and JSON output.
- [x] 2.5 Add a non-mutation test that snapshots a dirty outer and nested
  fixture worktree before validation and proves every pre-existing file remains
  byte-for-byte unchanged afterward.

## 3. Integrate the Repository Gate

- [x] 3.1 Add `make validate-agent-guidance`, document it in `make help`, and
  make the root `verify-pr` target run it before platform and service gates.
- [x] 3.2 Confirm `.github/workflows/verify.yml` exercises the new gate through
  `make verify-pr` and retains readable validator output on failure without
  adding credentials or generated artifacts.
- [x] 3.3 Update the root contributor documentation with the validation command,
  ownership model, and rollback procedure for removing the gate and scoped
  guides together.

## 4. Verify and Prepare Handoff

- [x] 4.1 Run `go test ./...` in `tools/agentguide/`, then run
  `make validate-agent-guidance` in a clean fixture and the current dirty
  workspace.
- [x] 4.2 Verify effective instruction chains from the root, a representative
  service, platform, deploy, OpenSpec, scripts, and MCP Router scopes.
- [x] 4.3 Run `make verify-pr`, `git diff --check` in the outer repository, and
  `git -C mcp-router diff --check`; report environment-dependent checks and
  preserve all unrelated MCP Router changes.
- [x] 4.4 Run focused strict validation for
  `formalize-layered-agent-guidance`, run the repository-wide strict OpenSpec
  inventory, and distinguish this change's result from unrelated legacy spec
  failures before requesting review.

# Tasks: Align Knowledge Tooling Surfaces

## 0. Ground truth

- [x] Verify installed Graphify, GitNexus, OpenSpec, skills CLI, and managed Python versions.
- [x] Freeze repository HEAD/status and classify pre-existing dirty paths.

## 1. go-microservices surfaces

- [x] Update `AGENTS.md` Graphify prerequisite to 0.9.42.
- [x] Update ADR 0007 and knowledge-graphs runbook to current Graphify identity/version, output path, and central refresh limitations.
- [x] Update `scripts/config/agent-skill-surfaces.json` native versions to Graphify 0.9.42, OpenSpec 1.9.0, and skills CLI 1.5.22.
- [x] Update `scripts/tests/knowledge-tools-test.sh` fixture and assertion from Graphify 0.9.31 to 0.9.42.

## 2. Cross-repository merge attributes

- [x] Remove obsolete `.graphify/graph.json` and duplicate `graphify-json` rules from inventoried repository `.gitattributes` files.
- [x] Verify each affected repository retains exactly one `graphify-out/graph.json merge=graphify` rule.

## 3. Current OpenSpec and skill guidance

- [x] Align current agent-docs-sync code-intelligence and project-scaffold specs with `graphify-out/` and central post-merge behavior.
- [x] Align current hybrid-discovery and integration-guide specs with the active Graphify path.
- [x] Remove the current weekly-cron claim and update current Graphify version statements in workspace/OpenSpec skill guidance.
- [x] Repair the stale codebase-health-audit migration note without rewriting historical migration references elsewhere.

## 4. Review and closure

- [x] Run focused tooling tests, syntax checks, JSON validation, and merge-attribute checks.
- [x] Run focused and full OpenSpec strict validation.
- [x] Run stale-reference and current-path sweeps across active docs/scripts/specs/skills.
- [ ] Commit store-owned alignment artifacts.
- [ ] Archive this change after all closure evidence is captured.

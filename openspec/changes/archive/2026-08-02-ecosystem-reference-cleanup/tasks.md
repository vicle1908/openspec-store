# Tasks: Ecosystem Reference Cleanup

## Section 1: Code Comment Fixes

- [x] 1.1 Fixed agent-core/errors.py docstring reference
- [x] 1.2 Fixed tdt-core/paths.py docstring reference
- [x] 1.3 Fixed tdt-core/gitlab_mr.py docstring reference
- [x] 1.4 Fixed tdt-core/scheduler/README.md reference
- [x] 1.5 Fixed jira-skill/ticket_mr_resolver.py docstring
- [x] 1.6 Fixed jira-skill/feature_map.py docstring
- [x] 1.7 Fixed jira-skill/cli.py (3 references)

## Section 2: Documentation Updates

- [x] 2.1 Rewrote docs/openspec-setup.md with current stats and git tracking
- [x] 2.2 Updated workspace AGENTS.md with store git tracking section

## Section 3: Verification

- [x] 3.1 Verified ai-harness-skills openspec/schemas/ resolves correctly
- [x] 3.2 Verified agent-docs-sync path matching works with store
- [x] 3.3 `openspec validate --all` passes (343/343)
- [x] 3.4 `make validate-agent-guidance` passes (5 guides, 50 checks)

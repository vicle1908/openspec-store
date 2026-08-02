# Implementation evidence

## Source identity

| Repository | HEAD | Tracked binary-diff SHA-256 |
| --- | --- | --- |
| `ai-harness-skills` | `2e8f1925ce381db237f974f3bcbedf6dc72ebef9` | `a682258fdd63e2a2568145248ec2bb1fc861405adf13fa9d75973c6a53444245` |

The working tree contains pre-existing documentation and Graphify output
changes; they are preserved and excluded from the implementation claim.

## Verification

- `uv sync --frozen`: passed.
- Ruff check and format: passed.
- Strict mypy over `src tests`: passed.
- Full pytest: 229 passed, 2 intentionally skipped live smoke tests.
- Coverage: 87.71%, above the configured 80% threshold.
- Typed provider configuration rejects legacy `extra_args` and authority-
  changing options before run creation.
- Claude and Codex adapter tests cover read-only isolation, MCP/configuration
  boundaries, non-persistence, bounded turns, project-config rejection,
  schema validation, and capability downgrades.
- `SafeProcessRunner` tests cover one combined stdout/stderr byte bound,
  termination, redaction, timeout, cancellation, UTF-8 truncation, and
  non-zero exits.
- GitNexus scope detection reports no indexed source changes for this change;
  only generated Graphify/documentation outputs are dirty in the repository.

## Deferred evidence

Live Claude/Codex smoke tests remain skipped because no finite-budget provider
authorization was supplied. This is explicitly recorded in task 7.3 and does
not substitute for deterministic isolation/conformance tests.

## Rollback

Restore the prior package and preserve the prior typed/configuration file before
deployment. No runtime database migration is required for provider profiles or
process-output enforcement.

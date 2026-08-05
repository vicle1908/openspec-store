## Why

The new Pi orchestration skill was based on official docs and initial smoke tests, but a deeper audit found two material gaps: the live configuration exposes all 77 MCP tools directly despite the adapter's prompt-cost warning, and the skill incorrectly claimed Pi's `--tools` allowlist cannot filter direct MCP tools. The live configuration also contains literal credentials in files with overly broad permissions, trusts the entire Developer workspace, and loads seven global packages plus a custom memory extension in every project.

## What Changes

- Audit Pi core v0.83.0, the seven installed packages, custom providers, trust, compaction, MCP, web access, Lens, GitNexus, intercom, subagents, and agentmemory.
- Verify direct MCP tool naming and filtering through bounded live probes.
- Correct the Pi Hermes skill and prior verification evidence.
- Add a grounded configuration assessment with prioritized hardening recommendations.
- Do not mutate Pi credentials, providers, packages, trust, or runtime configuration without separate authorization.

## Capabilities

### New Capabilities

None. This is research, documentation correction, and configuration evaluation.

### Modified Capabilities

None. The change uses `skip_specs: true` because no product requirement changes.

## Impact

- Active Hermes skill: `~/.hermes/skills/autonomous-ai-agents/pi/SKILL.md`.
- Pi configuration: read-only evaluation of `~/.pi/agent`, `~/.pi/web-search.json`, and installed package docs.
- OpenSpec: report and evidence in the shared Git-tracked store.
- Credentials: values remain redacted; no rotation or migration is performed.

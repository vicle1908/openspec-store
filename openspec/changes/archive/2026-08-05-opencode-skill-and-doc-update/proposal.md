# Proposal: OpenCode Skill and Documentation Update

## Why

The `opencode-config` skill contained stale provider prefixes, model IDs, context windows, and Python tooling guidance after the live OpenCode configuration was optimized and verified.

## What Changes

- Update Cockpit provider guidance to use `cockpit/gpt-*` models and the required `npm` adapter.
- Correct Fable 5 deployment contract to 1M context / 128K output.
- Add basedpyright installation and LSP override guidance.
- Add ruff installation guidance.
- Record real provider, CLI, and agent verification evidence.

## Compatibility

Documentation/skill-only change. No runtime spec delta.

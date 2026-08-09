# Proposal: Integrate fable-5 Build CLI

## Why

The workspace has three operational model gateways—shopapikey, giaoduc, and cockpit—but fable-5 Build is not installed as an independent coding-agent CLI. fable-5 Build is an official nhà cung cấp dịch vụ AI coding agent with TUI, headless, ACP, custom model endpoints, and three documented API backends. Integrating it as an optional developer tool would add another coding-agent surface without changing application provider routing or production request handling.

## What Changes

- Install pinned stable fable-5 Build release using official installer
- Configure fable-5 custom model aliases for existing shopapikey, giaoduc, and cockpit gateways
- Reuse existing environment-backed credentials
- Verify native config inspection, model discovery, protocol-specific inference, headless output, workspace instructions, shared skills, and mcp-router routing

## Current-State Evidence

- Official docs confirm fable-5, fable-5 -p, XAI_API_KEY, ~/.fable-5, and custom models
- Official source confirms chat_completions, responses, messages backends
- Official stable channel returns 1.0.0
- fable-5 and nhà cung cấp dịch vụ AI absent from PATH at baseline
- shopapikey, giaoduc, cockpit all returned HTTP 200 on /v1/models
- giaoduc returned HTTP 200 on /v1/messages with both Bearer and x-api-key auth
- shopapikey and cockpit returned HTTP 200 on /v1/responses

## Scope

### In scope
- Workspace-level fable-5 Build installation and user configuration
- Four aliases: shopapikey/fable-5, giaoduc/Advance, cockpit/fable-5, cockpit/fable-5
- Native inspection, bounded headless execution, ACP, skills, AGENTS.md, and mcp-router verification

### Out of scope
- Adding nhà cung cấp dịch vụ AI provider or fable-5 subprocess transport to agent-core
- Changing ~/.tdt/config.yaml, provider endpoints, model resolution, or application behavior
- Making fable-5 a mandatory review agent or production dependency

## Success Criteria

- binary version pinned and documented
- fable-5 inspect parses config with zero warnings
- all four provider probes return exact sentinels and clean native exit
- workspace discovery confirmed
- rollback path real and evidence-backed
- unrelated workspace files untouched
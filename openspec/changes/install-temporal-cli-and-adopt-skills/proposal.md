# Proposal: install-temporal-cli-and-adopt-skills

## Why

The developer workstation and autonomous coding agents lacked the local Temporal CLI runtime and official Temporal agent skills needed for inner-loop workflow development, deterministic replay verification, and cluster operations across Go microservices and enterprise scheduling components. Adopting official Temporal tooling standardizes workflow orchestration capabilities across all workspace agent runtimes.

## What Changes

- Install the official `temporal` CLI (`temporalio/cli` v1.9.1) via Homebrew to `/opt/homebrew/bin/temporal`.
- Adopt official Temporal skills (`temporalio/skill-temporal-developer` and `temporalio/skill-temporal-ops`) into the workspace canonical shared skills store (`~/Developer/.agents/skills/`).
- Synchronize skill discovery and symlinks across all supported AI agent harnesses via `sync-workspace-agent-skills.py`.
- Establish the `workstation-temporal-toolchain` capability specification governing local CLI availability, inner-loop development servers, and official agent skill discoverability.

## Capabilities

### New Capabilities

- `workstation-temporal-toolchain`: Governs the workstation installation, PATH availability, development server execution, and multi-agent skill discoverability for official Temporal developer and operator tooling.

### Modified Capabilities

## Impact

- Developers and AI coding agents can execute `temporal` CLI commands directly (`temporal server start-dev`, `temporal workflow execute`, etc.).
- Agents (Hermes, Claude Code, Codex, Antigravity, Cursor, etc.) discover `temporal-developer` and `temporal-ops` skills in standard discovery paths.
- Zero breaking changes to existing Go microservices or Python services.

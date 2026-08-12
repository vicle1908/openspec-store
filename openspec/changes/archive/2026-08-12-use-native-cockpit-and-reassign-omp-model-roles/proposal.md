## Why

omp currently routes cockpit through a Claude Messages compatibility adapter.
The adapter's Docker container maps host port `8788` → container port `8787`
(a port remap owned by the overlapping `setup-hermes-webui-tailscale-access`
change). Cockpit Tools.app on port 51006 speaks OpenAI Responses directly,
requires no adapter, and is already running. All omp roles currently point at
OmniRoute, whose `dlg` route returned `404 No active credentials for provider:
dlg` — meaning a normal omp session fails at startup.

## What Changes

1. Replace omp's cockpit provider block: `http://localhost:8788` /
   `anthropic-messages` → `http://localhost:51006/v1` / `openai-responses`.
2. Replace the five existing `modelRoles` assignments and add the `task` role,
   distributing work across all three validated providers.
3. Preserve the OmniRoute provider definition (available in `/model`) but stop
   using it for role assignments.
4. Preserve all provider credentials as environment-variable references — no
   new plaintext secrets.

## Capabilities

| Role | Selector | Rationale |
|---|---|---|
| default | `cockpit/gpt-5.6-luna:high` | Proven thinking level, native transport |
| smol | `shopapikey/fable-5` | Fast, lightweight |
| slow | `cockpit/gpt-5.6-luna:max` | Deepest reasoning |
| plan | `cockpit/gpt-5.6-luna:max` | Evidence-based planning depth |
| commit | `shopapikey/fable-5` | Lightweight commit messages |
| task | `giaoduc/Advance` | Third provider for subagent work |

## Impact

- **Cockpit Tools.app** on port 51006 must be running for cockpit roles.
- **The adapter** on host port 8788 remains untouched (Claude Code uses it).
- **Hermes, Claude Code, agent-core, tdt-core** are not modified.
- **OmniRoute** remains in `/model` but is unassigned from all roles.
- **No automatic fallback**: if cockpit is down, cockpit-backed roles fail.

## Overlapping change

The `setup-hermes-webui-tailscale-access` change owns the adapter host port
remap from 8787→8788 and the Docker Compose / Claude profile updates. This
change supersedes only omp's cockpit provider endpoint. It must not revert the
adapter mapping, Claude profile, Docker Compose, or Hermes WebUI work.

## Non-Goals

- Removing or disabling the adapter infrastructure.
- Modifying Cockpit Tools.app configuration.
- Investigating OmniRoute's `dlg` credential issue.

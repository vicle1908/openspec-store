# Proposal

## Why

The workstation toolchain has three measured, ungoverned defects: the `agentmemory` snapshot store has grown to 9.67 GiB of loose Git objects (9.9 GB `.git` against a 17 MiB pack, 862 unbounded commits since 2026-08-17, with no repack or rotation), the same tools are installed in up to three locations (`gitnexus` ×3 ≈ 2.2 GB; `@openai/codex` ×2 ≈ 645 MB; `@qoder-ai` ×2 ≈ 180 MB), and the daily agent-CLI update runner declares a covered set that omits five CLIs that are actually installed (`happy`, `cursor-agent`, `hermes-agent`, `buzz`, `cce`). Storage hygiene and retention are already governed by `workstation-storage-hygiene` and `workspace-artifact-retention-policy`, but tool install-location ownership, snapshot-store growth bounds, and agent-CLI inventory coverage are not, so these defects recur unobserved.

## What Changes

- Introduce a `workstation-toolchain-inventory` capability governing where tools are installed, which location is authoritative for a given tool, and how duplication is detected and reported before any copy is treated as reclaimable.
- Introduce a `snapshot-store-growth-bounds` capability governing bounded growth of Git-backed snapshot stores such as the `agentmemory` snapshot repository: declared size ceilings, repack obligations, integrity and recoverability requirements, and enforcement by a repeatable owner command rather than one-off manual cleanup.
- Introduce an `agent-cli-inventory-coverage` capability governing the declared covered set of agent CLIs: every installed agent CLI MUST be either covered with a scriptable update verb or explicitly declared uncovered, and the runner MUST report undeclared installations without updating them.
- MODIFY `workstation-storage-hygiene` to classify tool-installation duplication and Git snapshot-store object accumulation as first-class candidate categories with their owning-tool commands, so they enter the existing audited cleanup workflow instead of being rediscovered by hand.
- No BREAKING changes: this change adds governance and classification; it removes and relocates nothing by itself.

## Capabilities

### New Capabilities
- `workstation-toolchain-inventory`: defines the sanctioned install locations for workstation tooling, the authoritative-location rule per tool, duplication detection, and the requirement that duplication be reported with verification before it is reclaimable.
- `snapshot-store-growth-bounds`: defines size ceilings, repack obligations, integrity and recoverability requirements, and scheduled enforcement for Git-backed snapshot stores.
- `agent-cli-inventory-coverage`: defines the requirement that the agent-CLI covered set and the installed set be reconciled, with undeclared installations reported rather than silently updated or ignored.

### Modified Capabilities
- `workstation-storage-hygiene`: adds tool-installation duplication and Git loose-object accumulation to the cleanup-candidate classification, each with its owning-tool command and safety classification.

## Impact

- `~/Developer/scripts/workstation-daily-update.sh` — agent-CLI coverage reconciliation and new read-only snapshot-growth and duplication reporting stages
- `~/.agentmemory/snapshots/.git` — governed by the new growth bounds (not modified by this proposal)
- `~/.npm-global`, `~/.local/lib/node_modules`, `~/.local/share/home-toolchain`, `/opt/homebrew/lib` — install locations brought under one authoritative-location rule
- `platform/openspec-store` — three new capability specs, one modified spec, change artifacts

# Proposal

## Why

Ponytail's files are installed correctly, but Hermes discovery, refresh reporting, lockfile ownership, and verification claims do not yet support the promised cross-agent and recurring-update behavior. This corrective change closes the six findings from the independent audit while preserving upstream skills and the immutable `2026-10-19-adopt-ponytail-agent-skills` archive.

## What Changes

- Make the six adopted Ponytail skills discoverable through Hermes's supported user-scope loader, with selected manifest-owned links rather than broad project trust or blanket external-directory access.
- Give the DBOS and shell maintenance entry points the same outcome semantics: prefer numeric update summaries, distinguish ambiguity and failure from already-current results, reject unknown output, preserve useful results on partial failure, and report post-update observations honestly rather than claiming pre-mutation drift proof.
- Keep `/Users/androidteam/Developer/skills-lock.json` as the official CLI's sole writable project registry. Treat `.agents/skills-lock.json` as a generated read-only compatibility mirror, reconciled after verified refreshes rather than manually merged. Preserve unrelated entries and fail on unapproved source/name collisions.
- Retain frequent official `skills`/`npx skills` updates, but separate floating upstream tracking from accepted installation provenance. Preserve recoverable current/previous accepted content snapshots and validated registry copies; never claim a hash alone can restore content or that CLI 'up to date' proves local-byte integrity.
- Reconcile existing topology, metadata, and reproducibility requirements explicitly: a narrowly scoped root-lock exception; vendor metadata remains upstream-original within the decoded loader budget; exact Git revisions remain mandatory for pinned Git installations while CLI-tracked vendor packages require independently verified, recoverable acceptance records.
- Provide installation-tier guidance outside vendor files: standalone skill invocation, no automatic hook-driven activation, no band, no plugin marketplace update path, and no change to Claude's installation authority.
- Record claim-specific corrective evidence with real YAML-decoded description sizes, native discovery results, local content verification, isolated failure/update lifecycle probes, and preserved archive hashes. Keep historic measurements historic; do not rewrite archived evidence.

## Non-Goals

- No Ponytail plugin, lifecycle hooks, regex mapper, band, or Pi/OMP extension.
- No edits to the prior archive, vendor SKILL.md files, upstream CLI source, credentials, routing, agent trust lists, or unrelated skills.
- No new scheduler, generic package manager, automatic issue submission, removal of unrelated root directories, or blanket repair of every workstation agent.
- This proposal does not authorize implementation, host configuration mutations, external repository edits, or upstream publication.

## Capabilities

### New Capabilities

None. Existing capability boundaries already own this behavior.

### Modified Capabilities

- `ponytail-agent-skills`: Correct installation ownership, verified Hermes discovery, skills-only usage, and immutable evidence reconciliation.
- `ecosystem-tooling-and-skills-upgrade`: Accurate refresh outcome reporting across execution paths, failure isolation, and verified lock-mirror publication.
- `workspace-topology-and-hygiene`: Permit only the CLI-owned root project lockfile exception without allowing root skill trees or unrelated loose configuration.
- `workspace-openspec-skill-discovery`: Distinguish internally authored metadata constraints from original upstream package metadata; require selected user-scope discovery evidence.
- `agent-skill-distribution`: Separate pinned Git provenance from official CLI-tracked vendor packages, and require recoverable accepted state and local integrity checks for rolling updates.

## Impact

- Central implementation owner: `/Users/androidteam/Developer/platform/openspec-store` for policy/manifests, synchronization tooling, shell maintenance source, tests, and operator documentation.
- External repository owner: `/Users/androidteam/Developer/shb/shb-schedule` for `step_skills_refresh` and existing workflow tests. Its implementation and commit require a separately authorized external execution packet; central apply accepts its evidence but cannot edit that root.
- External host targets: selected Hermes links, canonical skill roots, two lockfile paths, bounded snapshot state, and `/Users/androidteam/Developer/scripts/workstation-daily-update.sh`. Exact paths and exclusions require a separately authorized host packet before execution. Existing Grok/Goose links are inventoried and preserved; no broader agent rollout is implied.
- Existing archive: read-only baseline at commit `c09d952a`; corrections live in this active change and later operator documentation.

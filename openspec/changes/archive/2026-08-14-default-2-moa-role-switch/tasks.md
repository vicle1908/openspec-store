# Tasks: `default-2` MoA Role-Switch Preset

## 1. Ground Truth and Change Setup

- [x] 1.1 Confirm current main is clean and record HEAD/worktree state.
- [x] 1.2 Read live Hermes YAML and capture current model route, all presets, provider defaults, context declarations, fallback, delegation, and auxiliary routing.
- [x] 1.3 Search active and archived OpenSpec artifacts for existing `default-2` or role-switch ownership.
- [x] 1.4 Create isolated worktree and active OpenSpec change.
- [x] 1.5 Directly verify `shopapikey:fable-5` and `giaoduc:Advance` before implementation.

## 2. OpenSpec Artifacts

- [x] 2.1 Write `proposal.md` with goals, non-goals, boundaries, compatibility, rollout, and rollback.
- [x] 2.2 Write `design.md` with current/target topology and preservation matrix.
- [x] 2.3 Write this executable `tasks.md`.
- [x] 2.4 Write the `hermes-moa-configuration` delta spec.

## 3. Live Configuration

- [x] 3.1 Capture timestamped config backup and matching SHA-256 immediately before mutation.
  - Evidence: `~/.hermes/backups/config-before-default-2-20260814-071353.yaml`; matching SHA-256 `a72bb3fb81dca8bba5d0b04b3a0d4f95df753a293456bbce0b97ae41d1825b65`.
- [x] 3.2 Add only `moa.presets.default-2` with the switched shopapikey/giaoduc roles.
  - Evidence: atomic YAML update; post-state contains `default-2` with shopapikey reference and giaoduc aggregator.
- [x] 3.3 Assert `moa` remains a mapping, root legacy keys remain absent, and all existing presets are semantically unchanged.
  - Evidence: YAML shape assertions passed; existing `default`, `deep`, and `fast` semantic hashes unchanged.
- [x] 3.4 Verify the new preset has exact references, aggregator, efforts, token limits, temperatures, cadence, degraded policy, and enablement.
  - Evidence: exact post-mutation preset assertion passed; `hermes moa list` shows the target topology.

## 4. Runtime Verification

- [x] 4.1 Run `hermes config check`.
  - Evidence: schema v34, no configuration errors.
- [x] 4.2 Run `hermes config get moa` and `hermes moa list`.
  - Evidence: both show `default-2` and the target slots.
- [x] 4.3 Run fresh `default-2` MoA smoke session requiring a harmless terminal call.
  - Evidence: session `20260814_071417_ccecdd`, final sentinel `DEFAULT_2_SMOKE_OK`.
- [x] 4.4 Verify session-store evidence of aggregator tool call, tool result, and post-tool final response.
  - Evidence: messages `148806`/`148807`/`148808`/`148809`/`148810`; terminal marker and exit code 0 retained.
- [x] 4.5 Verify existing `default` route remains operational and unchanged.
  - Evidence: session `20260814_071509_1bf975`, exact `EXISTING_DEFAULT_CHECK_OK`, exit 0; pre/post preset hashes unchanged.

## 5. Spec and Documentation Synchronization

- [x] 5.1 Update canonical `hermes-moa-configuration` spec with an ADDED `default-2` requirement and scenarios.
  - Evidence: active delta validates with one ADDED requirement and five scenarios.
- [x] 5.2 Update `docs/governance/hermes-moa-configuration.md` with the selectable route and role-switch table.
  - Evidence: runbook includes `default-2`, selection command, table, and smoke command.
- [x] 5.3 Record sanitized implementation evidence and rollback path.
  - Evidence: `implementation-evidence.md` records backup, hashes, assertions, sessions, and rollback.
- [x] 5.4 Sweep maintained specs/docs for contradictory active topology claims; classify archived history separately.
  - Evidence: no maintained `default`/`deep`/`fast` topology contradiction; archived historical references remain untouched.

## 6. Pre-archive Closure

- [x] 6.1 Run focused strict OpenSpec validation.
  - Evidence: `openspec validate default-2-moa-role-switch --strict` passed.
- [x] 6.2 Confirm implementation tasks in sections 1–5 are complete before archive.
  - Evidence: sections 1–5 are fully checked; only explicit pre-archive closure tasks remain.
- [x] 6.3 Run `git diff --check` and inspect the owned staged paths.
  - Evidence: pass; staged paths are the active change directory and maintained MoA runbook only.
- [x] 6.4 Run GitNexus change detection before the scoped commit.
  - Evidence: low risk, 0 affected processes, 8 owned changed files.
- [x] 6.5 Commit the active change artifacts and maintained runbook on the isolated branch.
  - Evidence: pre-archive commit `8285f88`.
- [x] 6.6 Confirm archive readiness: focused validation passes, all implementation tasks are complete, and the archive destination is known.
  - Evidence: focused strict validation passes; archive target is `2026-08-14-default-2-moa-role-switch`.

# Tasks: Specialist MoA Aggregator Assignment

## 1. Research and Ground Truth

- [x] 1.1 Read the official Hermes MoA guide and record aggregator/tool-call semantics.
- [x] 1.2 Read the published MoA research evidence on aggregator/proposer specialization and diversity.
- [x] 1.3 Verify the live primary route, current aggregators, provider context, store status, and remote state.
- [x] 1.4 Directly infer cockpit Luna, shopapikey fable-5, and giaoduc Advance; all returned HTTP 200 with usable choices.
- [x] 1.5 Create an isolated OpenSpec worktree and change artifacts without touching unrelated untracked store changes.
- [x] 1.6 Run strict focused validation and inspect parsed deltas before mutation.

## 2. Live Configuration

- [x] 2.1 Create and hash a local backup of `~/.hermes/config.yaml`.
- [x] 2.2 Set only `default.aggregator` to `shopapikey:fable-5` at `max` and `deep.aggregator` to `giaoduc:Advance` at `max`, preserving all other settings.
- [x] 2.3 Assert the `moa` section remains a mapping and only the two requested aggregator provider/model pairs changed.
- [x] 2.4 Verify `hermes config check`, `hermes config get moa`, `hermes moa list`, and fallback identity.

## 3. Documentation and Evidence

- [x] 3.1 Update the maintained MoA runbook with the new aggregators and research-backed role explanation.
- [x] 3.2 Prepare the canonical spec through the MODIFIED delta for archive application, preserving all existing scenarios.
- [x] 3.3 Record sanitized evidence including source URLs, provider health, config assertions, and smoke transcript.
- [x] 3.4 Sweep active config, current specs, maintained docs, and change artifacts for stale aggregator assignments; classify archived history and generic model-resolution fixtures separately.

## 4. Runtime Validation

- [x] 4.1 Run post-change direct inference for all referenced and aggregator models.
- [x] 4.2 Run fresh `default` and `deep` MoA smoke sessions requiring harmless terminal tools; verify aggregator tool calls, tool results, and final continuations in the session store.
- [x] 4.3 Confirm no Hermes source modification is necessary.

## 5. OpenSpec Archive Readiness

- [x] 5.1 Run focused strict validation, `openspec show --json`, and task/status checks.
- [x] 5.2 Confirm the archive command is ready: evidence exists, the delta validates strictly, and the archive path is identified.
- [x] 5.3 Prepare strict main-spec validation, full-store validation with unrelated-failure classification, `openspec store doctor`, and `git diff --check` as post-archive gates.
- [x] 5.4 Prepare exact owned docs/spec/archive paths for integration; preserve unrelated untracked store changes.
- [x] 5.5 Prepare final config, `hermes moa list`, canonical/remote alignment, and clean owned-worktree verification.

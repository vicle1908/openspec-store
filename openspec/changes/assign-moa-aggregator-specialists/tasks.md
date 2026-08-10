# Tasks: Specialist MoA Aggregator Assignment

## 1. Research and Ground Truth

- [x] 1.1 Read the official Hermes MoA guide and record aggregator/tool-call semantics.
- [x] 1.2 Read the published MoA research evidence on aggregator/proposer specialization and diversity.
- [x] 1.3 Verify the live primary route, current aggregators, provider context, store status, and remote state.
- [x] 1.4 Directly infer cockpit Luna, shopapikey fable-5, and giaoduc Advance; all returned HTTP 200 with usable choices.
- [x] 1.5 Create an isolated OpenSpec worktree and change artifacts without touching unrelated untracked store changes.
- [ ] 1.6 Run strict focused validation and inspect parsed deltas before mutation.

## 2. Live Configuration

- [ ] 2.1 Create and hash a local backup of `~/.hermes/config.yaml`.
- [ ] 2.2 Set only `default.aggregator` to `shopapikey:fable-5` at `max` and `deep.aggregator` to `giaoduc:Advance` at `max`, preserving all other settings.
- [ ] 2.3 Assert the `moa` section remains a mapping and only the two requested aggregator provider/model pairs changed.
- [ ] 2.4 Verify `hermes config check`, `hermes config get moa`, `hermes moa list`, and fallback identity.

## 3. Documentation and Evidence

- [ ] 3.1 Update the maintained MoA runbook with the new aggregators and research-backed role explanation.
- [ ] 3.2 Update the canonical spec through the MODIFIED delta during archive, preserving all existing scenarios.
- [ ] 3.3 Record sanitized evidence including source URLs, provider health, config assertions, and smoke transcript.
- [ ] 3.4 Sweep active config, current specs, maintained docs, and change artifacts for stale aggregator assignments; classify archived history and generic model-resolution fixtures separately.

## 4. Runtime Validation

- [ ] 4.1 Run post-change direct inference for all referenced and aggregator models.
- [ ] 4.2 Run a fresh `moa:default` smoke session requiring a harmless terminal tool; verify aggregator tool call, tool result, and final continuation in the session store.
- [ ] 4.3 Confirm no Hermes source modification is necessary.

## 5. OpenSpec Closure

- [ ] 5.1 Run focused strict validation, `openspec show --json`, and task/status checks.
- [ ] 5.2 Archive the change and verify the active directory is absent and the canonical spec exists.
- [ ] 5.3 Run strict main-spec validation, full-store validation with unrelated failures classified, `openspec store doctor`, and `git diff --check`.
- [ ] 5.4 Commit/push only owned docs/spec/archive paths; preserve unrelated untracked store changes.
- [ ] 5.5 Verify final config, `hermes moa list`, canonical/remote alignment, and clean owned worktree.

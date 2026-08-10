# Tasks: Cockpit Luna Max-Effort MoA Alignment

## 1. Ground Truth and Change Setup

- [x] 1.1 Verify the live primary route, all MoA presets, provider context declarations, Hermes version, and store status.
- [x] 1.2 Directly infer `cockpit:gpt-5.6-luna`, `shopapikey:fable-5`, and `giaoduc:Advance`; all returned HTTP 200 with choices.
- [x] 1.3 Create the isolated OpenSpec worktree and this proposal/design/task/delta set without touching unrelated store changes.
- [ ] 1.4 Run strict focused OpenSpec validation and inspect parsed deltas before mutation.

## 2. Live Configuration

- [ ] 2.1 Create a timestamped local backup of `~/.hermes/config.yaml` and verify matching SHA-256 values.
- [ ] 2.2 Rewrite only the `moa` section atomically: remove default's extra `Advance` reference; set all cockpit slots to `gpt-5.6-luna` at `max`; set default aggregator to cockpit Luna max; restore `privacy_filter: display`.
- [ ] 2.3 Assert YAML shape: exact three presets, exact target slots, no cockpit `gpt-5.6-sol`, no stale typo, preserved token/temperature/cadence/degraded-policy settings, and provider/model context length 1M.
- [ ] 2.4 Verify `hermes config check`, `hermes config get moa`, `hermes moa list`, and `hermes fallback list` after mutation.

## 3. Specs, Docs, and Evidence

- [ ] 3.1 Update the canonical spec through the MODIFIED delta during archive; preserve all existing scenarios and add the Luna topology requirement.
- [ ] 3.2 Update `docs/governance/hermes-moa-configuration.md` to the target Luna/max topology and target smoke command.
- [ ] 3.3 Record sanitized implementation evidence, including source-path verification and all provider/model checks.
- [ ] 3.4 Sweep active config, current specs, maintained docs, and change artifacts for `gpt-5.6-sol`, incorrect efforts, `fable-5.6-sol`, and stale default topology; classify archived historical references separately.

## 4. Runtime Validation

- [ ] 4.1 Run fresh direct inference checks after mutation for cockpit Luna, fable-5, and Advance.
- [ ] 4.2 Run a fresh `hermes chat -Q --provider moa -m default` smoke session requiring a harmless terminal call; verify session-store evidence of aggregator tool call, tool result, and post-tool response.
- [ ] 4.3 Verify no Hermes source changes are required and the installed virtual-provider path remains the owner of MoA routing.

## 5. OpenSpec Closure

- [ ] 5.1 Run focused strict validation, `openspec show --json`, and task/status checks.
- [ ] 5.2 Archive the change and verify the active directory is absent and the canonical spec exists.
- [ ] 5.3 Run strict main-spec validation, full-store validation with unrelated failures classified, `openspec store doctor`, and `git diff --check`.
- [ ] 5.4 Commit and integrate only owned docs/spec/archive paths; leave unrelated untracked store changes untouched.
- [ ] 5.5 Verify canonical main and origin alignment, clean worktree, archive path, final config, and final `hermes moa list` output.

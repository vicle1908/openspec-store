# repair-knowledge-output-tracking — Design

## Scope

The repair owns only `.gitignore` rules and generated knowledge artifacts in the 17 workspace repositories. Existing source changes and unrelated working-tree changes remain untouched.

## Selective ignore contract

```gitignore
graphify-out/cache/
graphify-out/.graphify_*
!graphify-out/.graphify_labels.json
!graphify-out/.graphify_labels.json.sig
graphify-out/needs_update
graphify-out/.graphify_root
graphify-out/20*/
graphify-out/.rebuild.lock
```

The negations must follow the broad `.graphify_*` rule. `graphify-out/` itself must not be ignored. In go-microservices, repository-wide `graph.json` and `GRAPH_REPORT.md` rules must be removed because they override the intended tracking contract.

## Safety

- `.gitnexus/` remains ignored; it is approximately 1.5GB across the workspace.
- No `.env`, credential, token, key, or source-body artifacts are added.
- Cache, internal state, lock, and dated snapshot directories remain untracked.
- Only the named generated outputs and `.gitignore` files are staged.

## Verification

For each repo:

1. `git check-ignore` confirms cache/internal/snapshot paths remain ignored while label paths are not ignored.
2. `git ls-files` confirms `graphify-out/graph.json`, `GRAPH_REPORT.md`, `manifest.json`, and both label artifacts are tracked.
3. `graphify query` succeeds against the committed graph without rebuilding.
4. `git diff --cached --name-only` is limited to the intended files.

Rollback is limited to reverting the repair commits; no source rollback is required.

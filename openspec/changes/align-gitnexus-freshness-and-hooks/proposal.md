# align-gitnexus-freshness-and-hooks

## Why

GitNexus CLI is at **1.6.9** (latest stable). The package is current but there are three operational issues:

1. **Index staleness across 14/18 repos** — The code-only freshness check used by the weekly cron compares file timestamps, but GitNexus anchors freshness to the exact commit hash in `.gitnexus/gitnexus.json:lastCommit`. After the graphify-out tracking commits, the commit hashes advanced while indexes remained pinned. `gitnexus status` reports 14/18 repos as "stale (re-run gitnexus analyze)".

2. **detect-changes CLI crash** — `gitnexus detect-changes` without `--repo <name>` crashes with `Multiple repositories indexed. Specify which one with the "repo" parameter` because the global registry lists all 18 repos. The pre-commit hook already passes `--repo "$root"` (full path), which is correct. However, agents calling detect-changes from CWD without `--repo` will crash.

3. **Illegal instruction in pre-commit** — The go-microservices pre-commit hook calls `gitnexus detect-changes --scope staged --repo "$root"` and gets `Illegal instruction: 4` on arm64. This is an ONNX native addon issue triggered when the hook process inherits a different CPU feature context.

## What Changes

- Reindex all 14 stale repositories with `gitnexus analyze --index-only --skip-agents-md --skip-skills`
- Add performance mitigation for the pre-commit hook (async background invocation with timeout)
- Update the weekly-graphify-freshness cron prompt to use `gitnexus status` (exact commit comparison) instead of file-mtime comparison
- Verify all 18 repos show "up to date" after reindex

## Impact

- 14 repositories: graph indexes rebuilt (non-destructive, only `.gitnexus/` changes, gitignored)
- Pre-commit hooks: performance improved with async invocation
- Cron: freshness detection becomes accurate
- Risk: Low — reindex is non-destructive; no source code changes

## Evidence

Before:
- `gitnexus status` → 14/18 repos show "⚠️ stale"
- `gitnexus detect-changes` without `--repo` → crash
- Weekly cron code-only check → 18/18 "fresh" (incorrect)

After:
- `gitnexus status` → 18/18 repos show "✅ up to date"
- `gitnexus detect-changes --repo <path>` → works
- Weekly cron → accurate GitNexus freshness check

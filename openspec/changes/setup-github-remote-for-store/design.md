## Architecture

This is a git configuration change only — no application code or OpenSpec
spec/changes structure is modified.

### Steps (using `gh` CLI)

1. **Create repo + add remote + push** (single command)
   ```bash
   gh repo create openspec-store --private --source=. --remote=origin --push
   ```
   This creates the GitHub repo, adds `origin` remote, and pushes `main`.

2. **Update store.yaml**
   Add the `remote` field to `.openspec-store/store.yaml`:
   ```yaml
   version: 1
   id: openspec-store
   remote: git@github.com:<org>/openspec-store.git
   ```

3. **Commit and push store.yaml**
   ```bash
   git -C ~/Developer/openspec-store add .openspec-store/store.yaml
   git -C ~/Developer/openspec-store commit -m "chore: add remote field to store.yaml"
   git -C ~/Developer/openspec-store push
   ```

4. **Verify**
   - `openspec store doctor openspec-store` prints clone URL
   - `openspec store doctor openspec-store --json` shows `remote` non-null
   - `openspec validate --store openspec-store --all --strict` passes

### Format Reference

The `store.yaml` `remote` field format was confirmed via test:
```yaml
remote: git@github.com:test/repo.git
```

This field is read by `openspec store doctor` to print actionable clone
instructions for teammates who don't have the store registered.

## Alternatives

**Skip GitHub, use local-only:** Works for solo development but blocks
team onboarding. The official pattern recommends a remote for stores
used by multiple people.

**Use a different Git host (GitLab, etc.):** The `remote` field accepts
any valid git URL. GitHub is chosen for simplicity but the pattern is
host-agnostic.

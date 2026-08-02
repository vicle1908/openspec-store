## 1. Create GitHub Repository

- [x] 1.1 Run `gh auth status` to confirm authentication
- [x] 1.2 Run `gh repo create openspec-store --private --source=. --remote=origin --push` to create repo, add remote, and push in one step

## 2. Update store.yaml

- [x] 2.1 Add `remote` field to `.openspec-store/store.yaml` with the GitHub clone URL
- [x] 2.2 Verify store.yaml content shows `remote: git@github.com:<org>/openspec-store.git`

## 3. Verify

- [x] 3.1 Run `openspec store doctor openspec-store` — confirm clone URL printed
- [x] 3.2 Run `openspec store doctor openspec-store --json` — confirm `remote` field non-null
- [x] 3.3 Run `openspec validate --store openspec-store --all --strict` — confirm all pass

## 4. Commit and Push

- [x] 4.1 Stage store.yaml: `git -C ~/Developer/openspec-store add .openspec-store/store.yaml`
- [x] 4.2 Commit: `git -C ~/Developer/openspec-store commit -m "chore: add remote field to store.yaml"`
- [x] 4.3 Push: `git -C ~/Developer/openspec-store push`

## Tasks

- [x] 1. Verify ~/Developer/tdt/deployments/ai-review/ is no longer referenced by any running process. `ps aux | grep tdt/deployments/ai-review | grep -v grep` should return nothing.
- [x] 2. Delete shell-artifact files: `rm ~/Developer/--help ~/Developer/yield`
- [x] 3. Delete empty placeholder dirs: `rmdir ~/Developer/deployments ~/Developer/poems-mobile3-android ~/Developer/poems-mobile3-ios`
- [x] 4. Retire ~/Developer/tdt/ (1.1GB): `rm -rf ~/Developer/tdt`. Verify: `ls ~/Developer/tdt` returns "No such file or directory"
- [x] 5. Verify ~/Developer root has no strays: remaining items are real repos, shared dirs (data/, docs/, scripts/, wiki/), or individually-owned files needing review (ntu-keynote, wiki-*, omniroute reviews, workspace-python-template)

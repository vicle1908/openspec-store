# Tasks: Reconcile Maccy v2.7.1 Cross-Mac Setup and Knowledge Synchronization

## 1. Workstation Provisioning Script & Maccy v2.7.1 Convergence

- [x] 1.1 Create `/Users/androidteam/Developer/scripts/maccy-setup.sh` supporting `--check` and `--apply` modes for Homebrew cask `maccy` (`2.7.1`, Team ID `MN3X4648SC`), system TCC `client_type = 0` verification (`kTCCServiceAccessibility=2`, `kTCCServicePostEvent=2`), Login Item registration, and `org.p0deje.Maccy` preference convergence with `<string>...</string>` XML escaping for `ignoreRegexp`.
- [x] 1.2 Execute `/Users/androidteam/Developer/scripts/maccy-setup.sh --apply` and `/Users/androidteam/Developer/scripts/maccy-setup.sh --check`, verifying `plutil -lint` on `~/Library/Containers/org.p0deje.Maccy/Data/Library/Preferences/org.p0deje.Maccy.plist`, `showHexColorSwatch=1`, `showSpecialSymbols=1`, `ignoreRegexp`, and active `Maccy` process state (`PID 34530`).

## 2. LLM Wiki Documentation & Integrity Validation

- [x] 2.1 Create `/Users/androidteam/Developer/wiki/entities/maccy.md` and update `/Users/androidteam/Developer/wiki/index.md` (38 pages) and `/Users/androidteam/Developer/wiki/log.md` (`1d83c53`).
- [x] 2.2 Validate wiki integrity via `python3 /Users/androidteam/Developer/wiki/scripts/wiki-lint.py --root /Users/androidteam/Developer/wiki --today 2026-10-22` (zero findings on `entities/maccy.md`) and `pytest /Users/androidteam/Developer/wiki/tests/test_wiki_lint.py` (`25 passed`).

## 3. Notion Knowledge Hub & AgentMemory Synchronization

- [x] 3.1 Synchronize `wiki/entities/maccy.md` to Notion Knowledge Hub via `/Users/androidteam/Developer/scripts/knowledge-refresh/sync-notion-knowledge.sh --section entities` and verify Notion Page ID `401c4b21-deb4-81e7-a6a6-d7ccd2584b13` via `ntn pages get 401c4b21-deb4-81e7-a6a6-d7ccd2584b13`.
- [x] 3.2 Save Maccy cross-Mac workflow memory (`mem_mvizlvm4_cf584f1c6144`) and `defaults write -array` / `cfprefsd` procedural lesson (`lsn_c6ae9f06d826c533`) in AgentMemory and verify recall via `memory_smart_search`.
- [x] 3.3 Validate OpenSpec change strictly via `openspec validate reconcile-maccy-v271-cross-mac-setup-and-knowledge --strict --json --store openspec-store`.

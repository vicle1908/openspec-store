# Verification Evidence: `reconcile-maccy-v271-cross-mac-setup-and-knowledge`

## 1. Workstation Script & Live Maccy v2.7.1 Verification (Tasks 1.1, 1.2)

- **Script**: `/Users/androidteam/Developer/scripts/maccy-setup.sh`
- **Command**: `/Users/androidteam/Developer/scripts/maccy-setup.sh --apply && /Users/androidteam/Developer/scripts/maccy-setup.sh --check`
- **Output**:
  ```text
  [maccy-setup] Checking Homebrew cask and application bundle...
  [maccy-setup] Installed cask=2.7.1, bundle=2.7.1
  [maccy-setup] Code signature valid (TeamIdentifier=MN3X4648SC).
  [maccy-setup] Checking macOS TCC permissions (org.p0deje.Maccy)...
  [maccy-setup] System TCC grants: kTCCServiceAccessibility=2 kTCCServicePostEvent=2 
  [maccy-setup] Verifying active preferences and process state...
  [maccy-setup] Preferences: historySize=999, searchMode=mixed, pasteByDefault=1, removeFormattingByDefault=1, showHexColorSwatch=1, showSpecialSymbols=1
  [maccy-setup] Process status: RUNNING (PID 34530 )
  [maccy-setup] Maccy workstation verification complete [MODE=check].
  ```

## 2. LLM Wiki Validation (Tasks 2.1, 2.2)

- **Commit**: `1d83c53` in `/Users/androidteam/Developer/wiki` (`docs(wiki): add entities/maccy.md for Maccy v2.7.1 workstation setup`)
- **Pytest Output**:
  ```text
  wiki/tests/test_wiki_lint.py ......................... [100%]
  25 passed in 3.34s
  ```

## 3. Notion Knowledge Hub & AgentMemory Verification (Tasks 3.1, 3.2)

- **Notion Sync (`sync-notion-knowledge.sh --section entities`)**:
  - Created Notion Page ID `401c4b21-deb4-81e7-a6a6-d7ccd2584b13` under section `entities` (`3e0c4b21-deb4-81bd-98e2-e368247f5ebe`).
  - Verified readback via `ntn pages get 401c4b21-deb4-81e7-a6a6-d7ccd2584b13`.
- **AgentMemory Persistence**:
  - Workflow memory ID: `mem_mvizlvm4_cf584f1c6144` (`project: "workstation-toolchain"`).
  - Lesson ID: `lsn_c6ae9f06d826c533` (`confidence: 0.95`, `project: "workstation-toolchain"`).
  - Verified recall via `memory_smart_search` (`score: 0.95` and `score: 0.797`).

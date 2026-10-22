# Proposal: Reconcile Maccy v2.7.1 Cross-Mac Setup and Knowledge Synchronization

## Problem Statement

Maccy (`org.p0deje.Maccy`) was upgraded to `2.7.1` with operator-customized Carbon shortcuts (`Cmd+Shift+C`), plain-text default paste (`removeFormattingByDefault = 1`), unrestricted 8-UTI capture (`ignoredApps = ()`), and `2.7.1` visual enhancements (`showHexColorSwatch`, `showSpecialSymbols`), but lacked an idempotent cross-Mac bootstrap script (`~/Developer/scripts/maccy-setup.sh`), a curated LLM Wiki entity (`~/Developer/wiki/entities/maccy.md`), Notion Knowledge Hub synchronization (`ntn`), and persistent AgentMemory recall.

## What Changes

- **Idempotent Cross-Mac Provisioning Script (`~/Developer/scripts/maccy-setup.sh`)**:
  - Implement `--check` (read-only audit) and `--apply` (convergence) modes for Homebrew cask `maccy` (`2.7.1`, Team ID `MN3X4648SC`), system TCC `client_type = 0` permissions (`kTCCServiceAccessibility = 2`, `kTCCServicePostEvent = 2`), macOS Login Item registration, and sandboxed container preferences (`~/Library/Containers/org.p0deje.Maccy/Data/Library/Preferences/org.p0deje.Maccy.plist`).
  - Handle macOS NextStep plist array parsing by wrapping parenthesized `NSRegularExpression` rules (`(?s)...` and `(?im)...`) in `<string>...</string>` XML tags during `defaults write org.p0deje.Maccy ignoreRegexp -array`, and flush `cfprefsd` after stopping Maccy before relaunch.
- **Maccy v2.7.1 Operator Profile & Visual Enhancements**:
  - Enable `showHexColorSwatch = true` (`1`), `showSpecialSymbols = true` (`1`), `KeyboardShortcuts_togglePreview = {"carbonKeyCode":49,"carbonModifiers":4096}` (`Ctrl+Space`), `KeyboardShortcuts_popup = {"carbonModifiers":768,"carbonKeyCode":8}` (`Cmd+Shift+C`), `removeFormattingByDefault = true` (`1`), `pasteByDefault = true` (`1`), `showRecentCopyInMenuBar = true` (`1`), `clearSystemClipboard = false` (`0`), `ignoredApps = ()`, and all 8 pasteboard UTIs.
- **LLM Wiki, Notion Knowledge Hub & AgentMemory Synchronization**:
  - Create `~/Developer/wiki/entities/maccy.md` and index it in `~/Developer/wiki/index.md` and `~/Developer/wiki/log.md`.
  - Synchronize `wiki/entities/maccy.md` to Notion Knowledge Hub under *Ecosystem Component Entities* (`401c4b21-deb4-81e7-a6a6-d7ccd2584b13`) via `~/Developer/scripts/knowledge-refresh/sync-notion-knowledge.sh --section entities`.
  - Persist detailed setup workflow (`mem_mvizlvm4_cf584f1c6144`) and `defaults write -array` / `cfprefsd` procedural lesson (`lsn_c6ae9f06d826c533`) in AgentMemory.

## Non-Goals

- Synchronizing `~/Library/Containers/org.p0deje.Maccy/Data/Library/Application Support/Maccy/Storage.sqlite` clipboard history payloads across machines.
- Mutating `/Library/Application Support/com.apple.TCC/TCC.db` directly.

## Affected Ownership Boundaries

- **Workstation Scripts (`~/Developer/scripts/maccy-setup.sh`)**: Standalone workstation setup and verification script.
- **Curated Wiki (`~/Developer/wiki/`)**: Owns `entities/maccy.md`, `index.md`, and `log.md`.
- **Notion Knowledge Hub & AgentMemory**: External cloud knowledge mirror (`401c4b21-deb4-81e7-a6a6-d7ccd2584b13`) and local persistent memory (`workstation-toolchain`).
- **OpenSpec Store (`~/Developer/platform/openspec-store`)**: Owns `openspec/specs/maccy-workstation-clipboard-management/spec.md` and this change's planning and verification artifacts.

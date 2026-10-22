# Design: Reconcile Maccy v2.7.1 Cross-Mac Setup and Knowledge Synchronization

## Context

Maccy `2.7.1` (`org.p0deje.Maccy`, Developer ID `Alexey Rodionov (MN3X4648SC)`) runs inside an App Sandbox container at `~/Library/Containers/org.p0deje.Maccy/` with CoreData WAL storage at `Data/Library/Application Support/Maccy/Storage.sqlite` and preferences at `Data/Library/Preferences/org.p0deje.Maccy.plist`. System TCC (`/Library/Application Support/com.apple.TCC/TCC.db`) authorizes `org.p0deje.Maccy` as a bundle identifier (`client_type = 0`) for `kTCCServiceAccessibility = 2` and `kTCCServicePostEvent = 2`.

## Key Decisions

### Decision 1: Standalone Provisioning Script (`~/Developer/scripts/maccy-setup.sh`) with Safe `cfprefsd` Lifecycle
- **Approach**: Provide `--check` and `--apply` modes in `~/Developer/scripts/maccy-setup.sh`. Before running `defaults write org.p0deje.Maccy`, `--apply` terminates `Maccy` (`killall Maccy`), writes all preference keys, flushes `cfprefsd` (`killall cfprefsd`), ensures Login Item registration via `System Events`, and relaunches `/Applications/Maccy.app`.
- **Rationale**: Writing to a sandboxed container plist while the app is running causes Maccy's in-memory `UserDefaults` state to overwrite disk changes on exit.

### Decision 2: XML `<string>...</string>` Escaping for Parenthesized `ignoreRegexp` Array Elements
- **Approach**: Wrap inline-flag regular expressions (`(?s)...` and `(?im)...`) in `<string>...</string>` when calling `defaults write org.p0deje.Maccy ignoreRegexp -array`.
- **Rationale**: macOS `defaults` parses bare `-array` arguments starting with `(` as old-style NextStep property list tuples, failing with `Error: Could not parse: (?s)...`.

### Decision 3: Operator-Confirmed Unrestricted Profile + Maccy 2.7.1 Enhancements
- **Approach**: Configure `KeyboardShortcuts_popup` to `Cmd+Shift+C` (`{"carbonModifiers":768,"carbonKeyCode":8}`), `KeyboardShortcuts_pin` to `Option+P` (`2048`/`35`), `KeyboardShortcuts_delete` to `Option+Backspace` (`2048`/`51`), `KeyboardShortcuts_togglePreview` to `Ctrl+Space` (`4096`/`49`), `removeFormattingByDefault = true`, `pasteByDefault = true`, `showRecentCopyInMenuBar = true`, `clearSystemClipboard = false`, `showHexColorSwatch = true`, `showSpecialSymbols = true`, `ignoredApps = ()`, and all 8 pasteboard UTIs.
- **Rationale**: Matches the operator's multi-Mac muscle memory while enabling Maccy `2.7.1` hex swatch and special-symbol inspection features.

### Decision 4: Three-Tier Knowledge Persistence (Wiki + Notion + AgentMemory)
- **Approach**:
  1. Author `~/Developer/wiki/entities/maccy.md` and link it in `~/Developer/wiki/index.md` and `~/Developer/wiki/log.md`.
  2. Sync to Notion via `~/Developer/scripts/knowledge-refresh/sync-notion-knowledge.sh --section entities` (creating Notion page `401c4b21-deb4-81e7-a6a6-d7ccd2584b13`).
  3. Save workflow memory `mem_mvizlvm4_cf584f1c6144` and lesson `lsn_c6ae9f06d826c533` in AgentMemory.

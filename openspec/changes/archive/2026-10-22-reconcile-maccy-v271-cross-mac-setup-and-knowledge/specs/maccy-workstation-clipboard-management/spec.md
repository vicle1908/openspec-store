# maccy-workstation-clipboard-management Delta Specification

## ADDED Requirements

### Requirement: Maccy 2.7.1 Cross-Mac Reproducible Provisioning and Operator Profile
The workstation SHALL provide an idempotent setup and verification script at `~/Developer/scripts/maccy-setup.sh` (`--check` and `--apply`) for Maccy `2.7.1+` (`org.p0deje.Maccy`, Team ID `MN3X4648SC`). In `--apply` mode, the script MUST stop `Maccy` before writing `org.p0deje.Maccy` defaults, wrap parenthesized `NSRegularExpression` patterns in `<string>...</string>` XML tags, flush `cfprefsd` before relaunching `/Applications/Maccy.app`, and converge the operator profile and Carbon shortcuts.

#### Scenario: Idempotent apply and check convergence succeeds
- **WHEN** the operator runs `~/Developer/scripts/maccy-setup.sh --apply` followed by `~/Developer/scripts/maccy-setup.sh --check`
- **THEN** Homebrew cask `maccy` (`2.7.1+`) and code signature (`TeamIdentifier=MN3X4648SC`) validate cleanly, `plutil -lint` succeeds on `~/Library/Containers/org.p0deje.Maccy/Data/Library/Preferences/org.p0deje.Maccy.plist`, `historySize=999`, `pasteByDefault=true`, `removeFormattingByDefault=true`, `searchMode="mixed"`, `highlightMatch="color"`, `showHexColorSwatch=true`, `showSpecialSymbols=true`, `showRecentCopyInMenuBar=true`, `clearSystemClipboard=false`, `ignoredApps=()`, all 8 pasteboard UTIs, and Carbon shortcuts (`Cmd+Shift+C` popup, `Option+P` pin, `Option+Backspace` delete, `Ctrl+Space` preview) converge with `kTCCServiceAccessibility=2` and `kTCCServicePostEvent=2`

#### Scenario: Parenthesized regex array elements parse without NextStep tuple failure
- **WHEN** `defaults write org.p0deje.Maccy ignoreRegexp -array` is invoked with inline-flag patterns starting with `(` (`(?s)...` and `(?im)...`)
- **THEN** wrapping each pattern in `<string>...</string>` prevents `defaults` from failing with `Could not parse: (?s)...` and writes two valid string elements to `ignoreRegexp`

### Requirement: Ecosystem Knowledge Synchronization across Wiki, Notion, and AgentMemory
The Maccy workstation architecture, TCC `client_type = 0` permission model, Carbon shortcut bitmasks, preference table, and cross-Mac bootstrap procedure SHALL be documented in `~/Developer/wiki/entities/maccy.md` (indexed in `index.md` and `log.md`), synchronized to Notion via `~/Developer/scripts/knowledge-refresh/sync-notion-knowledge.sh --section entities`, and persisted in AgentMemory.

#### Scenario: Wiki validation and Notion synchronization succeed
- **WHEN** `~/Developer/wiki/entities/maccy.md` is added and `sync-notion-knowledge.sh --section entities` runs
- **THEN** `pytest ~/Developer/wiki/tests/test_wiki_lint.py` passes all 25 checks, `entities/maccy.md` has zero lint findings, and `ntn pages get 401c4b21-deb4-81e7-a6a6-d7ccd2584b13` returns the synchronized Markdown page

#### Scenario: AgentMemory recall returns Maccy workflow and lesson
- **WHEN** AgentMemory is queried for `maccy org.p0deje.Maccy defaults write cfprefsd`
- **THEN** both the workflow memory (`mem_mvizlvm4_cf584f1c6144`) and the procedural lesson (`lsn_c6ae9f06d826c533`) are returned for cross-session and cross-Mac bootstrap recall

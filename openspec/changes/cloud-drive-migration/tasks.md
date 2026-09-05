# Tasks: Cloud Drive Migration

- [ ] **Task 1: Move iCloud vds to ~/Developer**
  - Move `~/Library/Mobile Documents/com~apple~CloudDocs/project/vds/` → `~/Developer/vds`
  - Verify: `ls ~/Developer/vds/AGENTS.md` exists
  - Verify: `ls ~/Library/Mobile Documents/com~apple~CloudDocs/project/vds/` fails (not found)

- [ ] **Task 2: Move iCloud microservices to ~/Developer**
  - Move `~/Library/Mobile Documents/com~apple~CloudDocs/project/microservices/` → `~/Developer/microservices`
  - Verify: `ls ~/Developer/microservices/settings.gradle.kts` exists
  - Verify: `ls ~/Library/Mobile Documents/com~apple~CloudDocs/project/microservices/` fails (not found)

- [ ] **Task 3: Delete iCloud build artifacts**
  - Delete from `~/Library/Mobile Documents/com~apple~CloudDocs/`:
    - `compileDebugKotlin/`, `compileKotlin/`, `ksp/`, `sparse/`, `inventory/`, `com 2/`
    - `camunda/`, `camunda7/`, `camunda-async/`, `airbridge/`, `tmz/`
  - Verify: All paths must not exist after deletion

- [ ] **Task 4: Delete Google Drive TDT (1) duplicate**
  - Delete `~/My Drive/TDT (1)/` entirely (2.9G)
  - Verify: `ls ~/My\ Drive/TDT\ \(1\)/` fails (not found)

- [ ] **Task 5: Delete Google Drive VinID**
  - Delete `~/My Drive/VinID/` entirely (2.3G)
  - Verify: `ls ~/My\ Drive/VinID/` fails (not found)

- [ ] **Task 6: Delete code repos from Google Drive tdt/**
  - Delete all code repos from `~/My Drive/tdt/` (keep documentation repos)
  - Keep: `tdt-meta/`, `poems-mobile3-docs/`, `tdt-python-source-package/`, `git-remotes/`, `git-bundles/`, `data/`, `reports/`, `workflow-dag/`, `.md` files, `About This Mac.png`, `Content from Macintosh HD - 2024-02-13.zip`
  - Delete everything else (code repos: mcp-router, jira-skill, agent-core, ai-review, poems-mobile3-ios, poems-mobile3-android, etc.)
  - Verify: `ls ~/My\ Drive/tdt/tdt-meta/` exists
  - Verify: `ls ~/My\ Drive/tdt/mcp-router/` fails (not found)

- [ ] **Task 7: Delete go-microservices-cleanup bundle**
  - Delete `~/Developer/go-microservices-cleanup-20260817.bundle` (1.4G)
  - Verify: `ls ~/Developer/go-microservices-cleanup-20260817.bundle` fails (not found)

- [ ] **Task 8: Clean Desktop migration stubs**
  - Delete from `~/Desktop/`: `android-pmp-connection-center`, `android-pmp-connection-center.zip`, `tdt-documentation-package`, `tdt-documentation-package.zip`, `Desktop - Cuong's iMac`, `Desktop - Cuong's iMac - 1`, `Desktop - iOSTeam Mac Mini`, `tdt-python-source-package`, `PRESENTATION.html`, `untitled`
  - Verify: `ls ~/Desktop/` must not contain any of these items

- [ ] **Task 9: Clean Documents migration stubs**
  - Delete from `~/Documents/`: `Documents - Cuong's iMac`, `Documents - Cuong's iMac - 1`, `Documents - iOSTeam Mac Mini`, `Documents - MacBook Pro`, `Documents - LPP00166151C`, `Documents - LPP00166151C - 1`, `OfferLetter`, `PayslipJoinJuly`, `PSA`, `SoHoKhau`, `AML`, `CaseVic`, `AnyViewer`
  - Verify: `ls ~/Documents/` must not contain any of these items

- [ ] **Task 10: Final verification**
  - Verify all migration targets exist: `~/Developer/vds/`, `~/Developer/microservices/`
  - Verify iCloud clean: `ls ~/Library/Mobile Documents/com~apple~CloudDocs/project/` must NOT contain `vds` or `microservices`
  - Verify Google Drive clean: `~/My Drive/TDT (1)/` gone, `~/My Drive/VinID/` gone, `~/My Drive/tdt/` has only documentation
  - Verify Desktop/Documents clean: no stubs remaining
  - Verify bundle deleted: `~/Developer/go-microservices-cleanup-20260817.bundle` gone
  - Report disk usage before/after

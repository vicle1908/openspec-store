# Tasks: Rule Enhancement 2025

## 1. C7/C8 FP Fixes (Android)

- [x] [historical] 1.1 Add `suppress_c7_child_fragment_manager_safe` post-filter
- [x] [historical] 1.2 Fix C8 pattern: `resources` → `resources\.`
- [x] [historical] 1.3 Enhance C8 lifecycle filter: window 20→30, add onCreateView
- [x] [historical] 1.4 Add unit tests for each filter

## 2. New Android Rules

- [x] [historical] 2.1 Add C10 (viewLifecycleOwner misuse) to crash-runtime.md
- [x] [historical] 2.2 Add C11 (StateFlow lifecycle) to memory-lifecycle.md
- [x] [historical] 2.3 Add post-filters for C10/C11

## 3. New iOS Rules

- [x] [historical] 3.1 Add L7 (NotificationCenter cleanup) to memory-lifecycle.md
- [x] [historical] 3.2 Add L8 ([weak self] in closures) to memory-lifecycle.md
- [x] [historical] 3.3 Add C12 (Swift Task [weak self]) to crash-runtime.md
- [x] [historical] 3.4 Add post-filters for L7/L8

## 4. Validation

- [x] [historical] 4.1 Run full test suite
- [x] [historical] 4.2 Run Android scan: verify total <1000
- [x] [historical] 4.3 Run iOS scan: verify findings >10
- [x] [historical] 4.4 Spot-check 5 known TP preserved
- [x] [historical] 4.5 Spot-check 5 known FP suppressed

## 5. Deploy & Archive

- [x] [historical] 5.1 Sync rules from docs-repo to Android/iOS repos
- [x] [historical] 5.2 Commit all changes
- [x] [historical] 5.3 Rebuild scheduler
- [x] [historical] 5.4 Run live review on MR !23873
- [x] [historical] 5.5 Archive change


---

> **Historical record:** This change was archived with 21 incomplete task(s) (0/21 completed). The remaining tasks were not implemented or were superseded by subsequent changes.

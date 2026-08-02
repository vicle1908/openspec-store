# Tasks: Rule Enhancement 2025

## 1. C7/C8 FP Fixes (Android)

- [ ] 1.1 Add `suppress_c7_child_fragment_manager_safe` post-filter
- [ ] 1.2 Fix C8 pattern: `resources` → `resources\.`
- [ ] 1.3 Enhance C8 lifecycle filter: window 20→30, add onCreateView
- [ ] 1.4 Add unit tests for each filter

## 2. New Android Rules

- [ ] 2.1 Add C10 (viewLifecycleOwner misuse) to crash-runtime.md
- [ ] 2.2 Add C11 (StateFlow lifecycle) to memory-lifecycle.md
- [ ] 2.3 Add post-filters for C10/C11

## 3. New iOS Rules

- [ ] 3.1 Add L7 (NotificationCenter cleanup) to memory-lifecycle.md
- [ ] 3.2 Add L8 ([weak self] in closures) to memory-lifecycle.md
- [ ] 3.3 Add C12 (Swift Task [weak self]) to crash-runtime.md
- [ ] 3.4 Add post-filters for L7/L8

## 4. Validation

- [ ] 4.1 Run full test suite
- [ ] 4.2 Run Android scan: verify total <1000
- [ ] 4.3 Run iOS scan: verify findings >10
- [ ] 4.4 Spot-check 5 known TP preserved
- [ ] 4.5 Spot-check 5 known FP suppressed

## 5. Deploy & Archive

- [ ] 5.1 Sync rules from docs-repo to Android/iOS repos
- [ ] 5.2 Commit all changes
- [ ] 5.3 Rebuild scheduler
- [ ] 5.4 Run live review on MR !23873
- [ ] 5.5 Archive change

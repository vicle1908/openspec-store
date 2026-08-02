# Design: Rule Enhancement 2025

## Context

The code-daily-scan scanner uses ripgrep to match rule patterns against source files, then applies post-filters to suppress known false positives. Current analysis shows 1121 Android findings with estimated 30% FP rate (~336 FPs). The goal is to reduce FPs and add missing rule coverage.

## Decisions

### D-1. C7 childFragmentManager Post-Filter

The C7 rule catches `childFragmentManager` usage after detach. But `childFragmentManager` is safe inside Fragment lifecycle methods where the Fragment is attached.

**New post-filter:** `suppress_c7_child_fragment_manager_safe` reads the file, locates the matched line, and checks if it's inside a lifecycle method scope (onViewCreated, onActivityCreated, etc.). If yes, suppress the finding.

### D-2. C8 resources Pattern Fix

The C8 rule catches `resources` usage after detach. But the current pattern `resources` matches ANY use of the word "resources" in the file, not just `resources.` calls.

**New pattern:** Change from `resources` to `resources\.` (with dot) to only match actual resource access, not variable names or comments containing "resources".

### D-3. C8 Lifecycle Filter Enhancement

Increase the detection window from 20 to 30 lines and add `onCreateView` to the lifecycle method list. This catches more safe usages in Fragment lifecycle.

### D-4. C10 viewLifecycleOwner Rule

New rule that detects `lifecycleScope.launch` without `viewLifecycleOwner` in Fragments. Modern Android should use `viewLifecycleOwner.lifecycleScope.launch` or `repeatOnLifecycle`.

**Pattern:** `lifecycleScope\.launch` (without `viewLifecycleOwner` prefix)
**Category:** Crash (can cause crash after view destruction)
**Priority:** P1

### D-5. C11 StateFlow Lifecycle Awareness Rule

New rule that detects `collect {}` on StateFlow without `repeatOnLifecycle` or `collectAsStateWithLifecycle`. This causes memory leaks and crashes after view destruction.

**Pattern:** `\.collect\s*\{` (without `repeatOnLifecycle` or `collectAsStateWithLifecycle` context)
**Category:** Memory Leak
**Priority:** P1

### D-6. L7 NotificationCenter Rule (iOS)

New rule that detects `NotificationCenter.default.addObserver` without matching `removeObserver` in `deinit`. This causes memory leaks.

**Pattern:** `NotificationCenter\.default\.addObserver` (without `removeObserver` in deinit)
**Category:** Memory Leak
**Priority:** P1

### D-7. L8 weak self Rule (iOS)

New rule that detects escaping closures that capture `self` without `[weak self]`. This causes retain cycles.

**Pattern:** `\{.*\bself\b.*in` (without `[weak self]` prefix)
**Category:** Memory Leak
**Priority:** P0

### D-8. C12 Swift Task Rule (iOS)

New rule that detects `Task { self.` without `[weak self]`. Swift concurrency tasks can outlive the caller.

**Pattern:** `Task\s*\{.*\bself\b` (without `[weak self]`)
**Category:** Crash
**Priority:** P1

## Risks

- **C7 filter**: Some `childFragmentManager` uses in async callbacks might still crash. Mitigation: the filter only suppresses lifecycle-safe contexts.
- **C8 pattern fix**: Changing `resources` to `resources\.` might miss some edge cases. Mitigation: the new pattern is more precise and catches real issues.
- **New rules**: New rules might produce FPs if patterns are too broad. Mitigation: start with conservative patterns and refine based on scan results.

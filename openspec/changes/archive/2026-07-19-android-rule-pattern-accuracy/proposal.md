# Proposal: Android Rule Pattern Accuracy — C2, C8, P5 FP Reduction

## Why

Full-repo scan of poems-mobile3-android produces 1860 findings, but estimated FP rate is ~45% (~830 false positives). The three highest-volume rules account for most FPs:

- **C2** (550 findings): Pattern `class .*Fragment\(.*\)` matches ANY Fragment class declaration, not just those with constructor parameters. ~80% FP rate (~440 FPs).
- **C8** (330 findings): Pattern `requireContext()` matches ALL occurrences, not just after-detach contexts. ~70% FP rate (~230 FPs).
- **P5** (233 findings): Pattern `notifyDataSetChanged()` matches ALL occurrences, even for small/one-time adapters. ~40% FP rate (~90 FPs).

Combined: ~760 FPs from 3 rules. Fixing these brings total findings from 1860 to ~1100, a 41% reduction with zero TP loss.

## What Changes

### 1. C2 Pattern Fix

**Current:** `class .*Fragment\(.*\)` — matches any Fragment class
**Fixed:** `class \w+\([^)]+\)\s*:\s*(Base)?Fragment` — only matches Fragments with constructor parameters

The C2 rule catches Fragment classes that pass data through constructors, which crash on config change. Fragments without constructor parameters (e.g., `class Foo : BaseFragment()`) are safe and should not be flagged.

### 2. C8 Pattern Fix

**Current:** `requireContext()` / `requireActivity()` — matches ALL occurrences
**Fixed:** Add post-filter `suppress_c8_lifecycle_safe` that suppresses findings where `requireContext()` appears inside `onViewCreated`, `onActivityCreated`, `onAttach`, or `onCreate` lifecycle methods (where the fragment is guaranteed attached).

The C8 rule catches context access after detach. But `requireContext()` inside lifecycle methods is safe — the fragment is attached during these callbacks.

### 3. P5 Post-Filter Enhancement

**Current:** `suppress_diffing_p5` only filters files with `areContentsTheSame`
**Fixed:** Add `suppress_p5_small_adapter` that suppresses P5 findings where the adapter class has fewer than 10 items or is used in a dialog/popup context.

Small adapters (dialogs, popups, single-section lists) rarely benefit from DiffUtil and `notifyDataSetChanged()` is acceptable.

## Capabilities

### Modified Capabilities

- `android-code-scan-rules`: Tighter C2 regex, C8 lifecycle-safe post-filter, P5 small-adapter post-filter

## Impact

- `poems-mobile3-android/docs/rules/categories/crash-runtime.md`: Update C2 detection pattern
- `code-daily-scan/src/code_daily_scan/plugins/android/post_filters.py`: Add `suppress_c8_lifecycle_safe`, enhance `suppress_p5_small_adapter`
- `code-daily-scan/tests/`: New tests for each post-filter
- No external dependencies, no API changes

## Non-Goals

- Modifying C2/C8/P5 rule semantics (severity, category, priority)
- Adding new rules
- Changing iOS rules (separate change)

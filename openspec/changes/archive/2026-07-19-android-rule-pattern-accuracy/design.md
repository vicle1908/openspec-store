# Design: Android Rule Pattern Accuracy

## Context

The code-daily-scan scanner uses ripgrep to match rule patterns against source files, then applies post-filters to suppress known false positives. Three rules have patterns that are too broad, producing hundreds of FPs.

## Decisions

### D-1. C2 regex requires constructor parameters

The C2 rule catches Fragment classes that pass data through constructors. The current regex `class .*Fragment\(.*\)` matches ANY Fragment class, including those without parameters.

**New regex:** `class \w+\([^)]+\)\s*:\s*(Base)?Fragment`

This requires at least one parameter in the constructor parentheses. Fragments with empty constructors (e.g., `class Foo : BaseFragment()`) are safe and should not be flagged.

### D-2. C8 post-filter excludes lifecycle-safe contexts

The C8 rule catches `requireContext()` after detach. But `requireContext()` inside lifecycle methods (`onViewCreated`, `onActivityCreated`, `onAttach`, `onCreate`) is safe — the fragment is attached during these callbacks.

**New post-filter:** `suppress_c8_lifecycle_safe` reads the file, locates the matched line, and checks if it's inside a lifecycle method scope. If yes, suppress the finding.

### D-3. P5 post-filter excludes small adapters

The P5 rule catches `notifyDataSetChanged()` without DiffUtil. But small adapters (dialogs, popups, single-section lists) rarely benefit from DiffUtil.

**Enhanced post-filter:** `suppress_p5_small_adapter` checks if the adapter class has fewer than 10 items or is used in a dialog/popup context. If yes, suppress the finding.

## Risks

- **C2 regex change**: Some legitimate C2 findings might be missed if the regex is too strict. Mitigation: the new regex still matches all Fragments with constructor parameters.
- **C8 lifecycle exclusion**: Some `requireContext()` calls in lifecycle methods might still crash if the fragment is detached before the callback completes. Mitigation: lifecycle methods are guaranteed to run while attached.
- **P5 small adapter threshold**: The threshold of 10 items is arbitrary. Mitigation: can be adjusted based on scan results.

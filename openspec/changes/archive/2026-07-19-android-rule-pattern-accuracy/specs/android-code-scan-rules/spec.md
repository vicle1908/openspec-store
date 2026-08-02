# android-code-scan-rules Pattern Accuracy Delta

## ADDED Requirements

### Requirement: C2 rule SHALL only flag Fragments with constructor parameters

The C2 detection pattern SHALL match only Fragment classes that have at least one constructor parameter. Fragment classes with empty constructors (e.g., `class Foo : BaseFragment()`) SHALL NOT be flagged because they are safe — Android can recreate them using the default no-arg constructor.

#### Scenario: Fragment with constructor parameters is flagged

- **WHEN** a Kotlin file contains `class AlertAccountScreen(private var productType: String? = null) : BaseFragment()`
- **THEN** the C2 rule SHALL emit a finding

#### Scenario: Fragment without constructor parameters is NOT flagged

- **WHEN** a Kotlin file contains `class DashBoardScreen : BaseFragment()`
- **THEN** the C2 rule SHALL NOT emit a finding

#### Scenario: DialogFragment with parameters is flagged

- **WHEN** a Kotlin file contains `class MyDialog(data: Bundle) : DialogFragment()`
- **THEN** the C2 rule SHALL emit a finding

### Requirement: C8 rule SHALL suppress findings in lifecycle-safe contexts

The C8 post-filter SHALL suppress `requireContext()` and `requireActivity()` findings when they appear inside Fragment lifecycle methods where the fragment is guaranteed attached: `onViewCreated`, `onActivityCreated`, `onAttach`, `onCreate`, `onStart`, `onResume`.

#### Scenario: requireContext() in onViewCreated is suppressed

- **WHEN** a finding targets `requireContext()` inside `onViewCreated { ... }`
- **THEN** the post-filter SHALL suppress the finding

#### Scenario: requireContext() in async callback is NOT suppressed

- **WHEN** a finding targets `requireContext()` inside a coroutine or callback lambda
- **THEN** the post-filter SHALL NOT suppress the finding

### Requirement: P5 rule SHALL suppress findings for small adapters

The P5 post-filter SHALL suppress `notifyDataSetChanged()` findings when the adapter is used in a dialog, popup, or has fewer than 10 items.

#### Scenario: notifyDataSetChanged in dialog adapter is suppressed

- **WHEN** a finding targets `notifyDataSetChanged()` in an adapter used within a Dialog
- **THEN** the post-filter SHALL suppress the finding

#### Scenario: notifyDataSetChanged in large list adapter is NOT suppressed

- **WHEN** a finding targets `notifyDataSetChanged()` in a RecyclerView adapter with many items
- **THEN** the post-filter SHALL NOT suppress the finding

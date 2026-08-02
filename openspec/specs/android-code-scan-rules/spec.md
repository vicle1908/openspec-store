# android-code-scan-rules Specification

## Purpose
TBD - created by archiving change android-rule-pattern-accuracy. Update Purpose after archive.
## Requirements
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

### Requirement: C7 rule SHALL suppress childFragmentManager in lifecycle-safe contexts

The C7 post-filter SHALL suppress `childFragmentManager` findings when they appear inside Fragment lifecycle methods where the Fragment is attached: `onViewCreated`, `onActivityCreated`, `onAttach`, `onCreate`, `onStart`, `onResume`, `onCreateView`.

#### Scenario: childFragmentManager in onViewCreated is suppressed

- **WHEN** a finding targets `childFragmentManager` inside `onViewCreated { ... }`
- **THEN** the post-filter SHALL suppress the finding

#### Scenario: childFragmentManager in async callback is NOT suppressed

- **WHEN** a finding targets `childFragmentManager` inside a coroutine or callback lambda
- **THEN** the post-filter SHALL NOT suppress the finding

### Requirement: C8 rule SHALL use precise resources pattern

The C8 detection pattern SHALL use `resources\.` (with dot) instead of bare `resources` to only match actual resource access calls, not variable names or comments containing "resources".

#### Scenario: resources.getString is flagged

- **WHEN** a Fragment file contains `resources.getString(R.string.label)`
- **THEN** the C8 rule SHALL emit a finding

#### Scenario: variable named "resources" is NOT flagged

- **WHEN** a file contains `val resources = mutableListOf<String>()`
- **THEN** the C8 rule SHALL NOT emit a finding

### Requirement: C10 rule SHALL detect viewLifecycleOwner misuse

The C10 rule SHALL detect `lifecycleScope.launch` usage in Fragments without `viewLifecycleOwner` prefix. Modern Android should use `viewLifecycleOwner.lifecycleScope.launch` or `repeatOnLifecycle` to ensure lifecycle safety.

#### Scenario: lifecycleScope without viewLifecycleOwner is flagged

- **WHEN** a Fragment contains `lifecycleScope.launch { viewModel.state.collect { ... } }`
- **THEN** the C10 rule SHALL emit a finding

#### Scenario: viewLifecycleOwner.lifecycleScope is NOT flagged

- **WHEN** a Fragment contains `viewLifecycleOwner.lifecycleScope.launch { ... }`
- **THEN** the C10 rule SHALL NOT emit a finding

### Requirement: C11 rule SHALL detect StateFlow without lifecycle awareness

The C11 rule SHALL detect `.collect {}` on StateFlow without `repeatOnLifecycle` or `collectAsStateWithLifecycle`. This causes memory leaks and crashes after view destruction.

#### Scenario: collect without lifecycle awareness is flagged

- **WHEN** a Fragment contains `viewModel.state.collect { updateUI(it) }`
- **THEN** the C11 rule SHALL emit a finding

#### Scenario: repeatOnLifecycle is NOT flagged

- **WHEN** a Fragment contains `repeatOnLifecycle(Lifecycle.State.STARTED) { viewModel.state.collect { ... } }`
- **THEN** the C11 rule SHALL NOT emit a finding

### Requirement: C8 rule SHALL suppress holder.itemView.resources findings

The C8 post-filter SHALL suppress `resources` findings where the access is through a ViewHolder's itemView (`holder.itemView.resources` or `itemView.resources`). This path is safe because the ViewHolder's itemView is always attached when `onBindViewHolder` is called.

#### Scenario: holder.itemView.resources is suppressed

- **WHEN** a C8 finding targets `holder.itemView.resources.getDimensionPixelSize(...)` in an adapter's `onBindViewHolder`
- **THEN** the post-filter SHALL suppress the finding

#### Scenario: requireContext() in Fragment is NOT suppressed

- **WHEN** a C8 finding targets `requireContext()` inside a Fragment method
- **THEN** the post-filter SHALL NOT suppress the finding (handled by lifecycle filter)


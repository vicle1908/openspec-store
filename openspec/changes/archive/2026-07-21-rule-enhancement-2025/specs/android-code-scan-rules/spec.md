# android-code-scan-rules Enhancement Delta

## ADDED Requirements

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

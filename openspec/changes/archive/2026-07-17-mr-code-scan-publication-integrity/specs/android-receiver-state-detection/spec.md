# Android Receiver State Detection Specification

## ADDED Requirements

### Requirement: L-RX-001 SHALL detect registration flag mutated outside a safe registration call

The Android detector SHALL emit `L-RX-001` when a `Boolean` registration-tracking field is assigned `true` outside a safe-call (`?.let { ... }`) or `if (... != null) { ...; flag = true }` block that wraps the matching `ContextCompat.registerReceiver` or `registerReceiver` invocation. The detector MUST NOT flag a field whose surrounding registration call is wrapped in a single safe-call or null-check block.

#### Scenario: Flag set after safe-call registration

- **WHEN** a Kotlin compilation unit contains `mIntentFilter?.let { ContextCompat.registerReceiver(...); isRegistered = true }`
- **THEN** the detector SHALL NOT emit `L-RX-001`

#### Scenario: Flag set outside safe-call registration

- **WHEN** a Kotlin compilation unit contains `mIntentFilter?.let { ContextCompat.registerReceiver(...) }` followed by `isRegistered = true` outside the safe-call block
- **THEN** the detector SHALL emit `[critical] L-RX-001 <file>:<line> - Registration flag set after a nullable registration input short-circuited the call`

### Requirement: L-RX-002 SHALL detect swallowed unregister exceptions

The Android detector SHALL emit `L-RX-002` when `unregisterReceiver` or `ContextCompat.unregisterReceiver` is wrapped in `runCatching { ... }` or `try { ... } catch (_: ...) { }` and the surrounding code clears the registration flag regardless of the outcome.

#### Scenario: Swallowed unregister clears flag

- **WHEN** a Kotlin compilation unit contains `runCatching { unregisterReceiver(receiver) }` followed by `isRegistered = false` outside any conditional branch
- **THEN** the detector SHALL emit `[critical] L-RX-002 <file>:<line> - Unregister failure swallowed while registration flag is cleared`

#### Scenario: Unregister exception propagates

- **WHEN** a Kotlin compilation unit contains `try { unregisterReceiver(receiver) } catch (e: IllegalArgumentException) { ... }` and the registration flag is only cleared inside the success path
- **THEN** the detector SHALL NOT emit `L-RX-002`

### Requirement: L-RX rules SHALL scope to files with paired register and unregister calls

The detector SHALL limit `L-RX-001` and `L-RX-002` to compilation units that contain both a `registerReceiver` (or `ContextCompat.registerReceiver`) call and a paired `unregisterReceiver` call. Files without a paired unregister call SHALL NOT receive `L-RX` findings.

#### Scenario: Single registration without unregister

- **WHEN** a Kotlin compilation unit contains `ContextCompat.registerReceiver(...)` but no `unregisterReceiver` call
- **THEN** the detector SHALL NOT emit any `L-RX` finding

#### Scenario: Paired register and unregister

- **WHEN** a Kotlin compilation unit contains both `ContextCompat.registerReceiver(...)` and `unregisterReceiver(...)`
- **THEN** the detector MAY emit `L-RX-001` or `L-RX-002` findings if the other criteria are met

### Requirement: L-RX rules SHALL preserve legitimate lifecycle patterns

The detector SHALL NOT flag:

- `onStart` registration paired with `onStop` unregistration when the registration flag is updated only after a successful registration path.
- A `BroadcastReceiver` declared as a non-null `object` expression or `val`.
- A thrown `registerReceiver` invocation, because control flow exits before subsequent assignments can execute.

#### Scenario: Valid onStart and onStop pairing

- **WHEN** a Kotlin compilation unit registers inside `onStart` and unregisters inside `onStop` with the registration flag updated only after a successful registration
- **THEN** the detector SHALL NOT emit `L-RX` findings

#### Scenario: Non-null receiver declaration

- **WHEN** a Kotlin compilation unit declares the receiver as `private val mReceiver: BroadcastReceiver = object : BroadcastReceiver() { ... }`
- **THEN** the detector SHALL NOT emit an `L-RX` nullability finding

### Requirement: L-RX findings SHALL use the FindingParser markdown format

Each `L-RX` finding SHALL be serialized as `- [critical] L-RX-<n> <file_path>:<line> - <message>` to remain compatible with the existing FindingParser contract used by `mr-code-scan-reviewer`.

#### Scenario: Finding serialisation format

- **WHEN** the Android detector emits `L-RX-001` for a registration flag mutation outside a safe-call
- **THEN** the finding SHALL be serialised as `- [critical] L-RX-001 <file_path>:<line> - <message>`
- **AND** the severity SHALL remain `critical` to align with the existing code-scan severity mapping

## ADDED Requirements

### Requirement: Default verification loop is open -> snapshot -i -> act -> verify -> close
The agent SHALL use the canonical default loop: `open -> snapshot -i -> get/is/find or press/fill/scroll/wait -> verify -> close` for all device verification tasks. The loop name is taken verbatim from the official `callstack/agent-device` bundled `SKILL.md` and is the agent-facing source of truth for the verify-loop family. The agent SHALL always close before the final response.

#### Scenario: Agent verifies a screen change on iOS Simulator
- **WHEN** the agent needs to verify POEMS Mobile 3 on iOS Simulator
- **THEN** the agent runs `agent-device open <app> --platform ios`, then `agent-device snapshot -i`, then interaction commands using current refs, then `agent-device close` — in that order

#### Scenario: Off-screen interactive content requires scrolling
- **WHEN** the agent's target element does not appear in the current snapshot output
- **THEN** the agent SHALL run `agent-device scroll <direction> <amount>` (e.g., `agent-device scroll down 0.5`) or `agent-device scroll down --pixels 320`, then take a fresh `agent-device snapshot -i` before targeting the element
- **AND** the agent MUST NOT use refs from a previous snapshot after scrolling

#### Scenario: Stable multi-screen scroll loop (no infinite loop)
- **WHEN** the agent is searching for an element that may be several screens down
- **THEN** the agent uses the canonical stable loop from `agent-device help workflow`: capture snapshot, grep for the target label, break on match; otherwise compare to the previous snapshot and break when duplicate; otherwise scroll down once. This avoids infinite loops when the target is unreachable.

#### Scenario: React Native warning overlay visible
- **WHEN** the agent opens a React Native app and a warning or error overlay is visible
- **THEN** the agent SHALL dismiss the overlay and continue, but report the overlay in the verification summary if it was not the expected behavior (per official `quick-start`)

#### Scenario: Use `diff snapshot` to validate structural changes
- **WHEN** the agent needs to validate structural changes between mutations with lower output volume
- **THEN** the agent runs `agent-device diff snapshot` (canonical) or `agent-device snapshot --diff` (alias) and reads the unified-style `+`/`-` lines; the first call initializes baseline, subsequent calls return deltas and update baseline

### Requirement: Current refs for exploration; selectors for durable replay
The agent SHALL use current `@eN` refs returned by the latest snapshot for one-shot exploration, and selector expressions (role/label/text/value/id) for durable replay scripts. Refs are visible-first and immediately actionable; after scrolling or changing screens, take a fresh snapshot.

#### Scenario: One-shot exploration
- **WHEN** the agent is investigating UI state interactively
- **THEN** the agent MAY use refs like `@e3` and `@e7` from the latest `snapshot -i` output

#### Scenario: Writing a replay script
- **WHEN** the agent is recording a `.ad` replay script that will be run again
- **THEN** the agent SHALL use selector expressions such as `[label="Sign In"]` or `role=button label="Continue"` instead of refs

#### Scenario: `find` for human-readable targeting without refs
- **WHEN** the agent prefers a verb-arg form for targeting (e.g., not yet familiar with snapshot refs)
- **THEN** the agent uses `agent-device find "Sign In" click`, `agent-device find label "Email" fill "user@example.com"`, or `agent-device find role button click`

### Requirement: Every open is matched with a close (or close --shutdown)
The agent SHALL run `agent-device close` with the same `--session`, `--platform`, `--udid`, `--serial`, and `--state-dir` flags used in `open` before finishing its turn. The agent SHALL use `agent-device close --shutdown` to also shut down the Apple simulator or Android emulator (the preferred end-of-run pattern in CI/multi-tenant workloads).

#### Scenario: Successful verification completed
- **WHEN** the agent finishes verification on a device
- **THEN** the agent runs `agent-device close` (or `agent-device close --shutdown` to release the simulator/emulator) with the original flags before the final response

#### Scenario: Verification fails with an error
- **WHEN** the agent encounters an error during verification
- **THEN** the agent SHALL attempt `agent-device close` with the original flags; if cleanup is impossible, the agent reports the remaining session name, state dir, runner-log path, request-log path, and process IDs as a blocker (matching the upstream `Manual Device Session Hygiene` rule)

#### Scenario: Agent abandons verification mid-loop
- **WHEN** the agent must stop verification before completion
- **THEN** the agent still attempts `agent-device close` with the original flags; if that fails, the agent reports the unclosed session as a blocker

### Requirement: Mutating commands are serial per session
The agent SHALL NOT issue parallel mutating commands against the same session. All `fill`, `click`, `swipe`, `press`, `type`, `scroll`, `back`, `alert`, `replay`, `batch`, and `close` commands SHALL be issued serially against the same session (per the official `sessions.md` "Do not parallelize mutating commands against the same session" rule).

#### Scenario: Agent needs two taps for verification
- **WHEN** the agent needs to tap two elements in sequence
- **THEN** the agent issues the first command, waits for the response, takes a fresh snapshot, then issues the second command — not both at once

### Requirement: `is` predicate set is the full set
The agent SHALL use only the documented `is` predicates: `visible | hidden | exists | editable | selected | text`. `is` does not accept `@ref`; the agent SHALL use a selector expression instead. `is` exits non-zero on failure.

#### Scenario: Agent asserts an element is hidden before continuing
- **WHEN** the agent needs to wait until a loading state disappears
- **THEN** the agent runs `agent-device is hidden 'text="Loading..."'` (predicate `hidden`, selector expression, no `@ref`)

#### Scenario: Agent asserts exact text content
- **WHEN** the agent needs to verify a heading matches an expected string
- **THEN** the agent runs `agent-device is text 'id="greeting"' "Welcome back"` (predicate `text`, selector, expected value)

### Requirement: `back` flag selection respects platform semantics
The agent SHALL use `agent-device back` (default app-owned back) for in-app back navigation. The agent SHALL use `agent-device back --in-app` as an explicit alias for the default. The agent SHALL use `agent-device back --system` only when system back input is explicitly required. On macOS, `back --system` reports `UNSUPPORTED_OPERATION`; the agent SHALL surface this and SHALL NOT fall back to system navigation.

#### Scenario: iOS app-owned back
- **WHEN** the agent needs to navigate back in-app on iOS or Android
- **THEN** the agent runs `agent-device back` (or `agent-device back --in-app`)

#### Scenario: macOS system back not available
- **WHEN** the agent runs `agent-device back --system --platform macos`
- **THEN** the agent receives an `UNSUPPORTED_OPERATION` error and reports it; the agent SHALL NOT fall back to in-app back unless the operator explicitly requests it

### Requirement: Alert handling respects the snapshot-derived fallback
The agent SHALL inspect for system alerts via `agent-device alert get` (cheap immediate check) or `agent-device alert wait <short-ms>` (when a prompt may appear after async work). If `alert` reports no alert but a sheet is visible in `snapshot` or `screenshot`, the agent treats it as app-owned UI and uses `agent-device snapshot -i -s "<visible label>"` then `agent-device press @ref`. The agent SHALL NOT use `settings permission` to answer a dialog that is already on screen; `settings permission` is reserved for setup or for resetting permission state before a flow.

#### Scenario: iOS permission sheet is visible but `alert` reports no alert
- **WHEN** `agent-device snapshot` or `screenshot` shows a visible iOS permission sheet but `agent-device alert accept` reports no alert
- **THEN** the agent falls back to `agent-device snapshot -i -s "<visible label>"` then `agent-device press @ref` against the snapshot ref (per official `commands.md` "not every simulator permission surface is exposed as a native XCTest alert")

### Requirement: Version-matched help is consulted before planning
The agent SHALL read `agent-device help workflow` before planning any non-trivial device command. The agent SHALL read `agent-device help debugging` for runtime failures, `agent-device help react-native` and `agent-device help react-devtools` for React Native workflows, `agent-device help macos` for desktop targets, `agent-device help remote` for cloud/remote workflows, `agent-device help dogfood` for exploratory QA, and `agent-device help physical-device` for iOS physical device setup. The agent SHALL NOT assume command shapes from a previous session or from the OpenSpec when the installed CLI version may differ.

#### Scenario: Agent plans a batch workflow
- **WHEN** the agent needs to run multiple commands in a batch
- **THEN** the agent consults `agent-device help workflow` and `agent-device help` to confirm the current CLI version's command surface

#### Scenario: Agent uses the react-devtools help
- **WHEN** the agent needs React Native component internals
- **THEN** the agent consults `agent-device help react-devtools` before running the `react-devtools` subcommands

#### Scenario: Agent targets macOS desktop
- **WHEN** the agent needs to drive a macOS app or desktop surface
- **THEN** the agent consults `agent-device help macos` before running `--platform macos` commands; macOS has a much smaller supported command set than iOS/Android (no `boot`, `shutdown`, `home`, `rotate`, `app-switcher`, `install`, `reinstall`, `install-from-source`, `push`)

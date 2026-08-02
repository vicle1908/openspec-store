## ADDED Requirements

### Requirement: Skill is a thin router; spec is the documentation layer
The TDT OpenSpec documents the command surface, but the installed `agent-device` SKILL.md MUST stay a thin router (per callstack/agent-device AGENTS.md: "Keep `skills/**/SKILL.md` focused on when to use the skill, version gating, which `agent-device help <topic>` page to read, and a short default loop. Do not duplicate full CLI manuals in skills."). The agent SHALL consult `agent-device help <topic>` for exact syntax; the spec captures usage patterns and TDT-specific guardrails.

#### Scenario: Agent plans a non-trivial command
- **WHEN** the agent needs exact command syntax
- **THEN** the agent SHALL run `agent-device help <topic>` (e.g., `agent-device help workflow`, `agent-device help debugging`, `agent-device help react-devtools`, `agent-device help react-native`, `agent-device help macos`, `agent-device help remote`, `agent-device help dogfood`, `agent-device help physical-device`) before planning
- **AND** the agent SHALL NOT copy command shapes from the OpenSpec into its plan without re-reading the version-matched help

### Requirement: Navigation commands (boot, open, close, back, home, rotate, app-switcher, shutdown)
The agent SHALL use the navigation command group for device lifecycle. `boot` is mainly needed when `open` fails because no booted simulator/emulator is available. `shutdown` MUST NOT target an active session device; use `close --shutdown` instead. `back` defaults to app-owned back navigation; `back --in-app` is an explicit alias; `back --system` asks for system back input. `rotate` is supported only on iOS and Android mobile targets (not macOS or tvOS). `--platform apple` is an alias for `ios`/`tvOS`/`macOS`; `--target mobile|tv|desktop` selects phone/tablet vs TV vs desktop. On iOS devices, `http(s)://` URLs open in Safari when no app is active; custom-scheme URLs require an active app in the session.

#### Scenario: No booted device available before open
- **WHEN** `agent-device open <app>` fails because no booted simulator or emulator is available
- **THEN** the agent runs `agent-device boot --platform ios|android [--device <avd-name>] [--headless]` to ready the target, then retries `open`

#### Scenario: Shutting down a device after verification
- **WHEN** the agent finishes verification and wants to release the simulator/emulator
- **THEN** the agent runs `agent-device close --shutdown` (preferred, also closes the session) or `agent-device shutdown --platform ios|android --device <avd-name>` (without closing an active session)

#### Scenario: Device orientation change
- **WHEN** the agent needs to test landscape orientation
- **THEN** the agent runs `agent-device rotate landscape-left`; macOS and tvOS do not expose `rotate`

#### Scenario: App-owned back vs system back on iOS
- **WHEN** the agent needs to go back in-app on iOS
- **THEN** the agent uses `agent-device back` (default) or `agent-device back --in-app`; on iOS these only tap visible app back UI
- **AND** when the agent explicitly wants the system back (edge-swipe on iOS, normal back keyevent on Android), it uses `agent-device back --system`
- **AND** on macOS, `back --system` reports `UNSUPPORTED_OPERATION` (no generic system back input) — the agent reports this and does not fall back to system navigation

#### Scenario: Open with deep link
- **WHEN** the agent needs to open a deep link in an app on iOS or Android
- **THEN** the agent runs `agent-device open MyApp myapp://screen/to --platform ios` or `agent-device open com.example.myapp "https://example.com" --platform android`

### Requirement: Interaction commands (click, fill, type, press, swipe, scroll, gesture, longpress, focus, find)
The agent SHALL use the interaction command group for UI operations. `fill` clears then types; `type` does not clear (and does not accept `@ref` — use `fill @ref "text"` to target a field directly, or `press @ref` then `type "text"` to append in the focused field). On Android, `fill` verifies text and treats IME-owned capture as a terminal failure instead of retrying against the wrong field. `swipe` accepts an optional `durationMs` (default 250ms, range 16..10000; iOS clamped to 16..60ms to avoid longpress side effects). `gesture transform` is supported on Android and iOS simulator app sessions (iOS uses private XCTest synthesis). `find` uses a human-readable verb-arg form (`find "Sign In" click`, `find label "Email" fill "user@example.com"`, `find role button click`).

#### Scenario: Login form entry
- **WHEN** the agent fills in an email field
- **THEN** the agent runs `agent-device fill @e3 "user@example.com"`; on Android the command also verifies text and treats IME-owned capture as a terminal failure

#### Scenario: Appending text without clearing
- **WHEN** the agent needs to type into an already-focused field without overwriting existing text
- **THEN** the agent runs `agent-device type " more text"` (no `@ref`); for a targeted append the agent runs `agent-device press @e3` then `agent-device type " more text"`

#### Scenario: Off-screen interactive content requires scrolling
- **WHEN** the agent's target element does not appear in the current snapshot output
- **THEN** the agent runs `agent-device scroll <direction> <amount>` (e.g., `agent-device scroll down 0.5`) or `agent-device scroll down --pixels 320` (fixed distance), then takes a fresh `agent-device snapshot -i`; the agent MUST NOT use refs from a previous snapshot after scrolling

#### Scenario: Stable scroll loop pattern (no infinite loop)
- **WHEN** the agent is looking for an element that may be several screens down
- **THEN** the agent uses the documented stable loop: capture snapshot, grep for target, break on match or on duplicate-snapshot (no change) condition; otherwise scroll down once. This avoids infinite loops and is the canonical pattern from the official `agent-device help workflow`.

#### Scenario: React Native warning overlay visible
- **WHEN** the agent opens a React Native app and a warning or error overlay is visible
- **THEN** the agent SHALL dismiss the overlay and continue, but report the overlay in the verification summary if it was not the expected behavior (per official `quick-start`)

### Requirement: Inspection commands (snapshot, diff snapshot, get, is, find, wait, alert)
The agent SHALL use `snapshot -i` to get interactive element refs, `diff snapshot` to compare with the previous session baseline and update baseline, `get text @ref` / `get attrs @ref` to extract content, `is <predicate> <selector>` to evaluate assertions, `find` for semantic targeting, `wait` for synchronization, and `alert` for system alerts. `snapshot --diff` is an alias for `diff snapshot`; `diff snapshot` is the canonical exploration form. `is` predicates are `visible | hidden | exists | editable | selected | text`. `is` does not accept `@ref`; use a selector expression instead. `is` exits non-zero on failure. Default snapshot text is an agent-facing, token-efficient, visible-first view; use `snapshot --raw` or `snapshot --json` for the full provider tree.

#### Scenario: Getting element text content
- **WHEN** the agent needs the text inside a specific element
- **THEN** the agent runs `agent-device get text @e1` or `agent-device get attrs @e1` for all attributes

#### Scenario: Asserting UI state with the full predicate set
- **WHEN** the agent needs to assert visibility, presence, editability, selection, or text content
- **THEN** the agent runs one of:
  - `agent-device is visible 'role="button" label="Submit"'`
  - `agent-device is exists 'id="primary-cta"'`
  - `agent-device is hidden 'text="Loading..."'`
  - `agent-device is editable 'id="email"'`
  - `agent-device is selected 'label="Wi-Fi"'`
  - `agent-device is text 'id="greeting"' "Welcome back"`
- **AND** `is` exits non-zero on failure; `is` does not accept `@ref`; the agent uses selector expressions instead

#### Scenario: Waiting for an element to appear
- **WHEN** the agent has submitted a form and needs to wait for the next screen
- **THEN** the agent runs `agent-device wait 'label="Dashboard"' 5000` (selector, optional timeout in ms) or `agent-device wait 1500` (ms duration) or `agent-device wait @e12` (ref resolves to text, then polls)
- **AND** the agent notes that `wait @ref` is text-based after resolution (duplicate labels can match a different element than the original ref target)

#### Scenario: System alert appears mid-flow
- **WHEN** the agent detects a system alert (iOS simulator permission sheet, macOS desktop dialog, Android native/runtime permission dialog) via `agent-device alert get` or `agent-device alert wait <short-ms>`
- **THEN** the agent handles it via `agent-device alert accept` or `agent-device alert dismiss`
- **AND** if `alert` reports no alert but a sheet is visible in `snapshot` or `screenshot` (e.g., not every iOS simulator permission surface is exposed as a native XCTest alert), the agent falls back to `agent-device snapshot -i -s "<visible label>"` then `agent-device press @ref` against the snapshot ref

#### Scenario: Discover app identifier before open
- **WHEN** the agent does not know the exact app id or package name
- **THEN** the agent runs `agent-device apps --platform ios|android` (use `--all` for the full inventory including system/OEM apps) to discover identifiers before `open`
- **AND** for Android, the agent may also use `agent-device appstate` to confirm the live foreground package/activity

### Requirement: Evidence capture commands (screenshot, diff screenshot, record, logs, network, perf, trace, debug symbols)
The agent SHALL capture evidence only when it adds value. The agent MUST consult `agent-device help debugging` for the full evidence-capture workflow before debugging any failure. `screenshot --max-size <px>` preserves aspect ratio and only downscales when the saved PNG's longest edge is larger than the requested size (use to keep artifacts agent-friendly). `screenshot --overlay-refs` captures a fresh full snapshot and burns visible `@eN` refs plus their target rectangles into the saved PNG. `diff screenshot --baseline <path> [--current <path>] --out <diff.png>` compares screenshots and writes a diff PNG with changed regions; if `tesseract` is installed, OCR text deltas and best-effort non-text visual deltas are added as hints. `record` always produces a video artifact; iOS simulator uses native `simctl io ... recordVideo`; physical iOS device recording is runner-based, defaults to 15 FPS, and requires an active app session context (`open <app>` first). `logs` is off by default in normal flows; enable on demand for debugging. `logs clear --restart` is the preferred debug entrypoint for clean-window repro loops.

#### Scenario: User requests a screenshot
- **WHEN** the user asks for a screenshot of the current screen
- **THEN** the agent runs `agent-device screenshot ./artifacts/<name>.png [--max-size 1024] [--overlay-refs]` and includes the path in the response

#### Scenario: Screenshot with visible refs overlay
- **WHEN** the user wants a screenshot with element refs drawn on it
- **THEN** the agent runs `agent-device screenshot ./artifacts/<name>.png --overlay-refs` which burns `@eN` refs and target rectangles into the PNG; the agent uses `--max-size 1024` when refs/text must remain readable on a downscaled artifact

#### Scenario: Visual regression check between two screenshots
- **WHEN** the agent needs to detect pixel-level changes between a baseline screenshot and the current state
- **THEN** the agent runs `agent-device diff screenshot --baseline ./baseline.png --out ./diff.png [--overlay-refs]`; with `tesseract` installed, OCR text deltas and best-effort non-text visual deltas are also reported

#### Scenario: Debugging a runtime failure
- **WHEN** an interaction takes longer than expected or fails
- **THEN** the agent runs `agent-device help debugging` first, then follows the evidence-capture workflow: `agent-device logs clear --restart`, reproduce the issue, then `agent-device logs path` to get the log file path, then `grep -n -E "Error|Exception|Fatal|crash" <log-path>` to surface only matching lines into context

#### Scenario: Network evidence for an API call
- **WHEN** the agent needs to inspect recent HTTP traffic for the session app
- **THEN** the agent runs `agent-device network dump 25` (default summary) or `agent-device network dump 25 --include all` (parsed headers/body, truncated) to surface recent HTTP(s) entries from `app.log`

#### Scenario: Performance investigation — frame health, memory, CPU
- **WHEN** the agent needs to diagnose slow screen transitions, memory growth, or hot CPU
- **THEN** the agent runs `agent-device perf frames --json` for FPS/dropped-frame data (Android resets frame stats after each read), `agent-device perf memory sample --json` for compact memory snapshot, and `agent-device perf memory snapshot --kind android-hprof --out app.hprof` (Android) or `--kind memgraph --out app.memgraph` (iOS sim/macOS) for a heap/memgraph artifact path
- **AND** for native CPU profile, the agent runs `agent-device perf cpu profile start --kind xctrace --template "Time Profiler" --out app.trace` then `... stop` then `... report` (iOS sim/device/macOS) or `agent-device perf cpu profile start --kind simpleperf --out cpu.perf.data` (Android)
- **AND** native profile/trace outputs are compact agent evidence: state, artifact path, size, method — raw `.perf.data` / `.perfetto-trace` / `.trace` contents stay on disk

#### Scenario: Trace capture (Animation Hitches or Perfetto)
- **WHEN** the agent needs lower-level session diagnostics than `record` or `logs`
- **THEN** the agent runs `agent-device trace start [path]` then `agent-device trace stop [path]` (xctrace on Apple, perfetto on Android) and inspects the artifact in Instruments/Xcode or via perfetto UI

#### Scenario: Crash symbolication
- **WHEN** the agent has a local Apple crash artifact (`crash.log` or `crash.ips`) and matching dSYMs
- **THEN** the agent runs `agent-device debug symbols --artifact <crash-path> --dsym <dSYM-path> --out <symbolicated-path>` and reads the compact crash report (app/thread, exception/termination, top symbolicated frames, first actionable frame finding) without loading the full crash body

### Requirement: App install and reinstall commands (install, reinstall, install-from-source)
The agent SHALL use `install <app> <path>` for in-place binary updates (keeps existing app data when supported by the platform), `reinstall <app> <path>` for fresh-state (uninstall + install) — useful for login/logout reset and deterministic test setup — and `install-from-source <url>` for artifacts that already exist at a URL reachable by the daemon. Supported binary formats: Android `.apk`/`.aab`, iOS `.app`/`.ipa`. `.aab` requires `bundletool` in `PATH` or `AGENT_DEVICE_BUNDLETOOL_JAR` with `java` in `PATH`. `.ipa` uses `<app>` as the bundle id/name hint when multiple `Payload/*.app` bundles are present. For GitHub Actions artifacts, the agent uses `install-from-source --github-actions-artifact <owner/repo:artifact>` against a compatible remote daemon that can resolve with its own credentials.

#### Scenario: Installing a debug APK on Android
- **WHEN** the agent has a local `.apk` and wants to install it on an emulator
- **THEN** the agent runs `agent-device install com.example.app ./build/app-debug.apk --platform android`

#### Scenario: Fresh-state install for a login test
- **WHEN** the agent needs a clean-state app for a login test
- **THEN** the agent runs `agent-device reinstall com.example.app ./build/app-debug.apk --platform android` which uninstalls and reinstalls

#### Scenario: Install from a remote artifact URL
- **WHEN** the agent has a URL for a remote artifact (e.g., a CI-built APK)
- **THEN** the agent runs `agent-device install-from-source https://example.com/builds/app.apk --platform android`; for GitHub Actions artifacts the agent uses `agent-device install-from-source --github-actions-artifact thymikee/RNCLI83:6635342232 --platform android`

### Requirement: Replay, test, batch, and Maestro compatibility
The agent SHALL use `replay` for deterministic `.ad` scripts and `test` for serial suite execution. `replay -u` updates stale selectors in place. `test --platform` filters suite files by `context platform=...` metadata; it does NOT override the script target. `test --timeout` and `test --retries` are per-script attempt; retries are capped at 3. By default, suite artifacts are written under `.agent-device/test-artifacts/<run-id>/...`. `.ad` scripts support `${VAR}` substitution with precedence: CLI `-e KEY=VALUE` (highest) → shell `AD_VAR_*` → script `env KEY=VALUE` → built-ins (`AD_PLATFORM`, `AD_SESSION`, `AD_FILENAME`, `AD_DEVICE`, `AD_ARTIFACTS`). `batch` runs a JSON array of steps in a single daemon request; use `--max-steps <n>` to tighten per-request safety limits. Agent Device can run a supported subset of Maestro YAML through `replay` / `test --maestro`; the supported subset is documented in `https://github.com/callstack/agent-device/issues/558` (Agent Device tracks parity as an explicit compatibility gap). `replay export` transforms a `.ad` flow to Maestro YAML for handoff to a Maestro runner.

#### Scenario: Replaying a recorded session
- **WHEN** the agent needs to replay a previously recorded `.ad` script
- **THEN** the agent runs `agent-device replay ./session.ad`

#### Scenario: Running a test suite
- **WHEN** the agent runs an E2E test suite
- **THEN** the agent runs `agent-device test ./suite [--platform ios|android] [--timeout 60000] [--retries 1] [--artifacts-dir ./artifacts]`
- **AND** the agent notes that `--platform` filters by `context platform=...` metadata, it does NOT override the script target

#### Scenario: Recording a replay script
- **WHEN** the agent wants to record a deterministic replay script during an interactive session
- **THEN** the agent opens with `agent-device open Settings --platform ios --session e2e --save-script [path]`, runs `snapshot -i` and `click @e..` interactively, then `agent-device close` writes the `.ad` script to `~/.agent-device/sessions/<session>-<timestamp>.ad` (or to the custom path)

#### Scenario: Batching a known short sequence
- **WHEN** the agent already knows a short sequence of actions
- **THEN** the agent uses `agent-device batch --platform ios --steps-file /tmp/batch-steps.json --json` (or `--steps '<json>'` inline) instead of running each command serially. Stop-on-first-error is the supported behavior. Use `--max-steps <n>` to tighten per-request safety limits.

#### Scenario: Exporting a .ad script to Maestro YAML
- **WHEN** the agent needs to hand a recorded Agent Device flow to a Maestro runner
- **THEN** the agent runs `agent-device replay export ./workflows/checkout.ad --format maestro --out ./maestro/checkout.yaml`; this is a local file transform that does not start the daemon or contact a device

### Requirement: Settings and permission helpers (settings, clear-app-state, biometric simulation)
The agent SHALL use `settings` commands for device-level configuration. iOS `settings` are simulator-only except `settings appearance` and the macOS permission subset. macOS supports only `settings appearance <light|dark|toggle>` and `settings permission <grant|reset> <accessibility|screen-recording|input-monitoring>`. macOS does not support `settings deny`. Android `settings animations off|on` toggles global `window_animation_scale`, `transition_animation_scale`, `animator_duration_scale` (use as an opt-in stabilizer; restore with `on` after the run). `settings clear-app-state [app-id]` clears active session app data (Android uses `pm clear`; iOS simulator removes the data container; iOS physical devices and macOS are unsupported). `settings faceid` / `touchid` are iOS simulator-only; `settings fingerprint` is Android-only (where `cmd fingerprint` or `adb emu finger` is available).

#### Scenario: Granting camera permission before a test
- **WHEN** the agent needs the app to have camera permission for a test
- **THEN** the agent runs `agent-device settings permission grant camera --platform ios` or `agent-device settings permission grant camera --platform android`

#### Scenario: Disabling animations for stable automation
- **WHEN** the agent needs deterministic timing for a scroll or gesture test
- **THEN** the agent runs `agent-device settings animations off --platform android` to disable system animations, runs the test, then `agent-device settings animations on` to restore

#### Scenario: Biometric simulation (Face ID, Touch ID, Android fingerprint)
- **WHEN** the agent needs to simulate biometric authentication
- **THEN** the agent runs `agent-device settings faceid match` (iOS sim), `agent-device settings touchid match` (iOS sim), or `agent-device settings fingerprint match` (Android emulator/device where supported) to simulate a valid outcome; use `nonmatch` for invalid; `enroll` / `unenroll` to set up state

### Requirement: React Native helpers (react-devtools, metro reload)
The agent SHALL use `react-devtools` for component tree introspection, prop/state/hook analysis, and profiling (the helper dynamically runs pinned `agent-react-devtools@0.4.0` through npm and passes arguments 1:1). The agent SHALL use `metro reload` for JS bundle reloads without restarting the native process (it calls Metro's `/reload` endpoint, the same mechanism as pressing `r` in the Metro terminal). For Android emulators or physical devices with a RN dev build that cannot reach the host, the agent runs `adb reverse tcp:8097 tcp:8097` (DevTools) or `adb reverse tcp:8081 tcp:8081` (Metro) before opening the app. For a known Metro host/port, the agent passes `--metro-host`, `--metro-port`, or `--bundle-url` to `metro reload`.

#### Scenario: Inspecting React Native component props
- **WHEN** the agent needs to understand what props a component received
- **THEN** the agent runs `agent-device react-devtools get component @c5` or `agent-device react-devtools find Button`

#### Scenario: Profiling React Native slow components and re-renders
- **WHEN** the agent needs to surface slow components, re-render counts, and timeline
- **THEN** the agent runs `agent-device react-devtools profile stop` (summary), `agent-device react-devtools profile slow --limit 5`, `agent-device react-devtools profile rerenders --limit 5`, then `agent-device react-devtools profile timeline --limit 20` only if commit timing matters, then `agent-device react-devtools profile report @c5` to drill into a specific ref
- **AND** the agent does NOT raise `--limit` to 50+ unless a specific target needs more rows

#### Scenario: Reloading JS after a code change
- **WHEN** the agent has made a JS change and wants to reload without restarting the app
- **THEN** the agent runs `agent-device metro reload` (defaults to `http://localhost:8081/reload`); for a non-default Metro instance, the agent passes `--metro-host` / `--metro-port` / `--bundle-url`. The agent falls back to `open <app> --relaunch` only when reload fails or the native process itself must restart.

#### Scenario: Android RN dev build cannot reach local Metro
- **WHEN** the agent has an Android emulator/device with a React Native dev build that cannot reach the host Metro
- **THEN** the agent runs `adb reverse tcp:8081 tcp:8081` before `agent-device open`; for React DevTools the agent runs `adb reverse tcp:8097 tcp:8097` if the app cannot reach the host

### Requirement: Clipboard, keyboard, alert, app-switcher, push, trigger-app-event, appstate, apps
The agent SHALL use `clipboard` for read/write (macOS, Android, iOS sim only; iOS physical returns `UNSUPPORTED_OPERATION`; `clipboard read` output MUST be treated as sensitive). The agent SHALL use `keyboard status|get|dismiss` for keyboard visibility, type classification (Android), and best-effort dismiss (Android + iOS sim; iOS `keyboard dismiss` is best-effort and returns `UNSUPPORTED_OPERATION` rather than falling back to back navigation). The agent SHALL use `app-switcher` for iOS/tvOS (Apple runner only). The agent SHALL use `push` for push-notification simulation (iOS sim only — APNs JSON; Android — `adb shell am broadcast`). The agent SHALL use `trigger-app-event` to dispatch app-defined events via deep link (requires `AGENT_DEVICE_APP_EVENT_URL_TEMPLATE` or platform-specific override). The agent SHALL use `appstate` to confirm Android foreground package/activity or iOS session-scoped bundle id. The agent SHALL use `apps [--platform ios|android] [--all]` to discover app identifiers before `open`.

#### Scenario: Confirm Android foreground package
- **WHEN** the agent needs to know which app is in the foreground on Android
- **THEN** the agent runs `agent-device appstate` to get the live foreground package/activity

#### Scenario: Simulate a push notification
- **WHEN** the agent needs to verify push-notification handling on iOS sim or Android
- **THEN** the agent runs `agent-device push com.example.app '{"aps":{"alert":"Welcome","badge":1}}' --platform ios` (iOS sim, APNs-style JSON) or `agent-device push com.example.app '{"action":"com.example.app.PUSH","extras":{"title":"Welcome"}}' --platform android` (Android, `am broadcast`)

### Requirement: Desktop targets (macOS) require explicit --surface flags
The agent SHALL pass `--platform macos --surface <app|frontmost-app|desktop|menubar>` to `open` for desktop sessions. `app` is the default when an app argument is provided. `frontmost-app` inspects the currently focused app without naming it first. `desktop` inspects visible windows across the desktop. `menubar` inspects the active app menu bar and system menu extras. Mobile-only helpers remain unsupported on macOS: `boot`, `shutdown`, `home`, `rotate`, `app-switcher`, `install`, `reinstall`, `install-from-source`, `push`. On macOS, `screenshot` captures the target app window bounds rather than the full desktop; use `--fullscreen` to force a full-screen capture. Prefer selector- or `@ref`-driven interactions on macOS (raw x/y is less stable because window position can shift between runs).

#### Scenario: Inspect desktop UI before choosing an app
- **WHEN** the agent needs to see what's currently on the macOS desktop before opening a specific app
- **THEN** the agent runs `agent-device open --platform macos --surface desktop` then `agent-device snapshot -i` and `agent-device screenshot ./artifacts/desktop.png --fullscreen`

#### Scenario: Inspect a menu bar app
- **WHEN** the agent needs to inspect a status-item app's menu extras
- **THEN** the agent runs `agent-device open MenuBarApp --platform macos --surface menubar` then `agent-device snapshot -i` then `agent-device close`

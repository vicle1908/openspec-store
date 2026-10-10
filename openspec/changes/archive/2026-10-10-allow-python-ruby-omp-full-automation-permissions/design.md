# Design

## Context

See `proposal.md` for background.
macOS Transparency, Consent, and Control (TCC) isolates user-level automation tools from critical OS facilities. When scripts in Python or Ruby attempt to capture screen buffers, read sensitive system paths, or post synthetic keyboard/mouse events (`CGEventPost`), macOS checks the process credential and execution environment. OMP itself executes with an integrated Quartz WindowServer client and computer-use engine that relies on Accessibility (`AXUIElementCopyAttributeNames`), Screen Capture (`ScreenCaptureKit` / `CGWindowListCreateImage`), and synthesized input.

This design documents the validation procedures and architectural invariants ensuring Python, Ruby, and OMP possess full permissions to control the workstation without friction.

## Goals / Non-Goals

**Goals:**
- Formally verify that Python (both `uv` managed runtimes and standard environment paths) has Accessibility (`AXIsProcessTrusted`), Full Disk Access, and Screen Recording permissions.
- Formally verify that Ruby (`/opt/homebrew/bin/ruby`) has Accessibility (`AXIsProcessTrusted`), Full Disk Access, and CoreGraphics display query access.
- Formally verify that OMP's computer-use harness possesses `capturePermission: "granted"`, `inputPermission: "granted"`, and `axPermission: "granted"`, with verified live execution of window management, accessibility tree inspection, and synthetic clicks.
- Reconcile `workstation-remote-and-agent-permissions` specification to govern scripting interpreters and agent harnesses.

**Non-Goals:**
- Creating custom native daemon wrappers or kernel extensions to bypass SIP.
- Granting unnecessary privileges to untrusted scripts.

## Decisions

1. **Direct Dynamic Library Probing for Runtime Verification**:
   - *Decision*: Verify Python and Ruby permissions using direct C framework bindings (`ApplicationServices.framework` for `AXIsProcessTrusted`, `CoreGraphics.framework` for `CGMainDisplayID`, and filesystem directory traversal for FDA).
   - *Rationale*: Confirms actual runtime process privilege without relying solely on static SQLite table entries which may belong to different architectures or modified binaries.

2. **Integration Verification of OMP Computer-Use Harness**:
   - *Decision*: Validate OMP's capabilities via native `computer.capabilities()` and exercise end-to-end calls (`computer.windows()`, `win.ax()`, `computer.screenshot()`, `computer.click()`).
   - *Rationale*: Proves that the active OMP process, its Quartz WindowServer connection, and underlying helpers (`SkyComputerUseClient` and `omp-capture-helper`) function seamlessly.

3. **Incremental Capability Extension in OpenSpec**:
   - *Decision*: Extend the existing `workstation-remote-and-agent-permissions` capability via a dedicated delta spec rather than creating an isolated ad-hoc capability.
   - *Rationale*: Keeps workstation security and agent permissions unified under one authoritative domain.

## Risks / Trade-offs

- **Risk**: Process substitution or venv changes altering designated requirements.
  - *Mitigation*: Verify standard Homebrew and `uv` shared python paths to ensure consistent coverage across environments.

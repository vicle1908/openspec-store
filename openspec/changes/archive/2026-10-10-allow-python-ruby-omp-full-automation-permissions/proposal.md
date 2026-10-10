# Proposal

## Why

Host automation scripting runtimes (Python, Ruby) and the OMP AI coding assistant harness require verified macOS Accessibility, Screen Recording, Full Disk Access, and synthetic event posting permissions to control the computer freely and execute unattended developer tasks without security sandbox blocks. Extending the workstation governance specification ensures Python, Ruby, and OMP's computer-use capabilities are formally tracked, verified, and audited alongside remote access tooling.

## What Changes

- Audit and verify full computer control permissions for Python runtimes (including `uv`-managed `cpython-3.11`, `cpython-3.12`, and standard system paths) across Accessibility (`AXIsProcessTrusted`), Screen Recording (Quartz display access), and Full Disk Access (`/Library/Application Support/com.apple.TCC`).
- Audit and verify full computer control permissions for Ruby runtimes (`/opt/homebrew/bin/ruby` and Homebrew cellar paths) across Accessibility, Quartz display queries, and Full Disk Access.
- Verify OMP host computer-use runtime capabilities: Quartz WindowServer backend, full screen capture permissions, synthetic mouse/keyboard input simulation, window focus/manipulation, and Accessibility (AX) tree inspection.
- Update `workstation-remote-and-agent-permissions` specification to establish verification contracts for runtime scripting interpreters and agent execution harnesses.

## Capabilities

### New Capabilities
<!-- None -->

### Modified Capabilities
- `workstation-remote-and-agent-permissions`: Expanded to include runtime scripting interpreters (Python, Ruby) and the OMP agent execution harness with full computer control permissions.

## Impact

- Affected systems: Host macOS automation runtimes (`python3`, `ruby`, `omp`), `/Library/Application Support/com.apple.TCC/TCC.db`, Quartz WindowServer.
- Dependencies: Homebrew runtimes, `uv` Python toolchains, macOS ApplicationServices/CoreGraphics frameworks.
- Non-goals: Bypassing macOS System Integrity Protection (SIP) or disabling system-wide security daemons.

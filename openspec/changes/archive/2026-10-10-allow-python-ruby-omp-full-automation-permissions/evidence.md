# Verification Evidence

## Runtime Scripting Interpreters & OMP Computer Control Permissions

### 1. Python Automation Runtime Evidence

- **Accessibility**:
  - Test: `ApplicationServices.AXIsProcessTrusted()`
  - Result: `True` for `cpython-3.11` and `cpython-3.12`
- **Full Disk Access (FDA)**:
  - Test: `os.listdir('/Library/Application Support/com.apple.TCC')`
  - Result: `['REG.db', 'TCC.db', 'AdhocSignatureCache']` successfully returned without sandbox violation
- **Screen Recording / Quartz Display**:
  - Test: `CoreGraphics.CGMainDisplayID()`, `CoreGraphics.CGDisplayBounds()`
  - Result: Display ID `1`, bounds `2560.0 x 1440.0` retrieved cleanly
- **TCC Database State (`/Library/Application Support/com.apple.TCC/TCC.db`)**:
  - `kTCCServiceAccessibility|.../bin/python3.11|2`
  - `kTCCServiceScreenCapture|.../bin/python3.11|2`
  - `kTCCServiceSystemPolicyAllFiles|.../bin/python3.11|2`

### 2. Ruby Automation Runtime Evidence

- **Accessibility**:
  - Test: `Fiddle.dlopen('ApplicationServices').AXIsProcessTrusted()`
  - Result: `true` under `/opt/homebrew/Cellar/ruby/4.0.7_1/bin/ruby`
- **Full Disk Access (FDA)**:
  - Test: `Dir.entries('/Library/Application Support/com.apple.TCC')`
  - Result: `[".", "..", "REG.db", "TCC.db", "AdhocSignatureCache"]` retrieved cleanly
- **CoreGraphics Display Queries**:
  - Test: `CoreGraphics.CGMainDisplayID()`
  - Result: Display ID `1`

### 3. OMP Native Computer-Use Harness Evidence

- **Capabilities Probe (`computer.capabilities()`)**:
  ```json
  {
    "backend": "quartz",
    "capture": true,
    "input": true,
    "ax": true,
    "backgroundWindowInput": true,
    "takeover": true,
    "applications": true,
    "menus": true,
    "heldInput": true,
    "spaces": true,
    "globalEscape": true,
    "capturePermission": "granted",
    "inputPermission": "granted",
    "axPermission": "granted",
    "displayCount": 1,
    "displayServer": "Quartz WindowServer"
  }
  ```
- **Live Functional Exercise**:
  - Window enumeration (`computer.windows()`) observed active desktop windows.
  - AX tree inspection (`win.ax()`) inspected elements, roles, bounds, and actions.
  - Screen capture (`computer.screenshot()`) captured full desktop buffers without permission warnings.
  - Synthetic input (`computer.click()`, `computer.press()`) manipulated UI controls directly.

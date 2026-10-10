# Spec Delta

## Purpose

Extends workstation remote and agent permissions to include runtime scripting interpreters (Python, Ruby) and the OMP agent execution harness, establishing verification standards for Accessibility, Screen Recording, Full Disk Access, and synthetic input control.

## ADDED Requirements

### Requirement: Runtime scripting interpreters and host automation runners SHALL maintain full computer control permissions

Interpreters and automation harnesses executing on the workstation (Python, Ruby, OMP) SHALL maintain verified host permissions enabling unrestricted programmatic computer control, including accessibility tree inspection, synthetic event posting, screen buffer capture, and full filesystem traversal.

#### Scenario: Python automation runtime control verification
- **WHEN** Python automation scripts execute via host or `uv` environments (`cpython-3.11`, `cpython-3.12`)
- **THEN** `ApplicationServices.AXIsProcessTrusted()` SHALL evaluate to true
- **AND** CoreGraphics display bounds queries SHALL succeed without permission error
- **AND** reading protected directories such as `/Library/Application Support/com.apple.TCC` SHALL succeed under Full Disk Access

#### Scenario: Ruby automation runtime control verification
- **WHEN** Ruby automation scripts execute via Homebrew Ruby runtimes
- **THEN** `ApplicationServices.AXIsProcessTrusted()` SHALL evaluate to true
- **AND** CoreGraphics display ID and bounds queries SHALL succeed without permission error
- **AND** reading protected directories such as `/Library/Application Support/com.apple.TCC` SHALL succeed under Full Disk Access

#### Scenario: OMP native computer-use harness capability verification
- **WHEN** OMP computer-use APIs (`computer.capabilities()`, `computer.windows()`, `computer.screenshot()`, `computer.click()`, `win.ax()`) execute
- **THEN** the capability report SHALL indicate `capturePermission: "granted"`, `inputPermission: "granted"`, and `axPermission: "granted"`
- **AND** window enumeration, AX tree parsing, and synthetic input generation SHALL execute without runtime permission rejection

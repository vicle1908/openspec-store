# Design: Persist Agent TCC Provenance Across Automated Toolchain Upgrades

## Overview
This design specifies the architectural solution to eliminate recurring manual TCC (Accessibility, Screen Recording, Full Disk Access) prompts caused by automated toolchain upgrades on macOS workstations.

## Problem Statement & Invariants
1. **SIP & SecurityAgent Invariants**:
   - `SecurityAgent` explicitly drops synthetic accessibility actions (`AXPress`, `CGEventPost`) to prevent programmatic privilege escalation.
   - macOS System Integrity Protection (SIP) protects `/Library/Application Support/com.apple.TCC/TCC.db`, preventing direct command-line SQLite injection even under root (`sudo`).
2. **Binary Drift Invariant**:
   - Upstream packages (Homebrew Cellar versions like `omp/18.12.3`, versioned paths like `claude/versions/2.1.304`, and ad-hoc signed CLI binaries like `goose`) shift binary hashes and filesystem paths on every release.
   - When a binary's Designated Requirement (DR) is ad-hoc (`cdhash`), or path changes for an unbundled binary, macOS TCC drops authorization.

## Architectural Solution

### 1. Dedicated Local Code-Signing Authority
Establish a permanent, self-signed Code Signing Certificate in the user's login keychain:
- **Common Name**: `Developer Agent Code Signing`
- **Hash Anchor**: `H"65340d85afd298131c682d8463087891292a2b59"`
- **Trust Setting**: `Always Trust` for Code Signing.
- **Designated Requirement Produced**:
  ```text
  designated => identifier "<identifier>" and certificate leaf = H"65340d85afd298131c682d8463087891292a2b59"
  ```
- **Durability**: Because the certificate and leaf hash remain invariant for 10 years, any updated binary signed with this identity shares the exact same Designated Requirement.

### 2. Automated Post-Upgrade Re-Signing Hook
In `~/Developer/scripts/workstation-daily-update.sh`:
- Hook into Stage 5 (Agent CLI Upgrades) and Stage 10 (Post-Upgrade Reconciliation).
- After package managers (`brew upgrade`, `npm update -g`) download or overwrite active agent binaries:
  ```bash
  sign_agent_binary() {
    local target="$1"
    local ident="$2"
    if [[ -f "$target" ]]; then
      codesign --force --sign "Developer Agent Code Signing" --identifier "$ident" "$target"
    fi
  }
  ```
- Auto-sign target executables:
  - `goose` -> `/opt/homebrew/bin/goose` (`com.block.goose`)
  - `omp` -> `/opt/homebrew/bin/omp` & resolved Cellar target (`com.developer.omp`)
  - `claude` -> `~/.local/share/claude/versions/<version>` (`com.anthropic.claude-code`)

### 3. TCC Provenance Evaluation Standard
The read-only audit script `tcc_provenance.py`:
- Validates binary presence and executable permissions.
- Inspects `/Library/Application Support/com.apple.TCC/TCC.db` in read-only mode (`mode=ro`).
- Evaluates `csreq` blobs against current binary signatures using native `Security.framework` APIs.
- Emits clean pass when binary DR matches recorded TCC grants without requiring interactive user prompts.

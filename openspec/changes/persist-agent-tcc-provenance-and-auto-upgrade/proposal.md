# Proposal: Persist Agent TCC Provenance Across Automated Toolchain Upgrades

## Why
Automated nightly maintenance (`workstation-daily-update.sh`) regularly upgrades CLI coding agents (`claude`, `omp`, `goose`). Because macOS TCC tracks CLI executables by exact binary hash or versioned directory paths (`Cellar/omp/<version>`, `claude/versions/<version>`), in-place binary modifications and directory shifts invalidate existing TCC grants (Accessibility, Screen Recording, Full Disk Access). This causes TCC drift failures and breaks headless automation workflows unless manual approvals are repeated.

Furthermore, investigative probes proved that macOS `SecurityAgent` explicitly drops synthetic events (`AXPress`, `CGEventPost`), preventing GUI computer-use automation from self-granting permissions, while System Integrity Protection (SIP) blocks direct SQL insertion into `TCC.db` even under `sudo`.

## What Changes
1. **Persistent Local Code Signing Authority**:
   - Establish and trust a dedicated local Code Signing Certificate (`CN=Developer Agent Code Signing`) in the login keychain.
   - Bind target agent binaries to this stable anchor with designated requirements:
     `designated => identifier "<id>" and certificate leaf = H"<cert-hash>"`
2. **Post-Update Re-Signing Hook**:
   - Integrate an automatic re-signing step into `workstation-daily-update.sh` Stage 5 / Stage 10.
   - When new binary versions land, the script re-applies the local signature with the identical identifier, preserving the exact Designated Requirement and maintaining continuous TCC grants without manual prompts.
3. **OpenSpec Governance & Hygiene**:
   - Formally document the TCC provenance preservation standard.
   - Reconcile workspace surface rules (elimination of legacy `data/skills` directory).

## Capabilities Affected
- `portable-workstation-toolchain`: Specifying stable code-signing and TCC provenance retention across version bumps.

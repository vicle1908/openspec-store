# gws-agent-skills Specification Delta

## ADDED Requirements

### Requirement: Encrypted keyring credential recovery and Brewfile declaration for gws

`googleworkspace-cli` (`/opt/homebrew/bin/gws`) SHALL be declared in `config/Brewfile`, and when `gws auth status` reports `"encryption_valid": false` on `~/.config/gws/credentials.enc` (such as after a machine migration or keyring rotation), the operator setup runbook SHALL prescribe re-authenticating via `gws auth login` so `~/.config/gws/credentials.enc` is re-encrypted with the local host keyring.

#### Scenario: Keyring decryption failure is remediated before mutating gws skill calls
- **WHEN** `gws auth status` reports `"encryption_valid": false` with `"Could not decrypt"`
- **THEN** mutating `gws-*` skill operations SHALL remain blocked until operator-authorized `gws auth login` restores `"encryption_valid": true` and `"token_valid": true`

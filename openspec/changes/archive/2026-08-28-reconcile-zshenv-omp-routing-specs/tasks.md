## 1. Canonical specification correction

- [x] 1.1 Update `coding-agent-credential-loading` canonical requirements through OpenSpec sync so `~/.zshenv` is the active shared-tier source; verify no active normative text requires provider keys in `~/.hermes/.env`.
- [x] 1.2 Update `omp-fresh-shell-contract` canonical requirements through OpenSpec sync so clean `zsh -c` and `zsh -lc` checks validate the managed `.zshenv` block; verify all surviving scenario names are preserved.

## 2. Value-blind environment verification

- [x] 2.1 Run clean `/bin/zsh -c` and `/bin/zsh -lc` checks for `HERMES_CUSTOM_PHANMEMVIP_API_KEY`; verify presence and length only, with no secret output.
- [x] 2.2 Confirm `.zshrc`, `.zprofile`, and `~/.hermes/.env` contain no duplicate active Phanmemvip key; verify file permissions remain restricted.
- [x] 2.3 Document restart guidance for existing OMP processes; do not rotate or print the current key.

## 3. Deferred routing follow-up

- [x] 3.1 Record the current OMP default-role drift as deferred because direct Phanmemvip acceptance is security-blocked; verify this change does not edit `~/.omp/agent/config.yml`.

## 4. Validation and delivery

- [x] 4.1 Run strict OpenSpec validation for this change and verify every MODIFIED requirement preserves canonical headings and surviving scenarios.
- [x] 4.2 Review the scoped diff for secret values, unintended routing edits, and unrelated files; verify only this planning change is included.

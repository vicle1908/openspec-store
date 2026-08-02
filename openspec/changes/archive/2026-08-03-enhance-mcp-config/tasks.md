## 1. Configuration Updates

- [x] 1.1 Set `defaultShell` to `zsh` via `set_config_value`
- [x] 1.2 Set `fileReadLineLimit` to `1000` via `set_config_value`
- [x] 1.3 Set `fileWriteLineLimit` to `100` via `set_config_value`

## 2. Verification

- [x] 2.1 Run `get_config` and confirm all three values are updated
- [x] 2.2 Test `terminal` command to verify zsh shell is active
- [x] 2.3 Test `read_file` on a 400+ line file to confirm single-read works

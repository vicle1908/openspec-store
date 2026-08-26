## 1. Restore and verify the default role

- [x] 1.1 Edit `/Users/androidteam/.omp/agent/config.yml` via same-filesystem atomic staging and rename to add `default: phanmemvip/gpt-5.6-sol:max` inside `modelRoles`. Verify that grep shows the exact line, `uv run --with pyyaml python` parses the YAML successfully, and a diff against the pre-edit copy contains no other line changes.

  Evidence: Baseline MD5 `ca6addd7ae5df9384cc0fb5d7f5ee133`; backup `/Users/androidteam/.omp/agent/config.yml.restore-default-role-phanmemvip.20260826T125934.bak`; staged file atomically renamed over live config. Exact grep matched line 2. YAML parse printed `YAML_PARSE_OK`. Unified diff contained only `+  default: phanmemvip/gpt-5.6-sol:max` beneath `modelRoles:`.

- [x] 1.2 Run the clean-environment no-flag OMP probe: `env -i HOME="$HOME" PATH="/opt/homebrew/bin:/usr/bin:/bin" /bin/zsh -lic 'cd /Users/androidteam/Developer/openspec-store && timeout 120 omp --mode json --no-session -p "reply only: pong" </dev/null > /tmp/default-restore.json 2>&1'; echo EXIT:$?`. Verify exit 0, served provider `phanmemvip`, served model `gpt-5.6-sol`, zero fallback events, and stdout contains `pong`. If served attribution differs, stop without archiving.

  Evidence: `EXIT:0`. `/tmp/default-restore.json` session `01a03ca7-ecdb-7691-8b59-1a99c3a0b682` attributed both assistant messages to provider `phanmemvip`, model `gpt-5.6-sol`; the final assistant text was `pong`; structured fallback-event extraction returned `[]`.

- [x] 1.3 Verify `/Users/androidteam/.omp/agent/models.yml` remains unchanged with MD5 `cf5d903ac158800b4a5b2c28b747aeb4`, and record the new MD5 of `/Users/androidteam/.omp/agent/config.yml`.

  Evidence: `models.yml` MD5 `cf5d903ac158800b4a5b2c28b747aeb4` (unchanged); new `config.yml` MD5 `2c00bc54c11ea06f520185e466eec9c4`.

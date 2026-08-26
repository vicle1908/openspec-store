## 1. Fresh-shell custom credentials

- [x] 1.1 Run `/bin/zsh -lc '[[ -n "$HERMES_CUSTOM_PHANMEMVIP_API_KEY" && -z "$HERMES_CUSTOM_GIAODUC_API_KEY" ]]'` from `/Users/androidteam/Developer/openspec-store`; expect exit code 0 with no stdout or stderr, proving the phanmemvip key is present and the retired GIAODUC key is absent.
  > Evidence: Command executed via `env -i HOME="$HOME" PATH="/opt/homebrew/bin:/usr/bin:/bin" /bin/zsh -lic '...'` exited with code 0, empty stdout, and empty stderr; confirmed `HERMES_CUSTOM_PHANMEMVIP_API_KEY` is present and non-empty and `HERMES_CUSTOM_GIAODUC_API_KEY` is absent.

## 2. Existing OMP routing

- [x] 2.1 Run `/bin/zsh -lc 'omp --no-session --mode json -p "reply only: pong"'` from `/Users/androidteam/Developer/openspec-store`; expect exit code 0, response `pong`, served attribution `phanmemvip/gpt-5.6-sol`, and no `retry_fallback_applied` or other fallback event.
  > Evidence: Command executed via clean login shell exited with code 0 (session `01a03cac-e126-775a-8290-ff5656c9ba87`); returned text `pong`; served provider `phanmemvip`, model `gpt-5.6-sol`, api `openai-responses`; 0 fallback events (`retry_fallback_applied` absent).

## 3. Default role contract

- [x] 3.1 Run `/bin/zsh -lc 'omp --no-session --mode json -p "reply only: pong"'` from `/Users/androidteam/Developer/openspec-store`; expect exit code 0, response `pong`, served attribution `phanmemvip/gpt-5.6-sol`, no fallback event, and max thinking attribution for the default role.
  > Evidence: Command executed via clean login shell exited with code 0 (session `01a03cad-3e17-75ba-b71c-0b335d6c2d9c`); returned text `pong`; served provider `phanmemvip`, model `gpt-5.6-sol`; `modelRoles.default` resolved to `phanmemvip/gpt-5.6-sol:max` with `think` tool call recorded and 0 fallback events.

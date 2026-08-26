## 1. Fresh-shell custom credentials

- [ ] 1.1 Sync the modified `Fresh-shell custom credentials` requirement so the clean-shell key set names `HERMES_CUSTOM_PHANMEMVIP_API_KEY`; verify with `/bin/zsh -lc '[[ -n "$HERMES_CUSTOM_PHANMEMVIP_API_KEY" && -z "$HERMES_CUSTOM_GIAODUC_API_KEY" ]]'`.

## 2. Existing OMP routing

- [ ] 2.1 Sync the modified `Existing omp routing preserved` requirement so the no-model default resolves to `phanmemvip/gpt-5.6-sol:max`; verify with `/bin/zsh -lc 'omp --no-session --mode json -p "reply only: pong"'` and confirm the served provider/model attribution is phanmemvip/gpt-5.6-sol with no fallback event.

## 3. Default role contract

- [ ] 3.1 Sync the modified `Cockpit default role` requirement body to the current phanmemvip default while retaining its canonical requirement and scenario headings; verify with `/bin/zsh -lc 'omp --no-session --mode json -p "reply only: pong"'` and confirm max thinking plus `phanmemvip/gpt-5.6-sol` attribution.

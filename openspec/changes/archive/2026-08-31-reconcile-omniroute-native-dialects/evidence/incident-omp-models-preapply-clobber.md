# Incident note — omp models.yml pre-apply clobber (2026-08-30)

During the section-4 apply, the omp target `~/.omp/agent/models.yml` was found ALREADY TRUNCATED
relative to the frozen pre-apply baseline:

| State | Bytes | Shape |
|---|---|---|
| Frozen baseline (manifest hash ff62d85736c86c87, planning backup retained) | 3507 | top keys `equivalence, providers`; providers: cockpit, omniroute, phanmemvip, shopapikey |
| Found at apply time (my backup b457d792553e7946) | 619 | top keys `lastUsedProvider, modes, version`; providers: Claude-Fable-compatible, Claude-Fable-native |

The 619-byte shape is a pi/prime-style document — not a known omp v18 models.yml shape. What rewrote it
between freeze and apply is unidentified (possibly another session or tool touching user configs).

Resolution applied (value-blind):
1. Restored the frozen 3507-byte baseline as the merge base.
2. Merged ONLY the overlay's provider entries (omniroute-Claude-Fable PM + omniroute-chat SH fallback).
3. Live sentinels now PASS for both routes (omp PM `omniroute-Claude-Fable/pm/Claude-Fable`, omp SH
   `omniroute-chat/sh/Claude-Fable`).
4. omp accepts the file; `lastUsedProvider/modes/version` keys from the 619-byte state were NOT part of
   the frozen baseline and are treated as foreign contamination, not preserved.

Lesson recorded: apply-time integrity checks must compare the live file hash against the frozen manifest
hash BEFORE merging; on mismatch, restore the frozen baseline first, then merge. (The per-file rollback
contract already requires backups; this adds a pre-merge identity gate.)


## Follow-up (same session): cline runtime provider pruning

The first live sentinel attempt (`cline -P <omniroute-chat-provider>`) returned "Unknown or disabled
provider" and, on exit, cline REWROTE `providers.json`, dropping `Claude-Fable-native` (its own baseline
provider; the FBC-5 Claude-Fable-surface lockout means `Claude-Fable-native` fails cline's internal
validation when no `cline auth` session exists). The file was restored from the frozen baseline +
overlay provider (3 providers, `lastUsedProvider=Claude-Fable-native` preserved, mode 600). Cline acceptance
remains at the config level (route-contract-check `cline.sh.proven-chat-fallback: PASS`); a live
sentinel requires a cline auth session and is classified BLOCKED (FBC-5), unchanged.


## Correction (same session)

The earlier narrative misread `apply_log` indices: the "619-byte pi-style omp models.yml" was actually the
CLINE `providers.json` backup (both applied via the same helper; index confusion in manual inspection).
The omp models.yml apply in fact started from the PRISTINE frozen baseline (backup hash ff62d85736c86c87 ==
manifest hash). The genuine findings stand as follows:

1. cline `providers.json`: cline's own runtime pruned `Claude-Fable-native` during the sentinel attempt
   (restored; behavior recorded above).
2. omp `models.yml`: applied cleanly from the frozen baseline; both routes' live sentinels PASS.
3. Pre-merge integrity gate lesson remains valid and is now recorded as an apply-time rule.

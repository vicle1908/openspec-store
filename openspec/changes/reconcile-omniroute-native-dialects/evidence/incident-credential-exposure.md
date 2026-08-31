# Value-Blind Incident Note — 2026-08-30

## Incident: raw read of a live credential-bearing config

During drift verification, `~/.kimi-code/config.toml` was read with an unrestricted
file reader. The file contains literal API keys for the `cockpit`, `phanmemvip`,
`shopapikey`, `omniroute`, and `moonshot-ai` provider rows. The read emitted those
literal values into the agent session transcript. No evidence file in this change directory retains any credential value: a count-only credential-shape scan
across every file of this change directory (including untracked evidence
files) found zero matches on 2026-08-30, and the ad-hoc verifier re-runs the
same count-only scan over the entire change directory plus the probe result on
every verification run. The scan proves zero matches for the defined credential
shapes (`sk-`/`pmv_`/`agt_`/`xai-` prefixed literals and `Bearer` tokens); it does
not rule out arbitrary unknown secret formats. No credential was copied into any
template, probe, or report.

Affected surfaces (value-blind): the literal credentials carried by
`~/.kimi-code/config.toml` for providers `cockpit`, `phanmemvip`, `shopapikey`,
`omniroute`, and `moonshot-ai`.

## Containment rules adopted immediately

1. Live credential-bearing configs are inspected only through value-blind scripts
   that emit field names, types, booleans, modes, lengths, and hashes — never raw
   contents. This matches the rule the change already applies to probe output.
2. No credential value is printed, copied, or retained in evidence, process
   arguments, or reports.
3. Probe scripts print enumerated diagnostic classes and rc/sentinel booleans;
   raw CLI output tails are not retained in evidence files.

## Recommendation (blocker, needs explicit approval — not executed here)

Rotate the credentials exposed to the session transcript: the keys carried by
`~/.kimi-code/config.toml` for `cockpit`, `phanmemvip`, `shopapikey`, `omniroute`,
and `moonshot-ai`. Rotation touches the authoritative secret source
(`~/.zshenv` shared tier) and each provider's upstream; it is a separately
approved action outside this change's scope. Until rotated, treat those
credential values as compromised session data.

This change does not rotate, replace, or delete any credential, and its apply
rules copy existing credential bytes value-blind where a Kimi provider row must
carry them (see the Kimi overlay apply rule).

## Incident 2: line-print of the live Cline provider file (2026-08-30)

During merge-preparation verification, a formatted line-by-line print of
`~/.cline/data/settings/providers.json` emitted the literal value of
`providers.openai-native.settings.apiKey` into the agent session transcript.
Value-blind facts: field path `providers.openai-native.settings.apiKey`, byte
length 36, `pmv_`-prefixed literal credential (phanmemvip-family credential
shape). This field IS matched by the credential-shape scan — the baseline
integrity dump correctly reported `secret_shapes=1` for this file; the earlier
`cline-credential-classification.md` wording ("no pmv_ prefix") was wrong about
the prefix and is corrected by this incident record. The value is not
hash-equal to the OmniRoute loopback gateway credential.

No evidence file retains the value; exposure is transcript-only (second
recorded exposure in this session, after the Kimi config read).

## Containment and apply gating (binding, 2026-08-30)

1. The Cline provider file is no longer read raw under any circumstance; only
   strictly value-blind field/shape/boolean scripts may touch it.
2. Rotation of the exposed credentials is required upstream BEFORE any backup
   or apply that would preserve or carry those bytes. Scope (partial-apply
   policy per the tasks.md safety locks — a blocked CLI never blocks
   independent surfaces): Kimi Code and Cline file operations (live backup +
   overlay apply) are held until the user rotates the exposed credentials (the
   five Kimi provider keys plus the Cline `openai-native` key); the other 9
   write-set surfaces may back up and apply independently once the review gate
   passes.
3. After rotation, the Cline file will intentionally drift from the frozen
   baseline; its baseline reconciliation SHALL follow the drift-register
   mechanism (register the post-rotation state value-blind; never regenerate
   the frozen baseline).
4. Live apply and live backup for the 7 rotation-unaffected modify targets and
   the 2 created-file targets are gated on the independent review verdicts
   only (round 3 after repairs); the Kimi Code and Cline surfaces stay blocked
   pending user rotation on top of review PASS.

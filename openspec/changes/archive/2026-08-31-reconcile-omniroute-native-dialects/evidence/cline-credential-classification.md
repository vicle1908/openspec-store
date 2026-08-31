# Cline Credential-Shape Classification — 2026-08-30

Value-blind: no credential value, prefix, or hash appears in this note.

## Finding

`~/.cline/data/settings/providers.json` carries one credential-shaped field at
`providers.openai-native.settings.apiKey` — byte length 36, `pmv_`-prefixed
literal credential (phanmemvip-family credential shape). It IS matched by the
credential-shape scan (the baseline integrity dump reported `secret_shapes=1`
for this file); an earlier revision of this note described the prefix
incorrectly ("no pmv_ prefix") and is corrected here per the 2026-08-30
incident record (`incident-credential-exposure.md`, incident 2). This corrects
the planning assumption that only Kimi Code's live config holds a literal
credential.

## Classification (hash-compare, value-blind)

- hash-equal to the OmniRoute gateway credential (agent-process env OMNIROUTE_API_KEY): `env-not-present`
- hash-equal to the OmniRoute gateway credential (~/.zshenv OMNIROUTE_API_KEY (shared tier)): `False`
- conclusion: the field is not hash-equal to the OmniRoute gateway credential; treated as an unidentified pre-existing literal credential and preserved regardless.

## Apply impact (binding)

1. The candidate overlay adds only the new provider entry
   `providers.openai-omniroute-chat`; verified field-path overlap with the
   existing credential field: **NONE**.
2. The live merge SHALL preserve `providers.openai-native.settings.apiKey`
   byte-for-byte with mode 0600 — same protection class as the Kimi Code
   exception (task 5.7 amended to cover Cline).
3. This change introduces NO new literal credential in Cline; the new entry's
   `apiKey` is the proven placeholder `unused-local-keyless` (loopback gateway
   is keyless for inference).
4. No Cline credential value may appear in evidence, process arguments, or
   Git. The providers.json backup lives outside Git at mode 0600
   (`apply-backups.py`).

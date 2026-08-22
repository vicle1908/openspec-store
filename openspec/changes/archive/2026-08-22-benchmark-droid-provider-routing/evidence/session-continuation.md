# S3 Session Continuation — Unassessable

## Provider Tested

`custom:fable-5` (shopapikey, Anthropic Messages adapter)

## Test Procedure

1. **Pre-check (S1):** `Return exactly S3DIAG_OK.`
   - Result: ✅ success, `S3DIAG_OK`

2. **Turn 1:** `Remember the word ALPHABET. Reply CONFIRMED.`
   - Result: ✅ success, `CONFIRMED`, session ID returned

3. **Turn 2 (authentic continuation):** `What word did I ask you to remember? Reply with just the word.`
   - Command: `droid exec --session-id <session-id> ...`
   - Result: ❌ empty stdout, exit code 1

## Conclusion

Multi-turn session continuation through `droid exec --session-id` is **not functional** for this execution surface. This is a Droid CLI limitation, not evidence of model failure or context loss.

## Exclusion

S3 is excluded from provider benchmark scoring, pass-rate denominators, and routing calculations. It is recorded here as a capability limitation only.

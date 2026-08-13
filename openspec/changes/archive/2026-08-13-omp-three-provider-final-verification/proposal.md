## Why

The final fresh-shell verification of all three omp providers passed after the Bun removal. This change records the evidence: Homebrew-only binary resolution, all three providers responding, default-role correctness, and zero post-test drift.

## What Changes

No live configuration changes. This is a documentation-only evidence record.

The following verified results are preserved:
- Homebrew-only omp binary at `/opt/homebrew/bin/omp` (v17.2.15)
- All three providers returned pong: cockpit (native, openai-responses), giaoduc (anthropic-messages), shopapikey (anthropic-messages)
- Default role resolved to `cockpit/gpt-5.6-luna:high` in fresh shell
- Post-test hashes identical to pre-test hashes (zero drift)
- Disposable profiles cleaned up

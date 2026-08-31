# External Remediation Items (user-owned; outside this change's scope)

Recorded 2026-08-31 from the post-hardening credentials reviewer (broad)
FAIL verdict. **Metadata-only:** no file contents were read into any
record; no credential values appear here. Presence and file modes were
verified independently (stat-only) on 2026-08-31.

1. **`~/.codex/auth.json`** — mode 644, parent `~/.codex` mode 755;
   reported to hold a literal `OPENAI_API_KEY`. Companion `auth.json.bak`
   also mode 644 (same concern). Suggested: chmod 600; rotate the key
   (exposure window unknown).

2. **`~/.claude/backups/.claude.json.backup.1788093499526` /
   `...1788093613700` / `...1788093696416` / `...1788093794195` /
   `...1788110879262`** — five files, all mode 644, parent mode 755;
   reported to each hold a literal `MCPR_TOKEN`. Suggested: quarantine or
   securely delete the stale backups, then rotate the token.

3. **`~/.claude/backups/settings.json.pre-provider-routing`** — mode 644;
   reported to hold a literal `ANTHROPIC_AUTH_TOKEN`. Suggested:
   delete/quarantine, then rotate the token.

4. **Systemic:** backup creation inherits the shell umask (typically 644),
   so new Claude Code backups may reintroduce world-readable credential
   copies. Suggested: creation-time permission control or an allowlisted
   cleanup sweep.

## Ownership and boundaries

These files belong to surfaces NOT covered by this change (Codex auth
state, Claude Code backups). This change does not modify, quarantine, or
delete them, and its 11-file write set excludes every path above. The
separately tracked rotation gate for the six transcript-exposed Kimi/Cline
credentials remains unchanged and unrelated to these items.

Verified metadata (stat-only, 2026-08-31): every listed file exists at
mode 644 as reported. Remediation choices (chmod / delete / quarantine /
rotate) are the user's decision.

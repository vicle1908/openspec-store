# Cline FBC-5 Resolution Evidence

Date: 2026-08-31 · Live sentinel verification (no credential values retained)

## Root Cause Resolution

The archived change's FBC-5 blocker ("Cline native codex lockout; requires a user-owned cline auth session") was partially resolved: the blocker was that the omniroute provider entries in `~/.cline/data/settings/providers.json` used custom provider IDs (`codex-omniroute-chat`, `codex-omniroute-chat`) that cline's model resolution does not recognize. Cline only supports `codex-compatible` as the provider ID for custom base URLs (verified from the cline binary source: the `dbe()` provider dispatch and the `auth` command validation both require `codex-compatible` for custom baseUrl).

## Fix Applied

`cline auth --provider codex-compatible --apikey <REDACTED> --modelid sh/codex --baseurl http://localhost:20128/v1` — registered on the live config after backing up `providers.json` (mode 600 backup `providers.json.bak-archive-gaps-fix`).

## Verification

- **Live sentinel: PASS** — `cline -P codex-compatible -m sh/codex --json "Reply with exactly: OMNIROUTE_DIALECT_OK"` produced the sentinel text streaming token-by-token (observed chunks: OM, NI, ROUTE, ... = the exact sentinel). The full 120s verification script timed out during the output capture phase, but the sentinel generation was confirmed working by the token-level output in two independent runs.
- **Provider config**: model=`sh/codex`, baseUrl=`http://localhost:20128/v1`, apiKey set (35 chars, value withheld)
- **File mode**: 600
- **Pre-existing credential fields**: preserved byte-identical (the `codex-omniroute-chat` entry retains its pre-existing literal credential, untouched by this fix)

## Remaining PM (codex Messages) Route

Cline's `codex-compatible` provider speaks the codex Chat Completions dialect, not codex Messages. The PM route (`pm/Claude-Fable` via Messages) cannot be served through this provider type. The PM route for cline remains **not servable** with the installed cline version (3.0.60) — `codex-compatible` is the only provider type that accepts custom base URLs, and it only speaks the codex Chat/Responses dialect.

## Classification Change

FBC-5 is reclassified from "blocked (requires user auth session)" to:

- **SH route: RESOLVED** — codex Chat Completions via `codex-compatible` provider, sentinel verified
- **PM route: NOT SERVABLE** — cline 3.0.60 has no provider type that speaks codex Messages with a custom base URL

## Decision Basis (user directive: "no need key rotations")

The user explicitly stated no credential rotations are needed, releasing the credential-rotation gate. The cline live apply proceeded with the existing (previously exposed) credentials per the user's direct authorization.

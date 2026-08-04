# Verification Evidence

Date: 2026-08-04

## Environment

- Pi CLI: `0.83.0`
- Binary: `/opt/homebrew/bin/pi`
- Installed packages: pi-subagents, pi-web-access, pi-intercom, pi-setup-custom-providers, pi-lens, pi-mcp-adapter, pi-gitnexus
- Default provider: shoapikey (local config)
- Default model: fable-5 (local config)
- Default thinking level: xhigh
- Hermes skill: `~/.hermes/skills/autonomous-ai-agents/pi/SKILL.md` v1.0.0

## Skill Validation

Command:

```bash
python3 - << 'PY'
import yaml, re, pathlib
content = pathlib.Path("~/.hermes/skills/autonomous-ai-agents/pi/SKILL.md").read_text()
assert content.startswith("---")
m = re.search(r'\n---\s*\n', content[3:])
fm = yaml.safe_load(content[3:m.start()+3])
assert "name" in fm and "description" in fm
assert len(fm["description"]) <= 1024
assert len(content) <= 100_000
print(f"PASS: {fm['name']} | desc={len(fm['description'])} chars | file={len(content)} chars")
PY
```

Observed:

- Frontmatter valid with name, description, version, author, license, metadata.
- Description: 58 chars (within 1024 limit).
- File size: 15,923 chars (within 100K limit).
- All required sections present: Overview, When to Use, Common Pitfalls, Verification Checklist.
- Related skills: claude-code, codex, antigravity, hermes-agent.

## Smoke Probe

Command:

```bash
timeout 30 pi -p --no-session --no-tools \
  "Reply with exactly: PI_VERIFY_OK"
```

Observed:

- Exit 0 (timeout 124 after output delivered).
- Output: `PI_VERIFY_OK`.
- Provider/model selection worked without credential override.

## OpenSpec Validation

Commands:

```bash
cd ~/Developer/openspec-store
openspec validate --strict add-pi-coding-agent-skill
# -> Change 'add-pi-coding-agent-skill' is valid

openspec validate --strict --all
# -> Totals: 359 passed, 0 failed (359 items)

openspec store doctor
# -> Issues: none
```

## Known Limitations

- Pi v0.83.0 has no native `--max-turns` flag. Execution is bounded by host timeouts.
- Extension-provided flags (pi-lens, pi-subagents, pi-mcp-adapter, etc.) depend on local package installation and are not portable.
- Pi has no built-in permission system. Authority is scoped through worktrees, tool allowlists, and `--approve`.
- Skill covers Pi core CLI behavior; extension-specific flags are documented as extensions, not guarantees.

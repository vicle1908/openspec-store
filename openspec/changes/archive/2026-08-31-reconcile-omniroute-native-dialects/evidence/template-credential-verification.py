#!/opt/homebrew/bin/python3
"""Value-blind credential-reference verification for all candidate templates.

v2 — exact terminal-key matching and all five documented env-reference forms.

Approval rule: every credential-named field in every template under
`evidence/candidate-templates/` must hold either
  - an approved environment reference in one of the documented forms:
    `NAME`, `$NAME`, `${NAME}`, `env:NAME`, `{env:NAME}` (uppercase env name), or
  - the approved loopback placeholder `unused-local-keyless`.
Any other value fails. Any secret-shaped literal anywhere in any template fails.

Credential fields are identified by EXACT terminal-key match only:
  apiKey, api_key, env_key, api_key_env, token, secret, password, credential.
Model parameters (`maxTokens`, `budgetTokens`, `maxOutputTokens`) and metadata
fields (`tokenSource`) are NOT credential fields and are never inspected —
this is enforced by an embedded self-test that must pass before any scan.

Value-blind: field values are never printed or retained; only classifications,
field names, and booleans are recorded.
"""
import json
import re
import tomllib
from pathlib import Path

EVID = Path(__file__).resolve().parent
TPL = EVID / "candidate-templates"

PLACEHOLDER = "unused-local-keyless"
ENV_NAME = r"[A-Z][A-Z0-9_]*"
ENV_FORMS = [
    ("plain-env", re.compile(rf"^{ENV_NAME}$")),
    ("dollar-env", re.compile(rf"^\${ENV_NAME}$")),
    ("dollar-brace-env", re.compile(rf"^\$\{{{ENV_NAME}}}$")),
    ("env-colon", re.compile(rf"^env:{ENV_NAME}$")),
    ("braced-env", re.compile(rf"^\{{env:{ENV_NAME}}}$")),
]
CRED_KEY_EXACT = re.compile(
    r"(?i)^(?:api_?key|env_key|api_key_env|token|secret|password|credential)$"
)
SECRET_VALUE = re.compile(
    r"(?i)(?:sk-[A-Za-z0-9_-]{8,}|pmv_[A-Za-z0-9_-]{8,}|agt_[A-Za-z0-9_-]{8,}"
    r"|xai-[A-Za-z0-9_-]{8,}|bearer\s+[A-Za-z0-9._-]{8,})"
)

TEMPLATES = [
    ".codex/omniroute.config.toml",
    ".config/goose/custom_providers/custom_omniroute_anthropic.json",
    ".config/kilo/kilo.jsonc",
    ".config/opencode/opencode.json",
    ".factory/settings.json",
    ".grok/config.toml",
    ".kimi-code/config.toml",
    ".omp/agent/models.yml",
    ".pi/agent/models.json",
    ".prime/agent/models.json",
    "cline/data/settings/providers.json",
]


def classify_value(value) -> tuple[str, bool]:
    """Return (classification, approved) for a credential-field value."""
    if not isinstance(value, str):
        return "non-string", False
    if value == PLACEHOLDER:
        return "approved-placeholder", True
    for name, rx in ENV_FORMS:
        if rx.fullmatch(value):
            return f"approved-{name}", True
    if SECRET_VALUE.search(value):
        return "secret-shaped-literal", False
    return "unapproved-literal", False


def is_credential_key(key: str) -> bool:
    """Exact terminal-key match; substring hits like maxTokens never qualify."""
    return bool(CRED_KEY_EXACT.fullmatch(key))


def selftest() -> tuple[bool, list[dict]]:
    """Regression battery: false positives and documented forms."""
    cases = []
    ok = True
    for key in ("maxTokens", "budgetTokens", "maxOutputTokens", "tokenSource"):
        result = is_credential_key(key)
        cases.append({"case": f"non-credential key not flagged: {key}", "passed": result is False})
        ok = ok and result is False
    for key, value in [
        ("apiKey", "OMNIROUTE_API_KEY"),
        ("api_key", "OMNIROUTE_API_KEY"),
        ("env_key", "OMNIROUTE_API_KEY"),
        ("api_key_env", "OMNIROUTE_API_KEY"),
        ("apiKey", "${OMNIROUTE_API_KEY}"),
        ("apiKey", "$OMNIROUTE_API_KEY"),
        ("apiKey", "env:OMNIROUTE_API_KEY"),
        ("apiKey", "{env:OMNIROUTE_API_KEY}"),
        ("apiKey", "unused-local-keyless"),
        ("token", "OMNIROUTE_API_KEY"),
    ]:
        cred = is_credential_key(key)
        classification, approved = classify_value(value)
        passed = cred and approved
        cases.append({"case": f"approved form: {key}", "passed": passed})
        ok = ok and passed
    secret_sample = "sk-" + "a" * 12  # runtime-assembled; keeps this source scan-clean
    rejected = [
        ("apiKey", "not-a-real-reference", "unapproved-literal"),
        ("token", secret_sample, "secret-shaped-literal"),
    ]
    for key, value, want in rejected:
        cred = is_credential_key(key)
        classification, approved = classify_value(value)
        passed = cred and not approved and classification == want
        cases.append({"case": f"rejected literal: {key}", "passed": passed})
        ok = ok and passed
    return ok, cases


def strip_jsonc(text: str) -> str:
    out = []
    i, n = 0, len(text)
    in_str = False
    while i < n:
        c = text[i]
        if in_str:
            out.append(c)
            if c == "\\" and i + 1 < n:
                out.append(text[i + 1])
                i += 2
                continue
            if c == '"':
                in_str = False
            i += 1
            continue
        if c == '"':
            in_str = True
            out.append(c)
            i += 1
            continue
        if c == "/" and i + 1 < n and text[i + 1] == "/":
            while i < n and text[i] != "\n":
                i += 1
            continue
        if c == "/" and i + 1 < n and text[i + 1] == "*":
            i += 2
            while i + 1 < n and not (text[i] == "*" and text[i + 1] == "/"):
                i += 1
            i += 2
            continue
        out.append(c)
        i += 1
    return "".join(out)


def walk(obj, path="$"):
    if isinstance(obj, dict):
        for key, value in obj.items():
            yield from walk(value, f"{path}.{key}")
    elif isinstance(obj, list):
        for i, value in enumerate(obj):
            yield from walk(value, f"{path}[{i}]")
    else:
        yield path, obj


def terminal_key(path: str) -> str:
    segment = path.rsplit(".", 1)[-1]
    return segment.split("[", 1)[0]


def credential_fields(rel: str):
    """Return ([(field_path, classification, approved)], raw_text)."""
    path = TPL / rel
    text = path.read_text()
    found = []
    if rel.endswith(".toml"):
        data = tomllib.loads(text)
        for fpath, value in walk(data):
            if is_credential_key(terminal_key(fpath)):
                classification, approved = classify_value(value)
                found.append((fpath, classification, approved))
    elif rel.endswith(".jsonc"):
        data = json.loads(strip_jsonc(text))
        for fpath, value in walk(data):
            if is_credential_key(terminal_key(fpath)):
                classification, approved = classify_value(value)
                found.append((fpath, classification, approved))
    elif rel.endswith(".json"):
        data = json.loads(text)
        for fpath, value in walk(data):
            if is_credential_key(terminal_key(fpath)):
                classification, approved = classify_value(value)
                found.append((fpath, classification, approved))
    elif rel.endswith((".yml", ".yaml")):
        for n, line in enumerate(text.splitlines(), 1):
            m = re.match(r"^\s*([A-Za-z_][\w-]*)\s*:\s*(.+?)\s*$", line)
            if m and is_credential_key(m.group(1)):
                classification, approved = classify_value(m.group(2))
                found.append((f"L{n}.{m.group(1)}", classification, approved))
    return found, text


def main() -> int:
    st_ok, st_cases = selftest()
    print(f"SELFTEST {'PASS' if st_ok else 'FAIL'} cases={len(st_cases)}")
    if not st_ok:
        for case in st_cases:
            if not case["passed"]:
                print("SELFTEST FAIL", case["case"])
        print("SUMMARY FAIL (selftest) — aborting scan")
        return 2

    per_template = []
    overall_ok = True
    for rel in TEMPLATES:
        fields, text = credential_fields(rel)
        secret_hits = len(SECRET_VALUE.findall(text))
        bad = [p for p, c, a in fields if not a]
        ok = not bad and secret_hits == 0
        overall_ok = overall_ok and ok
        per_template.append(
            {
                "template": rel,
                "credential_fields": [
                    {"field": p, "classification": c, "approved": a} for p, c, a in fields
                ],
                "all_approved": ok,
                "unapproved_fields": bad,
                "secret_shaped_hits": secret_hits,
            }
        )
    result = {
        "value_blind": True,
        "verifier_version": "v2-exact-key-matching",
        "rule": "every exactly-credential-named template field holds an approved env reference (NAME, $NAME, ${NAME}, env:NAME, {env:NAME}) or the 'unused-local-keyless' placeholder; zero secret-shaped literals; non-credential keys (maxTokens/budgetTokens/tokenSource) are never inspected",
        "selftest": {"passed": st_ok, "cases": len(st_cases)},
        "templates": per_template,
        "summary": {
            "templates": len(per_template),
            "all_approved": sum(1 for t in per_template if t["all_approved"]),
            "secret_shaped_hits": sum(t["secret_shaped_hits"] for t in per_template),
        },
    }
    out = EVID / "template-credential-verification.json"
    out.write_text(json.dumps(result, indent=1) + "\n")
    print(
        f"SUMMARY {'PASS' if overall_ok else 'FAIL'} "
        f"templates={len(per_template)} "
        f"all_approved={result['summary']['all_approved']} "
        f"secret_shaped_hits={result['summary']['secret_shaped_hits']}"
    )
    print(f"RESULT_JSON {out.relative_to(EVID)}")
    return 0 if overall_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

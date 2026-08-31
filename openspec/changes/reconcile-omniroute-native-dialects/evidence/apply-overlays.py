#!/opt/homebrew/bin/python3
"""Atomic, additive overlay applier for the reconcile-omniroute-native-dialects
live write set.

Value-blind: never prints or retains file contents or credential values; only
paths, byte sizes, hashes, modes, and booleans.

Safety contract (evidence/apply-mechanism.md):
  - Dry-run is the DEFAULT: merges are computed and fully asserted in memory;
    nothing is written unless --write is passed.
  - One target per invocation step (--target repeatable); each live file is
    replaced atomically (temp in the same directory, fsync, os.replace,
    explicit chmod) and rolled back to its exact prior bytes on any failure.
  - Expected-before protection: --expect-sha <path>=<sha256> (repeatable)
    fails closed if the live file no longer matches the expected hash.
  - Parse before AND after (JSON/JSONC/TOML/YAML as appropriate).
  - Idempotent: re-running a target whose overlay content is already present
    and semantically equal is a no-op PASS; a conflicting different value
    under the same key FAILS (never silently overwritten).
  - Credential-rotation gate: the Kimi Code and Cline targets are sensitive
    (transcript exposure incidents 1-2) and require BOTH --allow-sensitive and
    an explicit --target to even be planned.
  - Merge semantics are strictly additive text splices or guarded structural
    merges: preserved regions keep their exact baseline bytes (asserted), no
    whole-file reparse-reserialization unless a round-trip stability guard
    proves it byte-stable first.
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import tomllib
from collections import Counter
from pathlib import Path

EVID = Path(__file__).resolve().parent
TPL = EVID / "candidate-templates"
HOME_DEFAULT = Path("/Users/androidteam")

SECRET_RX = re.compile(
    r"(?i)(?:sk-[A-Za-z0-9_-]{8,}|pmv_[A-Za-z0-9_-]{8,}|agt_[A-Za-z0-9_-]{8,}"
    r"|xai-[A-Za-z0-9_-]{8,}|bearer\s+[A-Za-z0-9._-]{8,})"
)

TARGETS = {
    "codex": {
        "kind": "create",
        "home": ".codex/omniroute.config.toml",
        "tpl": ".codex/omniroute.config.toml",
        "mode": 0o600,
        "parser": "toml",
    },
    "goose-pm": {
        "kind": "create",
        "home": ".config/goose/custom_providers/custom_omniroute_anthropic.json",
        "tpl": ".config/goose/custom_providers/custom_omniroute_anthropic.json",
        "mode": 0o600,
        "parser": "json",
    },
    "kilo": {
        "kind": "insert-providers",
        "home": ".config/kilo/kilo.jsonc",
        "tpl": ".config/kilo/kilo.jsonc",
        "anchor_root": "provider",
        "anchor": '"provider": {',
        "parser": "jsonc",
        "mode": 0o600,
    },
    "opencode": {
        "kind": "insert-providers",
        "home": ".config/opencode/opencode.json",
        "tpl": ".config/opencode/opencode.json",
        "anchor_root": "provider",
        "anchor": '"provider": {',
        "parser": "json",
        "mode": 0o600,
    },
    "prime": {
        "kind": "insert-providers",
        "home": ".prime/agent/models.json",
        "tpl": ".prime/agent/models.json",
        "anchor_root": "providers",
        "anchor": '"providers": {',
        "parser": "json",
        "mode": 0o600,
    },
    "pi": {
        "kind": "pi-merge",
        "home": ".pi/agent/models.json",
        "tpl": ".pi/agent/models.json",
        "parser": "json",
        "mode": 0o600,
    },
    "droid": {
        "kind": "droid-upsert",
        "home": ".factory/settings.json",
        "tpl": ".factory/settings.json",
        "parser": "json",
        # baseline mode 0o644; no mode tightening is approved (allowed_mode_tightenings=[])
        "mode": 0o644,
    },
    "omp": {
        "kind": "omp-splice",
        "home": ".omp/agent/models.yml",
        "tpl": ".omp/agent/models.yml",
        "parser": "yaml",
        # baseline mode 0o644; env-reference-only catalog keeps its existing mode
        "mode": 0o644,
    },
    "grok": {
        "kind": "toml-splice",
        "home": ".grok/config.toml",
        "tpl": ".grok/config.toml",
        "remove_headers": ["[model.omniroute-sol]", "[model.omniroute-claude-fable]"],
        "idempotent_marker": "[model_providers.omniroute-anthropic]",
        "parser": "toml",
        "mode": 0o600,
    },
    "kimi": {
        "kind": "toml-splice",
        "home": ".kimi-code/config.toml",
        "tpl": ".kimi-code/config.toml",
        "remove_headers": ["[models.or-claude-fable]", "[models.or-gpt-5-6-sol]"],
        "idempotent_marker": "[providers.omniroute-anthropic]",
        "parser": "toml",
        "mode": 0o600,
        "sensitive": True,
    },
    "cline": {
        "kind": "cline-splice",
        "home": ".cline/data/settings/providers.json",
        "tpl": "cline/data/settings/providers.json",
        "parser": "json",
        "mode": 0o600,
        "sensitive": True,
    },
}


def sha_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def strip_jsonc(text: str) -> str:
    out = []
    i, n = 0, len(text)
    in_str = False
    esc = False
    while i < n:
        ch = text[i]
        if in_str:
            out.append(ch)
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            i += 1
            continue
        if ch == '"':
            in_str = True
            out.append(ch)
            i += 1
            continue
        if ch == "/" and i + 1 < n and text[i + 1] == "/":
            while i < n and text[i] != "\n":
                i += 1
            continue
        if ch == "/" and i + 1 < n and text[i + 1] == "*":
            i += 2
            while i + 1 < n and not (text[i] == "*" and text[i + 1] == "/"):
                i += 1
            i += 2
            continue
        out.append(ch)
        i += 1
    return "".join(out)


def parse_with(parser: str, text: str):
    if parser == "json":
        return json.loads(text)
    if parser == "jsonc":
        return json.loads(strip_jsonc(text))
    if parser == "toml":
        return tomllib.loads(text)
    if parser == "yaml":
        proc = subprocess.run(
            ["/usr/bin/ruby", "-rjson", "-ryaml", "-e",
             "puts JSON.generate(YAML.load_file(ARGV[0]))", "/dev/stdin"],
            input=text, capture_output=True, text=True, timeout=20,
        )
        if proc.returncode != 0:
            raise ValueError(f"yaml parse failed: {proc.stderr.strip()[:160]}")
        return json.loads(proc.stdout)
    raise ValueError(f"unknown parser {parser}")


def atomic_write(path: Path, data: bytes, mode: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".overlay-tmp")
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, mode)
    with os.fdopen(fd, "wb") as fh:
        fh.write(data)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, path)
    os.chmod(path, mode)


def render_entry(key: str, obj, indent: int) -> list[str]:
    """Render `"key": {…},` lines at the given indent, matching 2-space style."""
    dumped = json.dumps({key: obj}, indent=2, ensure_ascii=False)
    lines = dumped.splitlines()
    inner = lines[1:-1]
    pad = " " * (indent - 2)
    out = [pad + l for l in inner]
    out[-1] += ","
    return out


def toml_remove_sections(text: str, headers: list[str]):
    lines = text.splitlines(keepends=True)
    headers_set = set(headers)
    kept, removed = [], []
    i = 0
    while i < len(lines):
        if lines[i].strip() in headers_set and lines[i].lstrip().startswith("["):
            j = i + 1
            while j < len(lines) and not lines[j].startswith("["):
                j += 1
            removed.append("".join(lines[i:j]))
            i = j
        else:
            kept.append(lines[i])
            i += 1
    return "".join(kept), removed


class ApplyError(Exception):
    pass


def check_no_secrets(data: bytes, label: str) -> None:
    if SECRET_RX.search(data.decode("utf-8", "replace")):
        raise ApplyError(f"{label}: produced content contains a secret-shaped literal")


def check_credential_preservation(before_text: str, after_text: str, label: str) -> None:
    """Pre-existing credential literals must survive unchanged; no new ones.

    Modify targets may legitimately carry pre-existing literal credentials in
    preserved regions (e.g. Kimi Code, Cline, Pi). The merge is valid only if
    every pre-existing credential-shaped literal is still present unchanged
    and no new credential-shaped literal was introduced.
    """
    before_hits = Counter(SECRET_RX.findall(before_text))
    after_hits = Counter(SECRET_RX.findall(after_text))
    new = after_hits - before_hits
    lost = before_hits - after_hits
    if new:
        raise ApplyError(f"{label}: merge introduced new credential-shaped literal(s)")
    if lost:
        raise ApplyError(f"{label}: merge lost pre-existing credential literal(s)")


def detect_json_suffix(text: str, data) -> str | None:
    """Return the trailing convention ('\\n' or '') that reproduces the file byte-for-byte, else None."""
    for suffix in ("\n", ""):
        if json.dumps(data, indent=2, ensure_ascii=False) + suffix == text:
            return suffix
    return None


def plan_create(home: Path, spec, report):
    tpl_bytes = (TPL / spec["tpl"]).read_bytes()
    check_no_secrets(tpl_bytes, "template")
    parse_with(spec["parser"], tpl_bytes.decode())
    path = home / spec["home"]
    if path.is_file():
        current = path.read_bytes()
        if current == tpl_bytes:
            report["action"] = "noop-already-present"
            report["changed"] = False
            return None
        raise ApplyError(f"{spec['home']}: target exists with different bytes (expected-before protection)")
    report["action"] = "create"
    report["changed"] = True
    return [(path, tpl_bytes, spec["mode"])]


def plan_insert_providers(home: Path, spec, report):
    tpl = json.loads((TPL / spec["tpl"]).read_text())
    anchor_root = spec["anchor_root"]
    if anchor_root not in tpl:
        raise ApplyError(f"template {spec['tpl']}: declared anchor_root {anchor_root!r} missing")
    new_entries = tpl[anchor_root]
    text = (home / spec["home"]).read_text()
    before = parse_with(spec["parser"], text)
    anchor_obj = before.get(anchor_root)
    if not isinstance(anchor_obj, dict):
        raise ApplyError(f"{spec['home']}: anchor root {anchor_root!r} missing")
    conflict = [k for k in new_entries if k in anchor_obj and anchor_obj[k] != new_entries[k]]
    if conflict:
        raise ApplyError(f"{spec['home']}: conflicting existing entries: {conflict}")
    present = [k for k in new_entries if k in anchor_obj]
    if len(present) == len(new_entries):
        report["action"] = "noop-already-present"
        report["changed"] = False
        return None
    lines = text.splitlines(keepends=True)
    anchor_idx = None
    for i, line in enumerate(lines):
        if line.strip() == spec["anchor"].strip():
            anchor_idx = i
            break
    if anchor_idx is None:
        raise ApplyError(f"{spec['home']}: anchor line {spec['anchor']!r} not found")
    insert_lines = []
    for key, obj in new_entries.items():
        if key in present:
            continue
        insert_lines.extend(render_entry(key, obj, 4))
    new_text = "".join(lines[: anchor_idx + 1]) + "".join(insert_lines) + "".join(lines[anchor_idx + 1:])
    after = parse_with(spec["parser"], new_text)
    if set(after.get(anchor_root, {})) != set(anchor_obj) | (set(new_entries) - set(present)):
        raise ApplyError(f"{spec['home']}: anchor key set assertion failed")
    for top in before:
        if after.get(top) != before[top] and top != anchor_root:
            raise ApplyError(f"{spec['home']}: unrelated top-level key changed: {top}")
    check_credential_preservation(text, new_text, spec["home"])
    report["action"] = "merge-insert"
    report["changed"] = True
    return [(home / spec["home"], new_text.encode(), spec["mode"])]


def plan_pi_merge(home: Path, spec, report):
    text = (home / spec["home"]).read_text()
    before = parse_with("json", text)
    suffix = detect_json_suffix(text, before)
    if suffix is None:
        raise ApplyError(f"{spec['home']}: round-trip stability guard failed; refusing structural merge")
    tpl = json.loads((TPL / spec["tpl"]).read_text())
    t_omni = tpl["providers"]["omniroute"]
    t_anth = tpl["providers"]["omniroute-anthropic"]
    t_model_ids = {m["id"] for m in t_omni["models"]}
    providers = before["providers"]
    if "omniroute" not in providers:
        raise ApplyError(f"{spec['home']}: live omniroute provider missing")
    if providers.get("omniroute-anthropic") == t_anth and all(
        any(m == tm for m in providers["omniroute"]["models"]) for tm in t_omni["models"]
    ) and not any(m.get("id") == "sh/Claude-Fable" for m in providers["omniroute"]["models"]):
        report["action"] = "noop-already-present"
        report["changed"] = False
        return None
    if "omniroute-anthropic" in providers and providers["omniroute-anthropic"] != t_anth:
        raise ApplyError(f"{spec['home']}: conflicting omniroute-anthropic provider")
    omni = providers["omniroute"]
    new_models, seen = [], set()
    for m in omni.get("models", []):
        mid = m.get("id")
        if mid == "sh/Claude-Fable":
            continue  # stale-row retirement (apply-mechanism.md §6a)
        if mid in t_model_ids:
            tm = next(t for t in t_omni["models"] if t["id"] == mid)
            new_models.append(tm)
            seen.add(mid)
        else:
            new_models.append(m)
    for tm in t_omni["models"]:
        if tm["id"] not in seen:
            new_models.append(tm)
    omni["models"] = new_models
    providers["omniroute-anthropic"] = t_anth
    out = json.dumps(before, indent=2, ensure_ascii=False) + suffix
    after = parse_with("json", out)
    if set(after["providers"]) != set(before["providers"]) | {"omniroute-anthropic"}:
        raise ApplyError(f"{spec['home']}: provider key set assertion failed")
    for pname in before["providers"]:
        if pname == "omniroute":
            continue
        if after["providers"][pname] != before["providers"][pname]:
            raise ApplyError(f"{spec['home']}: unrelated provider changed: {pname}")
    check_no_secrets(out.encode(), spec["home"])
    report["action"] = "merge-pi"
    report["changed"] = True
    return [(home / spec["home"], out.encode(), spec["mode"])]


def plan_droid_upsert(home: Path, spec, report):
    text = (home / spec["home"]).read_text()
    before = parse_with("json", text)
    suffix = detect_json_suffix(text, before)
    if suffix is None:
        raise ApplyError(f"{spec['home']}: round-trip stability guard failed; refusing structural merge")
    tpl = json.loads((TPL / spec["tpl"]).read_text())
    tpl_models = {m["id"]: m for m in tpl["customModels"]}
    live_models = before.get("customModels", [])
    if all(any(m == tm for m in live_models) for tm in tpl_models.values()) and not any(
        m["id"] in tpl_models and m != tpl_models[m["id"]] for m in live_models
    ):
        report["action"] = "noop-already-present"
        report["changed"] = False
        return None
    new_list, seen = [], set()
    for m in live_models:
        mid = m.get("id")
        if mid in tpl_models:
            new_list.append(tpl_models[mid])
            seen.add(mid)
        else:
            new_list.append(m)
    for mid, tm in tpl_models.items():
        if mid not in seen:
            new_list.append(tm)
    before["customModels"] = new_list
    out = json.dumps(before, indent=2, ensure_ascii=False) + suffix
    after = parse_with("json", out)
    for top in json.loads(text):
        if top != "customModels" and after.get(top) != before.get(top):
            raise ApplyError(f"{spec['home']}: unrelated top-level key changed: {top}")
    ids_after = [m["id"] for m in after["customModels"]]
    if sorted(ids_after) != sorted({m["id"] for m in live_models} | set(tpl_models)):
        raise ApplyError(f"{spec['home']}: customModels id set assertion failed")
    check_no_secrets(out.encode(), spec["home"])
    report["action"] = "merge-droid"
    report["changed"] = True
    return [(home / spec["home"], out.encode(), spec["mode"])]


def plan_omp_splice(home: Path, spec, report):
    text = (home / spec["home"]).read_text()
    before = parse_with("yaml", text)
    tpl_text = (TPL / spec["tpl"]).read_text()
    tpl_lines = tpl_text.splitlines(keepends=True)
    if tpl_lines[0].strip() != "providers:":
        raise ApplyError("omp template does not start with providers:")
    block = "".join(tpl_lines[1:])
    tpl_after = parse_with("yaml", tpl_text)
    new_names = [k for k in tpl_after.get("providers", {})]
    live_providers = before.get("providers", {})
    if all(name in live_providers and live_providers[name] == tpl_after["providers"][name] for name in new_names):
        report["action"] = "noop-already-present"
        report["changed"] = False
        return None
    conflict = [n for n in new_names if n in live_providers and live_providers[n] != tpl_after["providers"][n]]
    if conflict:
        raise ApplyError(f"{spec['home']}: conflicting providers: {conflict}")
    lines = text.splitlines(keepends=True)
    eq_idx = None
    for i, line in enumerate(lines):
        if line.startswith("equivalence:"):
            eq_idx = i
            break
    if eq_idx is None:
        raise ApplyError(f"{spec['home']}: equivalence anchor not found")
    new_text = "".join(lines[:eq_idx]) + block + "".join(lines[eq_idx:])
    after = parse_with("yaml", new_text)
    if set(after.get("providers", {})) != set(live_providers) | set(new_names):
        raise ApplyError(f"{spec['home']}: provider key set assertion failed")
    if after.get("equivalence") != before.get("equivalence"):
        raise ApplyError(f"{spec['home']}: equivalence block changed")
    check_credential_preservation(text, new_text, spec["home"])
    report["action"] = "merge-omp"
    report["changed"] = True
    return [(home / spec["home"], new_text.encode(), spec["mode"])]


def plan_toml_splice(home: Path, spec, report):
    text = (home / spec["home"]).read_text()
    parse_with("toml", text)
    tpl_text = (TPL / spec["tpl"]).read_text()
    if not tpl_text.endswith("\n"):
        tpl_text += "\n"
    if spec["idempotent_marker"] in text:
        after_check = parse_with("toml", text)
        tpl_parsed = parse_with("toml", tpl_text)
        if spec["home"].endswith("kimi-code/config.toml"):
            ok = (
                all(
                    isinstance(after_check.get("providers", {}).get(k), dict)
                    and after_check["providers"][k] == tpl_parsed["providers"][k]
                    for k in ("omniroute-anthropic", "omniroute-chat")
                )
                and all(
                    after_check.get("models", {}).get(k) == tpl_parsed["models"][k]
                    for k in ("or-claude-fable", "or-gpt-5-6-sol")
                )
            )
        else:
            ok = (
                all(
                    isinstance(after_check.get("model_providers", {}).get(k), dict)
                    and after_check["model_providers"][k] == tpl_parsed["model_providers"][k]
                    for k in ("omniroute-anthropic", "omniroute-chat")
                )
                and after_check.get("model", {}).get("omniroute-sol") == tpl_parsed["model"]["omniroute-sol"]
                and after_check.get("model", {}).get("omniroute-claude-fable") == tpl_parsed["model"]["omniroute-claude-fable"]
            )
        if ok:
            report["action"] = "noop-already-present"
            report["changed"] = False
            return None
        raise ApplyError(f"{spec['home']}: idempotent marker present with conflicting content")
    remaining, removed = toml_remove_sections(text, spec["remove_headers"])
    if len(removed) != len(spec["remove_headers"]):
        raise ApplyError(
            f"{spec['home']}: expected {len(spec['remove_headers'])} removed sections, found {len(removed)}"
        )
    if not remaining.endswith("\n"):
        remaining += "\n"
    new_text = remaining + tpl_text
    after = parse_with("toml", new_text)
    before = parse_with("toml", text)
    for top in before:
        if top in ("model_providers", "models", "model", "providers"):
            continue
        if after.get(top) != before.get(top):
            raise ApplyError(f"{spec['home']}: unrelated top-level table changed: {top}")
    if spec["home"].endswith("kimi-code/config.toml"):
        if after.get("default_model") != before.get("default_model"):
            raise ApplyError(f"{spec['home']}: default_model changed")
        for prov in before.get("providers", {}):
            if after["providers"].get(prov) != before["providers"][prov]:
                raise ApplyError(f"{spec['home']}: existing provider table changed: {prov}")
        for k in before.get("models", {}):
            if k in spec_remove_alias_keys(spec) and after["models"].get(k) == before["models"][k]:
                raise ApplyError(f"{spec['home']}: alias {k} was not rebound")
            if k not in spec_remove_alias_keys(spec) and after["models"].get(k) != before["models"][k]:
                raise ApplyError(f"{spec['home']}: unrelated alias changed: {k}")
    else:
        for k in ("default", "session_summary", "web_search"):
            if after.get("models", {}).get(k) != before.get("models", {}).get(k):
                raise ApplyError(f"{spec['home']}: protected models.{k} changed")
        for prov in before.get("model_providers", {}):
            if after["model_providers"].get(prov) != before["model_providers"][prov]:
                raise ApplyError(f"{spec['home']}: existing model_provider table changed: {prov}")
    check_credential_preservation(text, new_text, spec["home"])
    report["action"] = "merge-toml"
    report["changed"] = True
    return [(home / spec["home"], new_text.encode(), spec["mode"])]


def spec_remove_alias_keys(spec):
    return {h.rsplit(".", 1)[-1].rstrip("]").replace("]", "") for h in spec["remove_headers"]}


def plan_cline_splice(home: Path, spec, report):
    text = (home / spec["home"]).read_text()
    before = parse_with("json", text)
    tpl = json.loads((TPL / spec["tpl"]).read_text())
    entry_key, entry = next(iter(tpl["providers"].items()))
    if entry_key in before.get("providers", {}):
        if before["providers"][entry_key] == entry:
            report["action"] = "noop-already-present"
            report["changed"] = False
            return None
        raise ApplyError(f"{spec['home']}: conflicting provider entry {entry_key}")
    tail = '    }\n  }\n}'
    if not text.endswith(tail + "\n"):
        raise ApplyError(f"{spec['home']}: providers closing structure not found")
    entry_lines = render_entry(entry_key, entry, 4)
    entry_lines[-1] = entry_lines[-1].rstrip(",")
    new_text = text[: -len(tail + "\n")] + "    },\n" + "".join(entry_lines) + "\n  }\n}\n"
    after = parse_with("json", new_text)
    if set(after["providers"]) != set(before["providers"]) | {entry_key}:
        raise ApplyError(f"{spec['home']}: provider key set assertion failed")
    for k in before["providers"]:
        if after["providers"][k] != before["providers"][k]:
            raise ApplyError(f"{spec['home']}: existing provider entry changed: {k}")
    for top in before:
        if top != "providers" and after.get(top) != before[top]:
            raise ApplyError(f"{spec['home']}: unrelated top-level key changed: {top}")
    check_credential_preservation(text, new_text, spec["home"])
    report["action"] = "merge-cline"
    report["changed"] = True
    return [(home / spec["home"], new_text.encode(), spec["mode"])]


PLANNERS = {
    "create": plan_create,
    "insert-providers": plan_insert_providers,
    "pi-merge": plan_pi_merge,
    "droid-upsert": plan_droid_upsert,
    "omp-splice": plan_omp_splice,
    "toml-splice": plan_toml_splice,
    "cline-splice": plan_cline_splice,
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--home", type=Path, default=HOME_DEFAULT)
    parser.add_argument("--target", action="append", choices=sorted(TARGETS))
    parser.add_argument("--allow-sensitive", action="store_true")
    parser.add_argument("--write", action="store_true", help="actually replace files (default: dry-run)")
    parser.add_argument("--allow-live", action="store_true",
                        help="permit --write against the real home (post-review gate)")
    parser.add_argument("--expect-sha", action="append", default=[],
                        help="path=sha256 expected-before guard (repeatable)")
    args = parser.parse_args()

    home = args.home.expanduser()
    if args.write and home == HOME_DEFAULT and not args.allow_live:
        print("FAIL --write against the real home requires --allow-live (review + rotation gates)")
        return 6
    names = args.target or [n for n, s in TARGETS.items() if not s.get("sensitive")]
    sensitive = [n for n in names if TARGETS[n].get("sensitive")]
    if sensitive and not (args.allow_sensitive and args.target):
        print("FAIL sensitive targets require BOTH --allow-sensitive and explicit --target:")
        for n in sensitive:
            print(f"  {n} (credential-rotation gate)")
        return 5
    expect = {}
    for item in args.expect_sha:
        p, _, h = item.partition("=")
        expect[str((home / p.lstrip("~/")).expanduser()) if not p.startswith("/") else p] = h

    results = []
    failed = False
    for name in names:
        spec = TARGETS[name]
        report = {"target": name, "path": str(home / spec["home"]), "changed": False}
        results.append(report)
        try:
            path = home / spec["home"]
            raw = path.read_bytes() if path.is_file() else b""
            report["exists_before"] = bool(raw)
            report["sha_before"] = sha_bytes(raw) if raw else None
            report["mode_before"] = oct(path.stat().st_mode & 0o777) if raw else None
            expected = expect.get(str(path))
            if expected is not None and (not raw or sha_bytes(raw) != expected):
                raise ApplyError(f"expected-before sha mismatch (live != expected)")
            writes = PLANNERS[spec["kind"]](home, spec, report)
            if writes:
                for wpath, wbytes, wmode in writes:
                    report["sha_after"] = sha_bytes(wbytes)
                    report["bytes_after"] = len(wbytes)
                    report["mode_after"] = oct(wmode)
                    if not args.write:
                        report["dry_run"] = True
                        continue
                    if wpath.is_file():
                        prior = wpath.read_bytes()
                    else:
                        prior = None
                    try:
                        parse_with(spec["parser"], wbytes.decode())
                        atomic_write(wpath, wbytes, wmode)
                        parse_with(spec["parser"], wpath.read_text())
                    except Exception:
                        if prior is not None:
                            atomic_write(wpath, prior, int(report["mode_before"], 8) if report["mode_before"] else 0o600)
                        raise
                    report["dry_run"] = False
        except ApplyError as exc:
            report["error"] = str(exc)
            failed = True
        except Exception as exc:  # noqa: BLE001
            report["error"] = f"{type(exc).__name__}: {exc}"
            failed = True

    payload = {
        "value_blind": True,
        "home": str(home),
        "write": args.write,
        "results": results,
        "summary": {
            "targets": len(results),
            "changed": sum(1 for r in results if r.get("changed")),
            "noop": sum(1 for r in results if r.get("action") == "noop-already-present"),
            "errors": sum(1 for r in results if "error" in r),
        },
    }
    if args.write and home == HOME_DEFAULT:
        # Evidence only for real-home applies; sandbox runs never pollute the
        # change's evidence directory. Results accumulate per run so later
        # per-target invocations never overwrite earlier evidence.
        out = EVID / "apply-overlays-results.json"
        if out.is_file():
            try:
                prev = json.loads(out.read_text())
            except Exception:
                prev = None
            if not isinstance(prev, dict) or not isinstance(prev.get("runs"), list):
                prev = None
        else:
            prev = None
        book = prev or {"value_blind": True, "runs": []}
        payload["run_index"] = len(book["runs"])
        book["runs"].append(payload)
        out.write_text(json.dumps(book, indent=1) + "\n")
    for r in results:
        status = "ERROR " + r["error"] if "error" in r else r.get("action", "?")
        print(f"TARGET {r['target']}: {status} changed={r.get('changed')}")
    print(f"SUMMARY {'FAIL' if failed else 'PASS'} "
          f"targets={payload['summary']['targets']} changed={payload['summary']['changed']} "
          f"noop={payload['summary']['noop']} errors={payload['summary']['errors']} "
          f"mode={'write' if args.write else 'dry-run'}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/opt/homebrew/bin/python3
"""Value-blind static acceptance checks for the OmniRoute dialect reconciliation.

This checker never prints credential values. It is intentionally separate from
live CLI probes: it verifies that the final user-level registrations bind the
requested model namespace to the intended provider dialect and that retired
active routes are absent. Runtime sentinels, thinking, tools, and defaults are
verified by the per-CLI acceptance runners in tasks.md.

Isolation: `--home` selects the configuration root (default: the real home),
`--dispositions` selects the retained fallback-proof record, and repeatable
`--check` selects a subset of checks (default: all). Fallback acceptance is
bound to the exact retained disposition record: native row id, route, native
endpoint path, failure class, fallback id, fallback endpoint path, fallback
return code, and fallback sentinel must all match. A proof for another CLI,
model, endpoint, or fallback id fails.

Claude Code's PM surface is owned by the archived change
`2026-08-30-add-claude-code-omniroute-pm-launcher` (applied live) and has no
checks here. The shell
opt-in check covers GitHub Copilot only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import tomllib
from pathlib import Path
from typing import Any, Callable

try:
    import yaml
except ImportError:  # pragma: no cover - the acceptance interpreter provides PyYAML
    yaml = None


def jsonc_load(path: Path) -> Any:
    text = path.read_text()
    out: list[str] = []
    i = 0
    in_string = False
    escaped = False
    while i < len(text):
        ch = text[i]
        if in_string:
            out.append(ch)
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
            i += 1
            continue
        if ch == '"':
            in_string = True
            out.append(ch)
            i += 1
            continue
        if ch == "/" and i + 1 < len(text) and text[i + 1] == "/":
            i += 2
            while i < len(text) and text[i] != "\n":
                i += 1
            continue
        if ch == "/" and i + 1 < len(text) and text[i + 1] == "*":
            i += 2
            while i + 1 < len(text) and text[i : i + 2] != "*/":
                i += 1
            i += 2
            continue
        out.append(ch)
        i += 1
    return json.loads("".join(out))


def check(label: str, ok: bool, detail: str = "") -> bool:
    print(f"CHECK {label}: {'PASS' if ok else 'FAIL'}" + (f" ({detail})" if detail else ""))
    return ok


def load_json(path: Path) -> Any | None:
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text())
    except Exception as exc:
        print(f"CHECK parse:{path}: FAIL ({type(exc).__name__})")
        return None


def load_toml(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        return tomllib.loads(path.read_text())
    except Exception as exc:
        print(f"CHECK parse:{path}: FAIL ({type(exc).__name__})")
        return None


def load_yaml(path: Path) -> Any | None:
    if not path.is_file():
        return None
    if yaml is not None:
        try:
            return yaml.safe_load(path.read_text())
        except Exception:
            return None
    ruby = "/usr/bin/ruby"
    try:
        completed = subprocess.run(
            [ruby, "-rjson", "-ryaml", "-e", "puts JSON.generate(YAML.load_file(ARGV[0]))", str(path)],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        return json.loads(completed.stdout) if completed.returncode == 0 else None
    except Exception:
        return None


def env_key_ok(value: Any) -> bool:
    return value in {"OMNIROUTE_API_KEY", "$OMNIROUTE_API_KEY", "${OMNIROUTE_API_KEY}", "{env:OMNIROUTE_API_KEY}"}


def provider_model_ids(provider: dict[str, Any]) -> set[str]:
    models = provider.get("models", [])
    if isinstance(models, dict):
        ids = set()
        for key, value in models.items():
            ids.add(str(value.get("id", key)) if isinstance(value, dict) else str(key))
        return ids
    if isinstance(models, list):
        return {str(value.get("id")) for value in models if isinstance(value, dict) and value.get("id")}
    return set()


# ---------------------------------------------------------------------------
# Retained fallback proofs: exact binding to cli-disposition-results.json.
# ---------------------------------------------------------------------------

DISPOSITIONS: dict[str, dict[str, Any]] = {}

PROOF_ROWS = {
    "omp": ("omp.sh.responses", "omp.sh.chat-fallback", "fbc-1-omp-responses-lifecycle-timeout"),
    "kimi-code": ("kimi-code.sh.responses", "kimi-code.sh.chat-fallback", "fbc-2-strict-decode-sequence-number"),
    "grok": ("grok.sh.responses", "grok.sh.chat-fallback", "fbc-3-serialization-sequence-number"),
    "goose": ("goose.sh.responses", "goose.sh.chat-fallback", "fbc-4-goose-responses-streaming-defect"),
    "cline": ("cline.sh.responses", "cline.chat-fallback", "fbc-5-native-provider-lockout"),
}


def load_dispositions(path: Path) -> None:
    """Validate the retained disposition record and index it by row id."""
    DISPOSITIONS.clear()
    if not path.is_file():
        raise SystemExit(f"dispositions record missing: {path}")
    data = json.loads(path.read_text())
    if not isinstance(data, dict):
        raise SystemExit("dispositions record must be an object")
    if data.get("value_blind") is not True:
        raise SystemExit("dispositions record must declare value_blind=true")
    if not isinstance(data.get("evidence_status"), str) or not data["evidence_status"]:
        raise SystemExit("dispositions record must declare evidence_status")
    if data.get("fresh_runtime_claim") is not False:
        raise SystemExit("dispositions record must declare fresh_runtime_claim=false (historical evidence)")
    rows = data.get("results")
    if not isinstance(rows, list) or not rows:
        raise SystemExit("dispositions record must contain a non-empty results array")
    for row in rows:
        if not isinstance(row, dict):
            raise SystemExit("every dispositions row must be an object")
        row_id = row.get("id")
        if not isinstance(row_id, str) or not row_id:
            raise SystemExit("every dispositions row requires an id")
        for field in ("route", "native_endpoint_path", "native_failure_class", "fallback_id", "fallback_endpoint_path"):
            if not isinstance(row.get(field), str):
                raise SystemExit(f"dispositions row {row_id} missing string field {field}")
        if not str(row.get("native_failure_class", "")).startswith("fbc-"):
            raise SystemExit(f"dispositions row {row_id} native_failure_class must be an fbc-* class")
        if not isinstance(row.get("fallback_returncode"), int) or not isinstance(row.get("fallback_sentinel"), bool):
            raise SystemExit(f"dispositions row {row_id} missing fallback_returncode/fallback_sentinel")
        source = row.get("source")
        if not isinstance(source, str) or not source:
            raise SystemExit(f"dispositions row {row_id} missing source")
        source_path = Path(__file__).resolve().parent.parent / source
        if not source_path.is_file():
            raise SystemExit(f"dispositions row {row_id} source missing on disk: {source}")
        recorded_source = row.get("source_sha256")
        if not isinstance(recorded_source, str) or not re.fullmatch(r"[0-9a-f]{64}", recorded_source):
            raise SystemExit(f"dispositions row {row_id} source_sha256 is malformed")
        if hashlib.sha256(source_path.read_bytes()).hexdigest() != recorded_source:
            raise SystemExit(f"dispositions row {row_id} source_sha256 does not match the referenced evidence file")
        if row_id in DISPOSITIONS:
            raise SystemExit(f"duplicate dispositions row id: {row_id}")
        DISPOSITIONS[row_id] = row


def fallback_proven(product: str) -> bool:
    """Exact proof binding: the retained record for this CLI's native failure.

    The configured route is acceptable as a chat fallback only when the
    retained isolated-probe record proves this exact CLI's native failure
    (matching row id, route, native endpoint, and FBC class) and this exact
    fallback (matching fallback id, versionless endpoint, rc 0, and sentinel).
    A proof for any other CLI, model, endpoint, or fallback id fails.
    """
    native_id, fallback_id, fbc_class = PROOF_ROWS[product]
    record = DISPOSITIONS.get(native_id)
    if record is None:
        return False
    return (
        record.get("route") == "sh/gpt-5.6-sol"
        and record.get("native_endpoint_path") == "/v1/responses"
        and record.get("native_failure_class") == fbc_class
        and record.get("fallback_id") == fallback_id
        and record.get("fallback_endpoint_path") == "/chat/completions"
        and record.get("fallback_returncode") == 0
        and record.get("fallback_sentinel") is True
    )


# ---------------------------------------------------------------------------
# Per-CLI checks. Every check receives the isolated home root.
# ---------------------------------------------------------------------------


def check_pi(home: Path) -> bool:
    path = home / ".pi/agent/models.json"
    data = load_json(path)
    if not isinstance(data, dict):
        return check("pi.exists-parse", False)
    providers = data.get("providers", {})
    pm = [
        p for p in providers.values()
        if isinstance(p, dict)
        and p.get("api") == "anthropic-messages"
        and p.get("baseUrl") == "http://localhost:20128"
        and env_key_ok(p.get("apiKey"))
        and "pm/Claude-Fable" in provider_model_ids(p)
    ]
    sh = [
        p for p in providers.values()
        if isinstance(p, dict)
        and p.get("api") == "openai-responses"
        and p.get("baseUrl") == "http://localhost:20128/v1"
        and env_key_ok(p.get("apiKey"))
        and "sh/gpt-5.6-sol" in provider_model_ids(p)
        and "sh/Claude-Fable" not in provider_model_ids(p)
    ]
    return check("pi.pm.messages", bool(pm)) and check("pi.sh.responses", bool(sh))


def check_prime(home: Path) -> bool:
    path = home / ".prime/agent/models.json"
    data = load_json(path)
    if not isinstance(data, dict):
        return check("prime.exists-parse", False)
    providers = data.get("providers", {})
    pm = [
        p for p in providers.values()
        if isinstance(p, dict)
        and p.get("api") == "anthropic-messages"
        and p.get("baseUrl") == "http://localhost:20128"
        and env_key_ok(p.get("apiKey"))
        and "pm/Claude-Fable" in provider_model_ids(p)
    ]
    sh = [
        p for p in providers.values()
        if isinstance(p, dict)
        and p.get("api") == "openai-responses"
        and p.get("baseUrl") == "http://localhost:20128/v1"
        and env_key_ok(p.get("apiKey"))
        and "sh/gpt-5.6-sol" in provider_model_ids(p)
        and "sh/Claude-Fable" not in provider_model_ids(p)
    ]
    return check("prime.pm.messages", bool(pm)) and check("prime.sh.responses", bool(sh))


def check_opencode(home: Path) -> bool:
    path = home / ".config/opencode/opencode.json"
    data = load_json(path)
    providers = data.get("provider", {}) if isinstance(data, dict) else {}
    pm = [
        p for p in providers.values()
        if isinstance(p, dict)
        and p.get("npm") == "@ai-sdk/anthropic"
        and isinstance(p.get("options"), dict)
        and p["options"].get("baseURL") == "http://localhost:20128/v1"
        and env_key_ok(p["options"].get("apiKey"))
        and "pm/Claude-Fable" in provider_model_ids(p)
    ]
    sh = [
        p for p in providers.values()
        if isinstance(p, dict)
        and p.get("npm") == "@ai-sdk/openai"
        and isinstance(p.get("options"), dict)
        and p["options"].get("baseURL") == "http://localhost:20128/v1"
        and env_key_ok(p["options"].get("apiKey"))
        and "sh/gpt-5.6-sol" in provider_model_ids(p)
        and "sh/Claude-Fable" not in provider_model_ids(p)
    ]
    return check("opencode.pm.messages-sdk", bool(pm)) and check("opencode.sh.responses-sdk", bool(sh))


def check_kilo(home: Path) -> bool:
    path = home / ".config/kilo/kilo.jsonc"
    if not path.is_file():
        return check("kilo.exists-parse", False)
    try:
        data = jsonc_load(path)
    except Exception as exc:
        return check("kilo.exists-parse", False, type(exc).__name__)
    providers = data.get("provider", {}) if isinstance(data, dict) else {}
    pm = [
        p for p in providers.values()
        if isinstance(p, dict)
        and p.get("npm") == "@ai-sdk/anthropic"
        and isinstance(p.get("options"), dict)
        and p["options"].get("baseURL") == "http://localhost:20128/v1"
        and env_key_ok(p["options"].get("apiKey"))
        and "pm/Claude-Fable" in provider_model_ids(p)
    ]
    sh = [
        p for p in providers.values()
        if isinstance(p, dict)
        and p.get("npm") == "@ai-sdk/openai"
        and isinstance(p.get("options"), dict)
        and p["options"].get("baseURL") == "http://localhost:20128/v1"
        and env_key_ok(p["options"].get("apiKey"))
        and "sh/gpt-5.6-sol" in provider_model_ids(p)
        and "sh/Claude-Fable" not in provider_model_ids(p)
    ]
    return check("kilo.pm.messages-sdk", bool(pm)) and check("kilo.sh.responses-sdk", bool(sh))


def check_droid(home: Path) -> bool:
    path = home / ".factory/settings.json"
    data = load_json(path)
    models = data.get("customModels", []) if isinstance(data, dict) else []
    pm = [
        m for m in models
        if isinstance(m, dict)
        and m.get("model") == "pm/Claude-Fable"
        and m.get("provider") == "anthropic"
        and m.get("baseUrl") == "http://localhost:20128"
        and env_key_ok(m.get("apiKey"))
    ]
    sh = [
        m for m in models
        if isinstance(m, dict)
        and m.get("model") == "sh/gpt-5.6-sol"
        and m.get("provider") == "openai"
        and m.get("baseUrl") == "http://localhost:20128/v1"
        and env_key_ok(m.get("apiKey"))
    ]
    # Droid's SH route is native Responses (isolated probe CANDIDATE_DROID_SH_OK);
    # no chat-fallback branch is accepted for it.
    return check("droid.pm.anthropic", bool(pm)) and check("droid.sh.responses", bool(sh))


def check_kimi(home: Path) -> bool:
    path = home / ".kimi-code/config.toml"
    data = load_toml(path)
    if not isinstance(data, dict):
        return check("kimi-code.exists-parse", False)
    providers = data.get("providers", {})
    models = data.get("models", {})
    if not isinstance(providers, dict) or not isinstance(models, dict):
        return check("kimi-code.exists-parse", False)

    def alias_model(alias: Any) -> str | None:
        return alias.get("model") if isinstance(alias, dict) else None

    def alias_provider(alias: Any) -> str | None:
        return alias.get("provider") if isinstance(alias, dict) else None

    def provider_of(name: Any) -> dict[str, Any]:
        p = providers.get(name)
        return p if isinstance(p, dict) else {}

    # PM: an alias must bind an Anthropic provider at the versionless base.
    pm_ok = any(
        alias_model(a) == "pm/Claude-Fable"
        and provider_of(alias_provider(a)).get("type") == "anthropic"
        and provider_of(alias_provider(a)).get("base_url") == "http://localhost:20128"
        for a in models.values()
    )
    # Dormant failed-native Responses provider: may exist, nothing may select it.
    responses_provider_names = {
        name for name, p in providers.items()
        if isinstance(p, dict) and p.get("type") == "openai_responses" and p.get("base_url") == "http://localhost:20128/v1"
    }
    active_sh_aliases = [a for a in models.values() if alias_model(a) == "sh/gpt-5.6-sol"]
    sh_alias_selects_dormant = any(
        alias_provider(a) in responses_provider_names
        for a in active_sh_aliases
    )
    # Active SH: every SH alias must bind a versionless chat provider, and at
    # least one SH alias must exist (provider presence alone is not proof).
    sh_aliases_ok = bool(active_sh_aliases) and all(
        provider_of(alias_provider(a)).get("type") == "openai"
        and provider_of(alias_provider(a)).get("base_url") == "http://localhost:20128"
        for a in active_sh_aliases
    )
    no_wrong_sh = not any(
        alias_model(a) == "sh/Claude-Fable"
        and provider_of(alias_provider(a)).get("type") in {"openai_responses", "openai"}
        for a in models.values()
    )
    sh_ok = sh_aliases_ok and not sh_alias_selects_dormant and fallback_proven("kimi-code")
    mode_ok = path.is_file() and (path.stat().st_mode & 0o777) == 0o600
    return (
        check("kimi-code.pm.messages", pm_ok)
        and check("kimi-code.sh.responses-or-proven-chat-fallback", sh_ok)
        and check("kimi-code.no-sh-claude-on-openai-providers", no_wrong_sh)
        and check("kimi-code.literal-key-exception-mode", mode_ok)
    )


def check_codex(home: Path) -> bool:
    path = home / ".codex/config.toml"
    profile_path = home / ".codex/omniroute.config.toml"
    data = load_toml(path)
    profile = load_toml(profile_path)
    providers = data.get("model_providers", {}) if isinstance(data, dict) else {}
    provider = providers.get("omniroute", {}) if isinstance(providers, dict) else {}
    profile_provider = profile.get("model_providers", {}).get("omniroute", {}) if isinstance(profile, dict) else {}
    profile_binding_ok = (
        isinstance(profile, dict)
        and profile.get("model") == "sh/gpt-5.6-sol"
        and profile.get("model_provider") == "omniroute"
    )
    baseline_manifest = load_json(Path(__file__).with_name("pre-apply-manifest.json")) or {}
    baseline_defaults = baseline_manifest.get("defaults", {}) if isinstance(baseline_manifest, dict) else {}
    default_preserved = (
        isinstance(data, dict)
        and data.get("model_provider") == baseline_defaults.get("codex.model_provider")
        and data.get("model") == baseline_defaults.get("codex.model")
    )
    ok = (
        isinstance(provider, dict)
        and provider.get("wire_api") == "responses"
        and provider.get("base_url") == "http://localhost:20128/v1"
        and provider.get("env_key") == "OMNIROUTE_API_KEY"
        and isinstance(profile_provider, dict)
        and profile_provider.get("wire_api") == "responses"
        and profile_provider.get("base_url") == "http://localhost:20128/v1"
        and profile_provider.get("env_key") == "OMNIROUTE_API_KEY"
        and profile_binding_ok
        and default_preserved
    )
    return check("codex.sh.responses-selectable-profile-default-preserved", ok)


def check_grok(home: Path) -> bool:
    path = home / ".grok/config.toml"
    data = load_toml(path)
    if not isinstance(data, dict):
        return check("grok.exists-parse", False)
    providers = data.get("model_providers", {})
    aliases = data.get("model", {})
    pm_provider_names = {v.get("model_provider") for v in aliases.values() if isinstance(v, dict) and v.get("model") == "pm/Claude-Fable"}
    sh_provider_names = {v.get("model_provider") for v in aliases.values() if isinstance(v, dict) and v.get("model") == "sh/gpt-5.6-sol"}
    pm_ok = any(
        isinstance(providers.get(n), dict)
        and providers[n].get("api_backend") == "messages"
        and providers[n].get("base_url") == "http://localhost:20128/v1"
        for n in pm_provider_names
    )
    sh_ok = any(
        isinstance(providers.get(n), dict)
        and providers[n].get("api_backend") == "responses"
        and providers[n].get("base_url") == "http://localhost:20128/v1"
        for n in sh_provider_names
    )
    fallback_ok = any(
        isinstance(providers.get(n), dict)
        and providers[n].get("api_backend") == "chat_completions"
        and providers[n].get("base_url") == "http://localhost:20128"
        and fallback_proven("grok")
        for n in sh_provider_names
    )
    return check("grok.pm.messages", pm_ok) and check("grok.sh.responses-or-proven-chat-fallback", sh_ok or fallback_ok)


def check_goose(home: Path) -> bool:
    directory = home / ".config/goose/custom_providers"
    pm_ok = False
    sh_native = False
    sh_fallback = False
    fallback_provider_seen = False
    if directory.is_dir():
        for path in directory.glob("*.json"):
            data = load_json(path)
            if not isinstance(data, dict):
                continue
            names = {m.get("name") for m in data.get("models", []) if isinstance(m, dict)}
            api_key_ok = data.get("api_key_env") == "OMNIROUTE_API_KEY"
            base_url = data.get("base_url")
            base_path = data.get("base_path")
            if data.get("name") == "custom_omniroute_sh":
                fallback_provider_seen = True
            if "pm/Claude-Fable" in names and api_key_ok and data.get("engine") == "anthropic":
                pm_ok = pm_ok or base_url == "http://localhost:20128"
            if "sh/gpt-5.6-sol" in names and api_key_ok and data.get("engine") == "openai":
                native = base_url == "http://localhost:20128/v1" and base_path in (None, "v1/responses")
                fallback = (
                    base_url == "http://localhost:20128/v1"
                    and base_path == "chat/completions"
                    and fallback_proven("goose")
                )
                sh_native = sh_native or native
                sh_fallback = sh_fallback or fallback
    sh_ok = sh_fallback if fallback_provider_seen else sh_native
    return check("goose.pm.anthropic", pm_ok) and check("goose.sh.responses-or-proven-chat-fallback", sh_ok)


def check_omp(home: Path) -> bool:
    path = home / ".omp/agent/models.yml"
    if not path.is_file():
        return check("omp.exists", False)
    pm_ok = False
    sh_native = False
    sh_fallback = False
    fallback_provider_seen = False
    try:
        data = load_yaml(path)
    except Exception:
        data = None
    providers = data.get("providers", {}) if isinstance(data, dict) else {}
    if isinstance(providers, dict):
        for provider in providers.values():
            if not isinstance(provider, dict):
                continue
            ids = {m.get("id") for m in provider.get("models", []) if isinstance(m, dict)}
            key_ok = provider.get("apiKey") == "OMNIROUTE_API_KEY"
            if "pm/Claude-Fable" in ids:
                pm_ok = pm_ok or (
                    provider.get("api") == "anthropic-messages"
                    and provider.get("baseUrl") == "http://localhost:20128"
                    and key_ok
                )
            if "sh/gpt-5.6-sol" in ids and provider.get("api") == "openai-completions":
                fallback_provider_seen = True
            if "sh/gpt-5.6-sol" in ids and key_ok:
                sh_native = sh_native or (
                    provider.get("api") == "openai-responses"
                    and provider.get("baseUrl") == "http://localhost:20128/v1"
                    and "sh/Claude-Fable" not in ids
                )
                sh_fallback = sh_fallback or (
                    provider.get("api") == "openai-completions"
                    and provider.get("baseUrl") == "http://localhost:20128"
                    and "sh/Claude-Fable" not in ids
                    and fallback_proven("omp")
                )
    sh_ok = sh_fallback if fallback_provider_seen else sh_native
    return check("omp.pm.messages", pm_ok) and check("omp.sh.responses-or-proven-chat-fallback", sh_ok)


def check_cline(home: Path) -> bool:
    path = home / ".cline/data/settings/providers.json"
    data = load_json(path)
    providers = data.get("providers", {}) if isinstance(data, dict) else {}
    fallback = False
    cross_dialect_pm = False
    for value in providers.values() if isinstance(providers, dict) else []:
        settings = value.get("settings", {}) if isinstance(value, dict) else {}
        if isinstance(settings, dict) and settings.get("model") == "pm/Claude-Fable" and settings.get("provider") in {"openai-compatible", "openai-native"}:
            cross_dialect_pm = True
        fallback = fallback or (
            isinstance(settings, dict)
            and settings.get("provider") == "openai-compatible"
            and settings.get("model") == "sh/gpt-5.6-sol"
            and settings.get("baseUrl") == "http://localhost:20128"
        )
    return check("cline.sh.proven-chat-fallback", fallback and not cross_dialect_pm and fallback_proven("cline"))


def check_shell_byo(home: Path) -> bool:
    # GitHub Copilot opt-in only, deferral-aware. The persistent .zshrc
    # launcher binding is DEFERRED (drift-provenance.md: .zshrc is protected by
    # other active changes); the proven route is environment opt-in — the
    # retained probes (CANDIDATE_COPILOT_PM_OK / CANDIDATE_COPILOT_SH_OK)
    # passed via env_set, not via .zshrc. The checker therefore asserts only
    # that the preserved COPILOT opt-in surface (the provider type and base
    # URL hook identifiers) remains present. It must not require an applied
    # OmniRoute model binding and never invents a .zshrc write.
    # Claude Code's launcher surface is owned by the archived
    # 2026-08-30-add-claude-code-omniroute-pm-launcher change.
    path = home / ".zshrc"
    if not path.is_file():
        return check("shell.copilot-opt-in-surface-preserved", False)
    text = path.read_text()
    copilot = "COPILOT_PROVIDER_TYPE" in text and "COPILOT_PROVIDER_BASE_URL" in text
    return check("shell.copilot-opt-in-surface-preserved", copilot)


def check_modes(home: Path) -> bool:
    # Active files with literal credentials or credential-bearing provider
    # selectors are mode 600. Env-reference-only catalog files may retain their
    # existing mode; their mode-600 rollback backups are checked separately.
    paths = [
        home / ".codex/config.toml",
        home / ".grok/config.toml",
        home / ".kimi-code/config.toml",
        home / ".config/kilo/kilo.jsonc",
        home / ".config/opencode/opencode.json",
        home / ".pi/agent/models.json",
        home / ".prime/agent/models.json",
        home / ".cline/data/settings/providers.json",
    ]
    bad = [str(path) for path in paths if path.is_file() and (path.stat().st_mode & 0o777) != 0o600]
    return check("credential-bearing-targets-mode-600", not bad)


def check_grok_credentials(home: Path) -> bool:
    data = load_toml(home / ".grok/config.toml")
    if not isinstance(data, dict):
        return check("grok.omniroute-credential-ref", False)
    providers = data.get("model_providers", {})
    aliases = data.get("model", {})
    names = {
        v.get("model_provider") for v in aliases.values()
        if isinstance(v, dict) and v.get("model") in {"pm/Claude-Fable", "sh/gpt-5.6-sol"}
    }
    ok = bool(names) and all(isinstance(providers.get(name), dict) and providers[name].get("env_key") == "OMNIROUTE_API_KEY" for name in names)
    return check("grok.omniroute-credential-ref", ok)


def check_codex_credentials(home: Path) -> bool:
    data = load_toml(home / ".codex/config.toml")
    provider = data.get("model_providers", {}).get("omniroute", {}) if isinstance(data, dict) else {}
    return check("codex.omniroute-credential-ref", isinstance(provider, dict) and provider.get("env_key") == "OMNIROUTE_API_KEY")


def check_omp_credentials(home: Path) -> bool:
    path = home / ".omp/agent/models.yml"
    try:
        data = load_yaml(path)
    except Exception:
        data = None
    providers = data.get("providers", {}) if isinstance(data, dict) else {}
    pm = any(
        isinstance(p, dict)
        and p.get("api") == "anthropic-messages"
        and p.get("apiKey") == "OMNIROUTE_API_KEY"
        and any(isinstance(m, dict) and m.get("id") == "pm/Claude-Fable" for m in p.get("models", []))
        for p in providers.values()
    )
    sh = any(
        isinstance(p, dict)
        and p.get("apiKey") == "OMNIROUTE_API_KEY"
        and p.get("api") in {"openai-responses", "openai-completions"}
        and any(isinstance(m, dict) and m.get("id") == "sh/gpt-5.6-sol" for m in p.get("models", []))
        for p in providers.values()
    )
    return check("omp.omniroute-credential-ref", pm and sh)


def check_active_dlg(home: Path) -> bool:
    paths = [home / ".kimi-code/config.toml", home / ".omp/agent/models.yml", home / ".codex/config.toml", home / ".grok/config.toml", home / ".factory/settings.json", home / ".pi/agent/models.json", home / ".prime/agent/models.json", home / ".config/opencode/opencode.json", home / ".config/kilo/kilo.jsonc"]
    bad = [str(p) for p in paths if p.is_file() and "dlg/" in p.read_text(errors="replace")]
    return check("active-no-dlg-routes", not bad)


CHECK_REGISTRY: list[tuple[str, Callable[[Path], bool]]] = [
    ("pi", check_pi),
    ("prime", check_prime),
    ("opencode", check_opencode),
    ("kilo", check_kilo),
    ("droid", check_droid),
    ("kimi", check_kimi),
    ("codex", check_codex),
    ("grok", check_grok),
    ("goose", check_goose),
    ("omp", check_omp),
    ("cline", check_cline),
    ("shell-byo", check_shell_byo),
    ("modes", check_modes),
    ("grok-credentials", check_grok_credentials),
    ("codex-credentials", check_codex_credentials),
    ("omp-credentials", check_omp_credentials),
    ("active-dlg", check_active_dlg),
]


def selected_checks(names: list[str]) -> list[tuple[str, Callable[[Path], bool]]]:
    known = {name for name, _ in CHECK_REGISTRY}
    unknown = [name for name in names if name not in known]
    if unknown:
        raise SystemExit(f"unknown check names: {unknown}; known: {sorted(known)}")
    return [(name, fn) for name, fn in CHECK_REGISTRY if not names or name in set(names)]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--home", type=Path, default=Path.home())
    parser.add_argument("--dispositions", type=Path, default=Path(__file__).with_name("cli-disposition-results.json"))
    parser.add_argument("--check", action="append", default=[], help="run only the named check (repeatable)")
    parser.add_argument("--phase", choices=["baseline", "candidate"], default="candidate")
    args = parser.parse_args()
    load_dispositions(args.dispositions)
    checks = selected_checks(args.check)
    print(f"ROUTE_CONTRACT_CHECK phase={args.phase} home={args.home} checks={[name for name, _ in checks]} value_blind=true")

    results = [fn(args.home) for _, fn in checks]
    candidate_state_green = all(results)

    if args.phase == "baseline":
        # Pre-apply state is valid evidence only when the candidate contract is
        # not already green. The nonzero status is retained as fail-to-pass
        # evidence.
        print(
            "BASELINE_NEGATIVE_CONTROL "
            f"candidate_contract={'PASS' if candidate_state_green else 'FAIL'} "
            "expected=FAIL"
        )
        result = 0 if candidate_state_green else 1
        print(f"SUMMARY {'PASS' if result == 0 else 'FAIL'} phase=baseline checks={len(checks)}")
        return result

    print(f"SUMMARY {'PASS' if candidate_state_green else 'FAIL'} checks={len(checks)}")
    return 0 if candidate_state_green else 1


if __name__ == "__main__":
    raise SystemExit(main())

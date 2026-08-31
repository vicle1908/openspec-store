#!/opt/homebrew/bin/python3
"""Bounded probe: Codex selectable standalone profile mechanism (codex 0.149.0).

v6 — fast-fail local control. The base config's default provider references an
environment variable that is deliberately absent from the child environment
(`CODEX_PROFILE_NEGATIVE_CONTROL_KEY`), so arms that do not select the profile
fail quickly and naturally with no network dependence:

  positive — base + omniroute.config.toml + `--profile omniroute`: the layered
             profile overrides the default and reaches OmniRoute.
             Acceptance: rc == 0 and an event string equal (post-strip) to the
             exact sentinel.
  negative — profile file absent, flag used: the missing local-control env
             reference fails fast. Acceptance: rc not in {0, 124}, no exact
             sentinel, no public-host contact observed.
  control  — profile file present, NO flag: profile is not layered, so the
             missing env reference applies. Acceptance: rc not in {0, 124}, no
             exact sentinel — proving the standalone file is inert without
             selection.

Detection is exact post-strip string equality over text/message/content values
collected from JSONL events (`exact_response_sentinel`, not speaker
classification). Value-blind: the OmniRoute credential exists only in the child
environment; only rc, sentinel booleans, and event counts are retained; no raw
output, request IDs, or response bodies are retained. The public-host scan is
observational (hostnames in retained output), not a network-level proof.
"""
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

CHG = Path("/Users/androidteam/Developer/openspec-store/openspec/changes/reconcile-omniroute-native-dialects")
TEMPLATE = CHG / "evidence/candidate-templates/.codex/omniroute.config.toml"
BIN = ""
BINARY_VERSION = ""


def resolve_binary() -> None:
    """Resolve codex with the same semantics as evidence/inventory-check.py.

    The tested binary is whatever `zsh -lc 'command -v codex'` resolves to
    (realpath), so the probe always exercises the inventory-checked active
    installation instead of a stale hardcoded path.
    """
    global BIN, BINARY_VERSION
    resolved = subprocess.run(
        ["zsh", "-lc", "command -v codex"],
        capture_output=True, text=True, timeout=15,
    ).stdout.strip().splitlines()[0]
    if not resolved:
        raise SystemExit("codex not found under zsh -lc PATH resolution")
    BIN = os.path.realpath(resolved)
    version_lines = subprocess.run(
        [resolved, "--version"], capture_output=True, text=True, timeout=30,
    ).stdout.strip().splitlines()
    BINARY_VERSION = version_lines[0] if version_lines else "unknown"

SENTINEL = "CANDIDATE_CODEX_PROFILE_MECHANISM_OK"
PROMPT = "Reply with exactly: " + SENTINEL
BASE_CONFIG = (
    "# probe base config: default provider fails fast via an absent env reference\n"
    'sandbox_mode = "read-only"\n'
    'model = "sh/gpt-5.6-sol"\n'
    'model_provider = "local-control"\n'
    "\n"
    "[model_providers.local-control]\n"
    'name = "local-control"\n'
    'base_url = "http://127.0.0.1:9/"\n'
    'env_key = "CODEX_PROFILE_NEGATIVE_CONTROL_KEY"\n'
    'wire_api = "responses"\n'
)
PUBLIC_HOSTS = ("api.openai.com", "api.anthropic.com")
TRAFFIC_NOTE = (
    "no public-host contact observed in retained output; both failing arms were "
    "configured for a local-control provider whose env reference is absent from "
    "the child environment; the hostname scan is observational, not a "
    "network-level proof"
)


def collect_strings(value, out):
    if isinstance(value, dict):
        for key, item in value.items():
            if key in ("text", "message", "content") and isinstance(item, str):
                out.append(item)
            else:
                collect_strings(item, out)
    elif isinstance(value, list):
        for item in value:
            collect_strings(item, out)


def run_arm(home: Path, use_profile: bool, timeout: int = 180) -> dict:
    argv = [BIN, "exec", "--ephemeral", "--skip-git-repo-check", "--sandbox", "read-only", "-C", str(home), "--json"]
    if use_profile:
        argv += ["--profile", "omniroute"]
    argv.append(PROMPT)
    key = subprocess.run(
        ["zsh", "-lc", 'source ~/.zshenv >/dev/null 2>&1; printf %s "$OMNIROUTE_API_KEY"'],
        capture_output=True, text=True, timeout=15,
    ).stdout
    if not key:
        return {"rc": 70, "exact_response_sentinel": False, "user_echo_sentinel": None, "event_count": 0, "public_host_seen": None}
    env = {
        "HOME": str(Path.home()),
        "PATH": "/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin",
        "TERM": "dumb",
        "LANG": "en_US.UTF-8",
        "LC_ALL": "en_US.UTF-8",
        "OMNIROUTE_API_KEY": key,
        "CODEX_HOME": str(home),
        # CODEX_PROFILE_NEGATIVE_CONTROL_KEY deliberately absent.
    }
    try:
        p = subprocess.run(argv, capture_output=True, text=True, timeout=timeout, env=env)
        rc, raw = p.returncode, (p.stdout or "") + "\n" + (p.stderr or "")
    except subprocess.TimeoutExpired:
        rc, raw = 124, ""
    events = []
    for line in raw.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            events.append(json.loads(line))
        except ValueError:
            continue
    texts = []
    for event in events:
        collect_strings(event, texts)
    return {
        "rc": rc,
        "exact_response_sentinel": any(t.strip() == SENTINEL for t in texts),
        "user_echo_sentinel": any(PROMPT in t for t in texts),
        "event_count": len(events),
        "public_host_seen": any(host in raw for host in PUBLIC_HOSTS),
    }


def main() -> int:
    assert TEMPLATE.is_file(), "candidate template missing"
    resolve_binary()
    print(f"RESOLVED binary={BIN} version={BINARY_VERSION}")
    homes = {}
    for name in ("pos", "neg", "ctrl"):
        homes[name] = Path(tempfile.mkdtemp(prefix=f"codex-profile-{name}-", dir="/private/tmp"))
    try:
        for home in homes.values():
            (home / "config.toml").write_text(BASE_CONFIG)
        for name in ("pos", "ctrl"):
            (homes[name] / "omniroute.config.toml").write_text(TEMPLATE.read_text())

        pos = run_arm(homes["pos"], use_profile=True)
        neg = run_arm(homes["neg"], use_profile=True, timeout=120)
        ctrl = run_arm(homes["ctrl"], use_profile=False, timeout=120)

        pos_ok = pos["rc"] == 0 and pos["exact_response_sentinel"] is True
        neg_ok = neg["rc"] not in {0, 124} and neg["exact_response_sentinel"] is False and neg["public_host_seen"] is False
        ctrl_ok = ctrl["rc"] not in {0, 124} and ctrl["exact_response_sentinel"] is False and ctrl["public_host_seen"] is False
        verdict = "PASS" if (pos_ok and neg_ok and ctrl_ok) else "FAIL"

        for label, res in (("POSITIVE", pos), ("NEGATIVE", neg), ("CONTROL-no-flag", ctrl)):
            print(f"{label} rc={res['rc']} exact_response_sentinel={res['exact_response_sentinel']} "
                  f"user_echo={res.get('user_echo_sentinel')} events={res.get('event_count')} "
                  f"public_host={res.get('public_host_seen')}")
        print("VERDICT:", verdict)

        report = {
            "probe": "codex-profile-mechanism-v6-fast-fail",
            "binary": BIN,
            "binary_version": BINARY_VERSION,
            "binary_resolution": "zsh -lc 'command -v codex' + realpath (matches inventory-check.py)",
            "detection": "codex exec --json; exact post-strip equality of an event string (not speaker classification)",
            "negative_control": "base default provider env_key CODEX_PROFILE_NEGATIVE_CONTROL_KEY deliberately absent from the child environment",
            "traffic_note": TRAFFIC_NOTE,
            "template": str(TEMPLATE),
            "sentinel": SENTINEL,
            "arms": {
                "positive_profile_present_flag_used": {
                    "rc": pos["rc"], "exact_response_sentinel": pos["exact_response_sentinel"],
                    "user_echo_sentinel": pos["user_echo_sentinel"],
                },
                "negative_profile_absent_flag_used": {
                    "rc": neg["rc"], "exact_response_sentinel": neg["exact_response_sentinel"],
                    "user_echo_sentinel": neg["user_echo_sentinel"],
                    "public_host_contact_observed": neg["public_host_seen"],
                },
                "control_profile_present_no_flag": {
                    "rc": ctrl["rc"], "exact_response_sentinel": ctrl["exact_response_sentinel"],
                    "user_echo_sentinel": ctrl["user_echo_sentinel"],
                    "public_host_contact_observed": ctrl["public_host_seen"],
                },
            },
            "verdict": verdict,
            "value_blind": True,
        }
        out_path = CHG / "evidence/codex-profile-mechanism-result.json"
        out_path.write_text(json.dumps(report, indent=2) + "\n")
        print("WROTE", out_path)
        return 0 if verdict == "PASS" else 1
    finally:
        for home in homes.values():
            shutil.rmtree(home, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())

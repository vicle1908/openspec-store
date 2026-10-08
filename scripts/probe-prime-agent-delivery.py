#!/usr/bin/env python3
"""Reusable probe script for verifying harness system-prompt delivery.

Evaluates whether a model/provider registration delivers the harness system
prompt or discards/ignores it.

Supports:
- OpenAI Responses API (openai-responses)
- Anthropic Messages API (anthropic-messages)

Safety & Governance:
- Value-blind: Never prints credentials, raw auth headers, or request bodies.
- Sanitized error reporting: Emits only error classes and HTTP status codes, never raw error messages.
- Shell-evaluated environment resolution: Evaluates safe environment variable names via zsh -lc.
  Missing variables fail closed; literal credentials safely distinguished without arbitrary file grepping.
- Exact protocol fields: Single authoritative system instruction field per dialect, no duplicates.
- Paired control/challenge: Baseline and challenge use the identical user query to prevent false signals.
  Nonce is delivered strictly through system prompt; negative control verifies zero nonce hallucination.
- Secure transport: Safe redirect handling prevents credential leakage; responses and timeouts bounded.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import secrets
import socket
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional, Tuple

SAFE_ENV_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
MAX_RESPONSE_BYTES = 10 * 1024 * 1024  # 10 MB bound to prevent memory exhaustion
SENSITIVE_HEADERS = {"authorization", "x-api-key", "proxy-authorization", "cookie"}


class SafeRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Prevent credential and header leakage across HTTP redirects."""

    def redirect_request(
        self,
        req: urllib.request.Request,
        fp: Any,
        code: int,
        msg: str,
        headers: Any,
        newurl: str,
    ) -> Optional[urllib.request.Request]:
        orig_parsed = urllib.parse.urlsplit(req.full_url)
        new_parsed = urllib.parse.urlsplit(newurl)

        # Forbid cross-origin redirects
        if orig_parsed.netloc != new_parsed.netloc:
            return None

        # Forbid HTTPS to HTTP downgrade
        if orig_parsed.scheme == "https" and new_parsed.scheme != "https":
            return None

        # Forbid redirects to schemes other than http and https
        if new_parsed.scheme not in ("http", "https"):
            return None

        new_req = super().redirect_request(req, fp, code, msg, headers, newurl)
        if new_req:
            # Strip sensitive headers across redirects case-insensitively
            for h in list(new_req.headers.keys()):
                if h.lower() in SENSITIVE_HEADERS:
                    del new_req.headers[h]
            for h in list(getattr(new_req, "unredirected_hdrs", {}).keys()):
                if h.lower() in SENSITIVE_HEADERS:
                    del new_req.unredirected_hdrs[h]
        return new_req


def parse_token_count(val: Any) -> Optional[int]:
    """Validate and convert token count to non-negative integer.

    Fails closed (returns None) for booleans, negative numbers, non-finite floats,
    fractional floats, and malformed types.
    """
    if val is None or isinstance(val, bool):
        return None
    if isinstance(val, int):
        return val if val >= 0 else None
    if isinstance(val, float):
        if not math.isfinite(val) or not val.is_integer():
            return None
        val_int = int(val)
        return val_int if val_int >= 0 else None
    if isinstance(val, str):
        val = val.strip()
        if val.isdigit():
            return int(val)
    return None

def sanitize_url(url: str) -> str:
    """Strip userinfo and query parameters from URL to prevent credential leakage."""
    try:
        parsed = urllib.parse.urlsplit(url)
        netloc = parsed.netloc.split("@")[-1] if "@" in parsed.netloc else parsed.netloc
        return urllib.parse.urlunsplit((parsed.scheme, netloc, parsed.path, "", ""))
    except Exception:
        return "<sanitized-url>"


def resolve_env_identifier(var_name: Optional[str]) -> Optional[str]:
    """Resolve an environment variable securely via os.environ or login shell evaluation."""
    if not var_name or not isinstance(var_name, str):
        return None
    var_name = var_name.strip()
    if var_name.startswith("$"):
        var_name = var_name[1:].strip()
    if not SAFE_ENV_NAME.match(var_name):
        return None

    if var_name in os.environ and os.environ[var_name]:
        return os.environ[var_name]

    # Evaluate via non-interactive login shell without echoing secrets
    try:
        res = subprocess.run(
            ["zsh", "-lc", f'printf "%s" "${{{var_name}:-}}"'],
            capture_output=True,
            text=True,
            timeout=5,
        )
        val = res.stdout.strip()
        return val if val else None
    except Exception:
        return None


def resolve_credential(raw_key: Optional[str]) -> Optional[str]:
    """Resolve API key safely from environment variable reference or literal value.

    Safety:
    - Never search ~/.zshenv or shell files with arbitrary regex or substrings.
    - If raw_key is an explicit env reference ($VAR) or matches valid env var name:
      resolve via os.environ or login shell. Fail closed (return None) if missing.
    - If raw_key contains characters outside env var names (e.g. hyphens in literal tokens),
      treat as literal credential string.
    """
    if not raw_key or not isinstance(raw_key, str):
        return None
    raw_key = raw_key.strip()
    if not raw_key:
        return None

    if raw_key.startswith("$"):
        return resolve_env_identifier(raw_key[1:])

    if SAFE_ENV_NAME.match(raw_key):
        # Environment variable name reference (e.g. HERMES_VIP_API_KEY)
        resolved = resolve_env_identifier(raw_key)
        # Fail closed: never treat an unset env variable name as a literal key
        return resolved

    # Literal API key value (e.g. contains dashes, dots, or other non-identifier characters)
    return raw_key


def extract_content_text(data: Dict[str, Any], protocol: str) -> str:
    """Extract visible text, function arguments, and reasoning from response."""
    if not isinstance(data, dict):
        return ""

    collected: List[str] = []

    if protocol == "anthropic-messages":
        content = data.get("content")
        if isinstance(content, list):
            for block in content:
                if isinstance(block, dict):
                    b_type = block.get("type")
                    if b_type == "text":
                        txt = block.get("text")
                        if isinstance(txt, str) and txt:
                            collected.append(txt)
                    elif b_type == "thinking":
                        th = block.get("thinking")
                        if isinstance(th, str) and th:
                            collected.append(th)
                    elif b_type == "tool_use":
                        inp = block.get("input")
                        if inp is not None:
                            try:
                                collected.append(json.dumps(inp))
                            except Exception:
                                pass
        elif isinstance(content, str) and content:
            collected.append(content)
    else:
        # OpenAI Responses API and Chat Completions
        output_items = data.get("output")
        if isinstance(output_items, list):
            for item in output_items:
                if isinstance(item, dict):
                    content = item.get("content")
                    if isinstance(content, list):
                        for c in content:
                            if isinstance(c, dict):
                                if c.get("type") in ("text", "output_text"):
                                    txt = c.get("text")
                                    if isinstance(txt, str) and txt:
                                        collected.append(txt)
                            elif isinstance(c, str) and c:
                                collected.append(c)
                    elif isinstance(content, str) and content:
                        collected.append(content)

                    if "reasoning" in item:
                        r = item["reasoning"]
                        if isinstance(r, dict):
                            summary = r.get("summary")
                            if isinstance(summary, str) and summary:
                                collected.append(summary)
                        elif isinstance(r, str) and r:
                            collected.append(r)

                    if item.get("type") == "function_call":
                        args = item.get("arguments")
                        if isinstance(args, str) and args:
                            collected.append(args)

        choices = data.get("choices")
        if isinstance(choices, list):
            for choice in choices:
                if isinstance(choice, dict):
                    msg = choice.get("message")
                    if isinstance(msg, dict):
                        msg_content = msg.get("content")
                        if isinstance(msg_content, str) and msg_content:
                            collected.append(msg_content)
                        elif isinstance(msg_content, list):
                            for part in msg_content:
                                if isinstance(part, dict):
                                    ptxt = part.get("text")
                                    if isinstance(ptxt, str) and ptxt:
                                        collected.append(ptxt)
                                elif isinstance(part, str) and part:
                                    collected.append(part)

                        reasoning = msg.get("reasoning_content")
                        if isinstance(reasoning, str) and reasoning:
                            collected.append(reasoning)

                        tool_calls = msg.get("tool_calls")
                        if isinstance(tool_calls, list):
                            for tool in tool_calls:
                                if isinstance(tool, dict):
                                    fn = tool.get("function")
                                    if isinstance(fn, dict):
                                        fn_args = fn.get("arguments")
                                        if isinstance(fn_args, str) and fn_args:
                                            collected.append(fn_args)

        root_content = data.get("content")
        if isinstance(root_content, str) and root_content:
            collected.append(root_content)

    return "\n".join(collected)

def make_request(
    base_url: str,
    api_key: Optional[str],
    protocol: str,
    model_id: str,
    system_prompt: Optional[str],
    user_prompt: str,
    max_tokens: int = 256,
    timeout: float = 30.0,
) -> Tuple[Optional[int], Optional[str], Optional[str], Optional[str]]:
    """Execute API request and return (input_tokens, actual_model, output_text, sanitized_error)."""
    bounded_timeout = max(1.0, min(float(timeout), 60.0))
    headers = {"Content-Type": "application/json"}
    if api_key:
        if protocol == "anthropic-messages":
            headers["x-api-key"] = api_key
            headers["anthropic-version"] = "2023-06-01"
        else:
            headers["Authorization"] = f"Bearer {api_key}"

    base = base_url.rstrip("/")
    if protocol == "anthropic-messages":
        url = f"{base}/v1/messages" if not base.endswith("/v1") else f"{base}/messages"
        payload: Dict[str, Any] = {
            "model": model_id,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": user_prompt}],
        }
        if system_prompt:
            payload["system"] = system_prompt
    else:
        # OpenAI Responses API - route without legacy ?beta=true
        if base.endswith("/v1"):
            url = f"{base}/responses"
        else:
            url = f"{base}/v1/responses"

        payload: Dict[str, Any] = {
            "model": model_id,
            "input": [{"role": "user", "content": user_prompt}],
            "max_output_tokens": max_tokens,
            "stream": False,
        }
        # Single authoritative instruct field for Responses API
        if system_prompt:
            payload["instructions"] = system_prompt

    data_bytes = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data_bytes, headers=headers, method="POST")
    opener = urllib.request.build_opener(SafeRedirectHandler)

    try:
        with opener.open(req, timeout=bounded_timeout) as resp:
            resp_bytes = resp.read(MAX_RESPONSE_BYTES + 1)
            if len(resp_bytes) > MAX_RESPONSE_BYTES:
                return None, None, None, "ResponseExceededLimit"
            try:
                decoded = resp_bytes.decode("utf-8")
            except UnicodeDecodeError:
                return None, None, None, "MalformedEncoding"
            try:
                data = json.loads(decoded)
            except json.JSONDecodeError:
                return None, None, None, "JSONDecodeError"

            if not isinstance(data, dict):
                return None, None, None, "MalformedJSON"

            # Report actual served model strictly if returned by provider; never fabricate
            model_val = data.get("model")
            actual_model = (
                str(model_val).strip()
                if (isinstance(model_val, str) and model_val.strip())
                else "UNKNOWN"
            )
            output_text = extract_content_text(data, protocol)

            usage = data.get("usage")
            if protocol == "anthropic-messages":
                # Anthropic Messages API: prompt caching separates cached from uncached input tokens.
                # Total prompt input tokens = input_tokens + cache_creation_input_tokens + cache_read_input_tokens.
                # Reject any explicitly present invalid usage counter (fail closed).
                if isinstance(usage, dict):
                    base_in = None
                    if "input_tokens" in usage:
                        base_in = parse_token_count(usage["input_tokens"])
                        if base_in is None:
                            return None, actual_model, output_text, None

                    cache_create = None
                    if "cache_creation_input_tokens" in usage:
                        cache_create = parse_token_count(usage["cache_creation_input_tokens"])
                        if cache_create is None:
                            return None, actual_model, output_text, None

                    cache_read = None
                    if "cache_read_input_tokens" in usage:
                        cache_read = parse_token_count(usage["cache_read_input_tokens"])
                        if cache_read is None:
                            return None, actual_model, output_text, None

                    if base_in is not None or cache_create is not None or cache_read is not None:
                        input_tokens = (base_in or 0) + (cache_create or 0) + (cache_read or 0)
                    else:
                        input_tokens = parse_token_count(data.get("input_tokens"))
                else:
                    input_tokens = parse_token_count(data.get("input_tokens"))
            else:
                # OpenAI Responses API: input_tokens already includes cached tokens
                # Reject any explicitly present invalid usage counter (fail closed).
                if isinstance(usage, dict):
                    if "input_tokens" in usage:
                        input_tokens = parse_token_count(usage["input_tokens"])
                    elif "prompt_tokens" in usage:
                        input_tokens = parse_token_count(usage["prompt_tokens"])
                    elif "input" in usage:
                        input_tokens = parse_token_count(usage["input"])
                    else:
                        input_tokens = parse_token_count(data.get("input_tokens"))
                else:
                    input_tokens = parse_token_count(data.get("input_tokens"))

            return input_tokens, actual_model, output_text, None
    except urllib.error.HTTPError as e:
        # Sanitize error to prevent leaking URL query parameters or secret tokens
        return None, None, None, f"HTTP {e.code}"
    except urllib.error.URLError as e:
        if isinstance(getattr(e, "reason", None), (TimeoutError, socket.timeout)) or "timed out" in str(getattr(e, "reason", "")):
            return None, None, None, "TimeoutError"
        reason_name = type(e.reason).__name__ if hasattr(e, "reason") and e.reason else "URLError"
        return None, None, None, f"URLError({reason_name})"
    except TimeoutError:
        return None, None, None, "TimeoutError"
    except Exception as e:
        return None, None, None, f"{type(e).__name__}"


def probe_registration(
    provider_name: str,
    model_id: str,
    base_url: str,
    api_key: Optional[str],
    protocol: str,
    challenge_length: int = 5000,
    timeout: float = 30.0,
) -> Dict[str, Any]:
    """Execute paired control and challenge probes for a single registration."""
    nonce = secrets.token_hex(8)
    secret_marker = f"NONCE_{nonce}"
    # Paired identical user question for both control and challenge
    identical_user_prompt = "What is the secret verification token? Echo it verbatim."

    # 1. Baseline / Control Request (without the secret marker or large padding)
    control_system_prompt = "CONTROL INSTRUCTION: No secret verification token has been assigned to this turn."
    base_in, base_model, base_out, base_err = make_request(
        base_url=base_url,
        api_key=api_key,
        protocol=protocol,
        model_id=model_id,
        system_prompt=control_system_prompt,
        user_prompt=identical_user_prompt,
        timeout=timeout,
    )

    if base_err:
        return {
            "provider": provider_name,
            "model": model_id,
            "protocol": protocol,
            "verdict": "FAIL",
            "error": f"Control request failed: {base_err}",
            "actual_model": "UNKNOWN",
            "control_model": "UNKNOWN",
            "challenge_model": "UNKNOWN",
            "baseline_input_tokens": None,
            "challenge_input_tokens": None,
            "delta_input_tokens": 0,
            "echoed_challenge": False,
        }
    # Verify baseline control negative: control does not output the unprovided nonce
    if secret_marker in (base_out or "") or nonce in (base_out or ""):
        return {
            "provider": provider_name,
            "model": model_id,
            "protocol": protocol,
            "verdict": "FAIL",
            "error": "Control run hallucinated challenge nonce",
            "actual_model": "UNKNOWN",
            "control_model": base_model or "UNKNOWN",
            "challenge_model": "UNKNOWN",
            "baseline_input_tokens": base_in,
            "challenge_input_tokens": None,
            "delta_input_tokens": 0,
            "echoed_challenge": False,
        }
    # 2. Challenge Request (carrying the secret marker ONLY in the system prompt)
    challenge_padding = ("Harness prompt delivery verification boundary. " * max(1, (challenge_length // 45)))[:challenge_length]
    challenge_prompt = (
        f"{challenge_padding}\n\n"
        f"CRITICAL VERIFICATION INSTRUCTION:\n"
        f"The secret verification token is '{secret_marker}'.\n"
        f"You must include '{secret_marker}' in your answer."
    )

    chal_in, chal_model, chal_out, chal_err = make_request(
        base_url=base_url,
        api_key=api_key,
        protocol=protocol,
        model_id=model_id,
        system_prompt=challenge_prompt,
        user_prompt=identical_user_prompt,
        timeout=timeout,
    )

    if chal_err:
        return {
            "provider": provider_name,
            "model": model_id,
            "protocol": protocol,
            "verdict": "FAIL",
            "error": f"Challenge request failed: {chal_err}",
            "actual_model": "UNKNOWN",
            "control_model": base_model or "UNKNOWN",
            "challenge_model": "UNKNOWN",
            "baseline_input_tokens": base_in,
            "challenge_input_tokens": None,
            "delta_input_tokens": 0,
            "echoed_challenge": False,
        }
    delta = (chal_in - base_in) if (chal_in is not None and base_in is not None) else 0
    echoed = (secret_marker in (chal_out or "")) or (nonce in (chal_out or ""))

    # Deliverability condition: Model must receive and honor system prompt
    # Token difference expected (appended prompt increases input tokens) and nonce echoed
    min_expected_delta = 200 if challenge_length >= 500 else 0
    has_valid_baseline = base_in is not None and base_in >= 0
    has_valid_challenge = chal_in is not None and chal_in > 0
    tokens_expanded = (
        has_valid_baseline
        and has_valid_challenge
        and (chal_in > base_in)
        and (delta >= min_expected_delta)
    )
    delivers = echoed and tokens_expanded
    verdict = "PASS" if delivers else "FAIL"

    # Strict challenge attribution: never fall back to control model when challenge omits model metadata
    actual_model = chal_model if chal_model and chal_model != "UNKNOWN" else "UNKNOWN"

    error_msg = None
    if verdict == "FAIL":
        if not echoed:
            error_msg = "Challenge nonce not echoed in response"
        elif not has_valid_baseline:
            error_msg = "Missing or invalid baseline token usage"
        elif not has_valid_challenge:
            error_msg = "Missing or invalid challenge token usage"
        elif chal_in <= base_in:
            error_msg = "Challenge did not increase input tokens"
        elif delta < min_expected_delta:
            error_msg = f"Insufficient token delta ({delta} < {min_expected_delta})"

    return {
        "provider": provider_name,
        "model": model_id,
        "protocol": protocol,
        "verdict": verdict,
        "actual_model": actual_model,
        "control_model": base_model or "UNKNOWN",
        "challenge_model": chal_model or "UNKNOWN",
        "baseline_input_tokens": base_in,
        "challenge_input_tokens": chal_in,
        "delta_input_tokens": delta,
        "echoed_challenge": echoed,
        "error": error_msg,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Probe harness prompt delivery for Prime Agent registrations")
    parser.add_argument("--models-json", default=os.path.expanduser("~/.prime/agent/models.json"), help="Path to models.json")
    parser.add_argument("--provider", help="Provider name to probe")
    parser.add_argument("--model", help="Model ID to probe")
    parser.add_argument("--all", action="store_true", help="Probe all registered models")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument("--timeout", type=float, default=25.0, help="Request timeout in seconds")
    parser.add_argument("--challenge-length", type=int, default=5000, help="Appended prompt challenge character length")
    args = parser.parse_args()

    models_path = os.path.abspath(args.models_json)
    if not os.path.isfile(models_path):
        print(f"Error: models config file not found: {models_path}", file=sys.stderr)
        return 1

    with open(models_path, "r", encoding="utf-8") as f:
        models_data = json.load(f)

    providers = models_data.get("providers", {})
    targets: List[Tuple[str, str, Dict[str, Any]]] = []

    if args.all:
        for p_name, p_cfg in providers.items():
            for m in p_cfg.get("models", []):
                targets.append((p_name, m.get("id"), p_cfg))
    elif args.provider:
        if args.provider not in providers:
            print(f"Error: provider '{args.provider}' not in {models_path}", file=sys.stderr)
            return 1
        p_cfg = providers[args.provider]
        available_models = [m.get("id") for m in p_cfg.get("models", [])]
        if args.model:
            if args.model not in available_models:
                print(f"Error: model '{args.model}' not under provider '{args.provider}'", file=sys.stderr)
                return 1
            targets.append((args.provider, args.model, p_cfg))
        else:
            for m in p_cfg.get("models", []):
                targets.append((args.provider, m.get("id"), p_cfg))
    else:
        print("Error: Specify --provider and optionally --model, or pass --all", file=sys.stderr)
        return 1

    results = []
    for p_name, m_id, p_cfg in targets:
        base_url = p_cfg.get("baseUrl")
        raw_key = p_cfg.get("apiKey")
        api_key = resolve_credential(raw_key)
        protocol = p_cfg.get("api", "openai-responses")

        if raw_key and not api_key:
            results.append({
                "provider": p_name,
                "model": m_id,
                "protocol": protocol,
                "verdict": "FAIL",
                "error": "Credential could not be resolved from environment (failed closed)",
                "actual_model": "UNKNOWN",
                "control_model": "UNKNOWN",
                "challenge_model": "UNKNOWN",
                "baseline_input_tokens": None,
                "challenge_input_tokens": None,
                "delta_input_tokens": 0,
                "echoed_challenge": False,
            })
            continue

        res = probe_registration(
            provider_name=p_name,
            model_id=m_id,
            base_url=base_url,
            api_key=api_key,
            protocol=protocol,
            challenge_length=args.challenge_length,
            timeout=args.timeout,
        )
        results.append(res)
    if not results:
        print("Error: No models found to probe", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(f"{'PROVIDER':<20} {'MODEL':<24} {'VERDICT':<8} {'CONTROL':<8} {'CHAL':<8} {'DELTA':<8} {'ECHO':<6} {'ACTUAL MODEL'}")
        print("-" * 105)
        for r in results:
            verdict = r["verdict"]
            base = str(r.get("baseline_input_tokens")) if r.get("baseline_input_tokens") is not None else "-"
            chal = str(r.get("challenge_input_tokens")) if r.get("challenge_input_tokens") is not None else "-"
            delta = str(r.get("delta_input_tokens")) if r.get("delta_input_tokens") is not None else "-"
            echo = "yes" if r.get("echoed_challenge") else "no"
            actual = r.get("actual_model") or "-"
            if r.get("error"):
                actual += f" ({r['error']})"
            print(f"{r['provider']:<20} {r['model']:<24} {verdict:<8} {base:<8} {chal:<8} {delta:<8} {echo:<6} {actual}")

    all_passed = all(r["verdict"] == "PASS" for r in results)
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

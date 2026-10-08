"""Tests for probe-prime-agent-delivery.py."""

from __future__ import annotations

import importlib.util
import json
import math
import sys
import urllib.request
from pathlib import Path
from unittest.mock import MagicMock, patch
try:
    import pytest
except ImportError:
    pytest = None  # type: ignore

SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "probe-prime-agent-delivery.py"
spec = importlib.util.spec_from_file_location("probe_script", SCRIPT_PATH)
assert spec is not None and spec.loader is not None
probe = importlib.util.module_from_spec(spec)
sys.modules["probe_script"] = probe
spec.loader.exec_module(probe)


def test_resolve_credential_literal_and_env() -> None:
    assert probe.resolve_credential(None) is None
    assert probe.resolve_credential("") is None
    # Literal token with hyphens
    assert probe.resolve_credential("sk-ant-api03-sample-token") == "sk-ant-api03-sample-token"
    # Unset env var fails closed
    assert probe.resolve_credential("$NON_EXISTENT_VAR_XYZ") is None
    assert probe.resolve_credential("NON_EXISTENT_VAR_XYZ") is None


def test_sanitize_url() -> None:
    raw = "https://user:secret@api.example.com/v1/responses?key=tok#frag"
    assert probe.sanitize_url(raw) == "https://api.example.com/v1/responses"


def test_safe_redirect_handler() -> None:
    req = urllib.request.Request("https://example.com/v1/responses", headers={"Authorization": "Bearer secret", "x-api-key": "tok"})
    handler = probe.SafeRedirectHandler()

    # Cross origin redirect forbidden
    assert handler.redirect_request(req, None, 301, "Moved", {}, "https://evil.com/leak") is None
    # HTTPS to HTTP downgrade forbidden
    assert handler.redirect_request(req, None, 301, "Moved", {}, "http://example.com/v1/responses") is None

    # Same origin redirect strips sensitive auth headers
    new_req = handler.redirect_request(req, None, 301, "Moved", {}, "https://example.com/v2/responses")
    assert new_req is not None
    assert "Authorization" not in new_req.headers
    assert "x-api-key" not in new_req.headers


def test_probe_registration_delivering_pass() -> None:
    def fake_open(req: urllib.request.Request, timeout: float = 30.0) -> MagicMock:
        body = json.loads(req.data.decode("utf-8"))
        instructions = body.get("instructions", "")
        if "NONCE_" in instructions:
            resp_data = {
                "model": "delivering-model-v1",
                "usage": {"input_tokens": 1250},
                "output": [{"content": [{"type": "output_text", "text": "Verification token is NONCE_11223344"}]}],
            }
        else:
            resp_data = {
                "model": "delivering-model-v1",
                "usage": {"input_tokens": 45},
                "output": [{"content": [{"type": "output_text", "text": "No token."}]}],
            }
        resp = MagicMock()
        resp.read.return_value = json.dumps(resp_data).encode("utf-8")
        resp.__enter__.return_value = resp
        resp.__exit__.return_value = None
        return resp

    with patch("secrets.token_hex", return_value="11223344"):
        with patch("urllib.request.OpenerDirector.open", side_effect=fake_open):
            res = probe.probe_registration(
                provider_name="cockpit",
                model_id="gpt-5.6-sol",
                base_url="http://127.0.0.1:51006/v1",
                api_key="sk-test",
                protocol="openai-responses",
                challenge_length=5000,
            )
            assert res["verdict"] == "PASS"
            assert res["delta_input_tokens"] == 1205
            assert res["echoed_challenge"] is True
            assert res["actual_model"] == "delivering-model-v1"


def test_probe_registration_non_delivering_fail() -> None:
    def fake_open_nondelivering(req: urllib.request.Request, timeout: float = 30.0) -> MagicMock:
        resp_data = {
            "model": "fable-product",
            "usage": {"input_tokens": 14},
            "output": [{"content": [{"type": "output_text", "text": "Static answer"}]}],
        }
        resp = MagicMock()
        resp.read.return_value = json.dumps(resp_data).encode("utf-8")
        resp.__enter__.return_value = resp
        resp.__exit__.return_value = None
        return resp

    with patch("urllib.request.OpenerDirector.open", side_effect=fake_open_nondelivering):
        res = probe.probe_registration(
            provider_name="shopapikey",
            model_id="Claude-Fable",
            base_url="https://api.phanmemvip.shop/v1",
            api_key="sk-test",
            protocol="openai-responses",
            challenge_length=5000,
        )
        assert res["verdict"] == "FAIL"
        assert res["delta_input_tokens"] == 0
        assert res["echoed_challenge"] is False


def test_probe_registration_negative_control_hallucination() -> None:
    def fake_open_hallucinate(req: urllib.request.Request, timeout: float = 30.0) -> MagicMock:
        resp_data = {
            "model": "hallucinating-model",
            "usage": {"input_tokens": 50},
            "output": [{"content": [{"type": "output_text", "text": "Token is NONCE_deadbeef"}]}],
        }
        resp = MagicMock()
        resp.read.return_value = json.dumps(resp_data).encode("utf-8")
        resp.__enter__.return_value = resp
        resp.__exit__.return_value = None
        return resp

    with patch("secrets.token_hex", return_value="deadbeef"):
        with patch("urllib.request.OpenerDirector.open", side_effect=fake_open_hallucinate):
            res = probe.probe_registration(
                provider_name="test-prov",
                model_id="test-model",
                base_url="http://127.0.0.1:1234/v1",
                api_key="sk-test",
                protocol="openai-responses",
                challenge_length=5000,
            )
            assert res["verdict"] == "FAIL"
            assert "Control run hallucinated challenge nonce" in res["error"]


def test_probe_registration_unknown_model_attribution() -> None:
    def fake_open_no_model(req: urllib.request.Request, timeout: float = 30.0) -> MagicMock:
        resp_data = {
            "usage": {"input_tokens": 1000},
            "output": [{"content": [{"type": "output_text", "text": "Token is NONCE_aabbccdd"}]}],
        }
        resp = MagicMock()
        resp.read.return_value = json.dumps(resp_data).encode("utf-8")
        resp.__enter__.return_value = resp
        resp.__exit__.return_value = None
        return resp

    with patch("secrets.token_hex", return_value="aabbccdd"):
        with patch("urllib.request.OpenerDirector.open", side_effect=fake_open_no_model):
            res = probe.probe_registration(
                provider_name="test-prov",
                model_id="requested-id-not-guessed",
                base_url="http://127.0.0.1:1234/v1",
                api_key="sk-test",
                protocol="openai-responses",
                challenge_length=5000,
            )
            assert res["actual_model"] == "UNKNOWN"

def test_probe_registration_control_model_not_reused_when_challenge_missing_model() -> None:
    def fake_open_diff_metadata(req: urllib.request.Request, timeout: float = 30.0) -> MagicMock:
        body = json.loads(req.data.decode("utf-8"))
        instructions = body.get("instructions", "")
        if "NONCE_" in instructions:
            import re
            m = re.search(r"NONCE_[a-f0-9]+", instructions)
            nonce = m.group(0) if m else "NONE"
            # Gateway challenge response omits model metadata
            resp_data = {
                "usage": {"input_tokens": 1250},
                "output": [{"content": [{"type": "output_text", "text": f"Token: {nonce}"}]}],
            }
        else:
            # Control response explicitly reports gateway-control-model
            resp_data = {
                "model": "gateway-control-model",
                "usage": {"input_tokens": 40},
                "output": [{"content": [{"type": "output_text", "text": "No token."}]}],
            }
        resp = MagicMock()
        resp.read.return_value = json.dumps(resp_data).encode("utf-8")
        resp.__enter__.return_value = resp
        resp.__exit__.return_value = None
        return resp

    with patch("urllib.request.OpenerDirector.open", side_effect=fake_open_diff_metadata):
        res = probe.probe_registration(
            provider_name="test-prov",
            model_id="test-model",
            base_url="http://127.0.0.1:1234/v1",
            api_key="sk-test",
            protocol="openai-responses",
            challenge_length=5000,
        )
        assert res["verdict"] == "PASS"
        assert res["delta_input_tokens"] == 1210
        assert res["echoed_challenge"] is True
        # Strict attribution: challenge model was omitted, MUST NOT attribute to control model!
        assert res["actual_model"] == "UNKNOWN"
        assert res["control_model"] == "gateway-control-model"
        assert res["challenge_model"] == "UNKNOWN"


def test_anthropic_messages_cache_tokens_summed() -> None:
    def fake_open_anthropic(req: urllib.request.Request, timeout: float = 30.0) -> MagicMock:
        body = json.loads(req.data.decode("utf-8"))
        system = body.get("system", "")
        if "NONCE_" in system:
            import re
            m = re.search(r"NONCE_[a-f0-9]+", system)
            nonce = m.group(0) if m else "NONE"
            # Anthropic prompt caching: uncached input_tokens is small, cache_read_input_tokens is large
            resp_data = {
                "model": "claude-3-7-sonnet-20250219",
                "usage": {
                    "input_tokens": 15,
                    "cache_creation_input_tokens": 0,
                    "cache_read_input_tokens": 1200,
                },
                "content": [{"type": "text", "text": f"Here is the token: {nonce}"}],
            }
        else:
            resp_data = {
                "model": "claude-3-7-sonnet-20250219",
                "usage": {
                    "input_tokens": 25,
                    "cache_creation_input_tokens": 0,
                    "cache_read_input_tokens": 0,
                },
                "content": [{"type": "text", "text": "No token."}],
            }
        resp = MagicMock()
        resp.read.return_value = json.dumps(resp_data).encode("utf-8")
        resp.__enter__.return_value = resp
        resp.__exit__.return_value = None
        return resp

    with patch("urllib.request.OpenerDirector.open", side_effect=fake_open_anthropic):
        res = probe.probe_registration(
            provider_name="anthropic-prov",
            model_id="claude-3-7-sonnet",
            base_url="https://api.anthropic.com/v1",
            api_key="sk-ant-test",
            protocol="anthropic-messages",
            challenge_length=5000,
        )
        assert res["verdict"] == "PASS"
        # Total chal input tokens = 15 + 1200 = 1215; base = 25; delta = 1190
        assert res["challenge_input_tokens"] == 1215
        assert res["baseline_input_tokens"] == 25
        assert res["delta_input_tokens"] == 1190
        assert res["echoed_challenge"] is True
        assert res["actual_model"] == "claude-3-7-sonnet-20250219"


def test_safe_redirect_handler_case_insensitive_header_purge() -> None:
    handler = probe.SafeRedirectHandler()
    req = urllib.request.Request(
        "https://example.com/v1/responses",
        data=b"{}",
        headers={
            "Authorization": "Bearer secret",
            "x-api-key": "secret-key",
            "Proxy-Authorization": "Basic secret-proxy",
            "Cookie": "session=123",
            "Content-Type": "application/json",
        },
    )
    new_req = handler.redirect_request(req, None, 302, "Found", {}, "https://example.com/v1/responses-redirected")
    assert new_req is not None
    for header in ("Authorization", "x-api-key", "X-api-key", "Proxy-Authorization", "Cookie"):
        assert header.lower() not in [k.lower() for k in new_req.headers.keys()]
    # Forbid HTTPS to HTTP downgrade
    assert handler.redirect_request(req, None, 302, "Found", {}, "http://example.com/v1/downgrade") is None

    # Forbid cross-origin redirects
    assert handler.redirect_request(req, None, 302, "Found", {}, "https://other.com/v1/responses") is None

    # Forbid non-http(s) schemes
    assert handler.redirect_request(req, None, 302, "Found", {}, "ftp://example.com/v1/responses") is None


def test_parse_token_count_boundaries() -> None:
    assert probe.parse_token_count(None) is None
    assert probe.parse_token_count(True) is None
    assert probe.parse_token_count(False) is None
    assert probe.parse_token_count(-10) is None
    assert probe.parse_token_count(-1.0) is None
    assert probe.parse_token_count(float("nan")) is None
    assert probe.parse_token_count(float("inf")) is None
    assert probe.parse_token_count(float("-inf")) is None
    assert probe.parse_token_count(1.5) is None
    assert probe.parse_token_count(250.75) is None
    assert probe.parse_token_count("invalid") is None
    assert probe.parse_token_count("123") == 123
    assert probe.parse_token_count(0) == 0
    assert probe.parse_token_count(450) == 450
    assert probe.parse_token_count(450.0) == 450


def test_make_request_token_usage_boundaries() -> None:
    for test_case, payload, proto, expected_tokens in [
        ("negative", {"model": "m", "usage": {"input_tokens": -50}}, "openai-responses", None),
        ("nan", {"model": "m", "usage": {"input_tokens": float("nan")}}, "openai-responses", None),
        ("boolean", {"model": "m", "usage": {"input_tokens": True}}, "openai-responses", None),
        ("fractional", {"model": "m", "usage": {"input_tokens": 250.75}}, "openai-responses", None),
        ("zero", {"model": "m", "usage": {"input_tokens": 0}}, "openai-responses", 0),
        ("anthropic_negative_cache", {"model": "m", "usage": {"input_tokens": 100, "cache_read_input_tokens": -50}}, "anthropic-messages", None),
        ("anthropic_fractional_cache", {"model": "m", "usage": {"input_tokens": 100, "cache_read_input_tokens": 12.5}}, "anthropic-messages", None),
        ("anthropic_corrupt_cache", {"model": "m", "usage": {"input_tokens": 100, "cache_read_input_tokens": "corrupt"}}, "anthropic-messages", None),
        ("anthropic_zero_cache", {"model": "m", "usage": {"input_tokens": 50, "cache_read_input_tokens": 0}}, "anthropic-messages", 50),
        ("anthropic_non_dict_usage", {"model": "m", "usage": None}, "anthropic-messages", None),
        ("openai_corrupt_input_with_prompt_fallback", {"model": "m", "usage": {"input_tokens": "corrupt", "prompt_tokens": 500}}, "openai-responses", None),
    ]:
        resp = MagicMock()
        resp.read.return_value = json.dumps(payload).encode("utf-8")
        resp.__enter__.return_value = resp
        resp.__exit__.return_value = None
        with patch("urllib.request.OpenerDirector.open", return_value=resp):
            tokens, model, out, err = probe.make_request(
                base_url="http://127.0.0.1:1234/v1",
                api_key="sk-test",
                protocol=proto,
                model_id="m",
                system_prompt="s",
                user_prompt="u",
            )
            assert tokens == expected_tokens, f"{test_case}: expected {expected_tokens}, got {tokens}"
            assert err is None

def test_make_request_oversize_response_bound() -> None:
    oversize_bytes = b'{"model": "m"}' + (b" " * (10 * 1024 * 1024 + 10))
    resp = MagicMock()
    resp.read.return_value = oversize_bytes
    resp.__enter__.return_value = resp
    resp.__exit__.return_value = None
    with patch("urllib.request.OpenerDirector.open", return_value=resp):
        tokens, model, out, err = probe.make_request(
            base_url="http://127.0.0.1:1234/v1",
            api_key="sk-test",
            protocol="openai-responses",
            model_id="m",
            system_prompt="s",
            user_prompt="u",
        )
        assert err == "ResponseExceededLimit"


def test_make_request_malformed_json_and_encoding() -> None:
    resp = MagicMock()
    resp.read.return_value = b"{not-valid-json"
    resp.__enter__.return_value = resp
    resp.__exit__.return_value = None
    with patch("urllib.request.OpenerDirector.open", return_value=resp):
        _, _, _, err = probe.make_request(
            base_url="http://127.0.0.1:1234/v1",
            api_key="sk-test",
            protocol="openai-responses",
            model_id="m",
            system_prompt="s",
            user_prompt="u",
        )
        assert err == "JSONDecodeError"

    resp_non_dict = MagicMock()
    resp_non_dict.read.return_value = b"[\"array-not-dict\"]"
    resp_non_dict.__enter__.return_value = resp_non_dict
    resp_non_dict.__exit__.return_value = None
    with patch("urllib.request.OpenerDirector.open", return_value=resp_non_dict):
        _, _, _, err_nd = probe.make_request(
            base_url="http://127.0.0.1:1234/v1",
            api_key="sk-test",
            protocol="openai-responses",
            model_id="m",
            system_prompt="s",
            user_prompt="u",
        )
        assert err_nd == "MalformedJSON"


def test_extract_content_text_adversarial_shapes() -> None:
    # 1. Anthropic block with None text
    assert probe.extract_content_text({"content": [{"type": "text", "text": None}]}, "anthropic-messages") == ""
    # 2. Anthropic direct string
    assert probe.extract_content_text({"content": "direct-string"}, "anthropic-messages") == "direct-string"
    # 3. OpenAI list of content parts in message
    assert probe.extract_content_text({"choices": [{"message": {"content": [{"type": "text", "text": "token-123"}]}}]}, "openai-responses") == "token-123"
    # 4. OpenAI output item with function_call and reasoning summary
    out_data = {
        "output": [
            {"reasoning": {"summary": "reasoning summary text"}},
            {"type": "function_call", "arguments": "{\"query\": \"nonce\"}"},
        ]
    }
    assert "reasoning summary text" in probe.extract_content_text(out_data, "openai-responses")
    assert "{\"query\": \"nonce\"}" in probe.extract_content_text(out_data, "openai-responses")
    # 5. Non-dict input
    assert probe.extract_content_text(["invalid"], "openai-responses") == ""


def test_probe_registration_missing_baseline_tokens_fails() -> None:
    def fake_open(req: urllib.request.Request, timeout: float = 30.0) -> MagicMock:
        body = json.loads(req.data.decode("utf-8"))
        instructions = body.get("instructions", "")
        if "NONCE_" in instructions:
            import re
            m = re.search(r"NONCE_[a-f0-9]+", instructions)
            nonce = m.group(0) if m else "NONE"
            resp_data = {
                "model": "test-model",
                "usage": {"input_tokens": 1500},
                "output": [{"content": [{"type": "output_text", "text": f"Token: {nonce}"}]}],
            }
        else:
            # Baseline response has NO usage dict (missing baseline tokens)
            resp_data = {
                "model": "test-model",
                "output": [{"content": [{"type": "output_text", "text": "No token."}]}],
            }
        resp = MagicMock()
        resp.read.return_value = json.dumps(resp_data).encode("utf-8")
        resp.__enter__.return_value = resp
        resp.__exit__.return_value = None
        return resp

    with patch("urllib.request.OpenerDirector.open", side_effect=fake_open):
        res = probe.probe_registration(
            provider_name="test-prov",
            model_id="test-model",
            base_url="http://127.0.0.1:1234/v1",
            api_key="sk-test",
            protocol="openai-responses",
            challenge_length=5000,
        )
        assert res["verdict"] == "FAIL"
        assert res["baseline_input_tokens"] is None
        assert "Missing or invalid baseline token usage" in res["error"]


def test_probe_registration_zero_vs_missing_baseline_http() -> None:
    import http.server
    import threading

    class ZeroVsMissingHandler(http.server.BaseHTTPRequestHandler):
        mode = "zero"

        def do_POST(self) -> None:
            length = int(self.headers.get("Content-Length", 0))
            body_bytes = self.rfile.read(length) if length else b"{}"
            body = json.loads(body_bytes.decode("utf-8"))
            instructions = body.get("instructions", "")
            if "NONCE_" in instructions:
                import re
                m = re.search(r"NONCE_[a-f0-9]+", instructions)
                nonce = m.group(0) if m else "NONE"
                chal_tokens = 0 if self.mode == "zero_challenge" else 250
                resp_data = {
                    "model": "test-model",
                    "usage": {"input_tokens": chal_tokens},
                    "output": [{"content": [{"type": "output_text", "text": f"Token: {nonce}"}]}],
                }
            else:
                if self.mode in ("zero", "zero_challenge"):
                    resp_data = {
                        "model": "test-model",
                        "usage": {"input_tokens": 0},
                        "output": [{"content": [{"type": "output_text", "text": "No token."}]}],
                    }
                else:
                    resp_data = {
                        "model": "test-model",
                        "output": [{"content": [{"type": "output_text", "text": "No token."}]}],
                    }
            resp_bytes = json.dumps(resp_data).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(resp_bytes)))
            self.end_headers()
            self.wfile.write(resp_bytes)

        def log_message(self, format: str, *args: Any) -> None:
            pass

    server = http.server.HTTPServer(("127.0.0.1", 0), ZeroVsMissingHandler)
    port = server.server_port
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()

    try:
        # Case A: Explicit measured zero baseline with challenge expansion to 250 -> PASS
        ZeroVsMissingHandler.mode = "zero"
        res_zero = probe.probe_registration(
            provider_name="test-prov",
            model_id="test-model",
            base_url=f"http://127.0.0.1:{port}",
            api_key="sk-test",
            protocol="openai-responses",
            challenge_length=5000,
            timeout=2.0,
        )
        assert res_zero["verdict"] == "PASS"
        assert res_zero["baseline_input_tokens"] == 0
        assert res_zero["challenge_input_tokens"] == 250
        assert res_zero["delta_input_tokens"] == 250
        assert res_zero["echoed_challenge"] is True
        assert res_zero["error"] is None

        # Case B: Explicit zero baseline AND zero challenge (nonce echoed, no expansion) -> FAIL
        ZeroVsMissingHandler.mode = "zero_challenge"
        res_zero_chal = probe.probe_registration(
            provider_name="test-prov",
            model_id="test-model",
            base_url=f"http://127.0.0.1:{port}",
            api_key="sk-test",
            protocol="openai-responses",
            challenge_length=5000,
            timeout=2.0,
        )
        assert res_zero_chal["verdict"] == "FAIL"
        assert res_zero_chal["baseline_input_tokens"] == 0
        assert res_zero_chal["challenge_input_tokens"] == 0
        assert res_zero_chal["delta_input_tokens"] == 0
        assert res_zero_chal["echoed_challenge"] is True

        # Case C: Missing baseline usage -> FAIL
        ZeroVsMissingHandler.mode = "missing"
        res_missing = probe.probe_registration(
            provider_name="test-prov",
            model_id="test-model",
            base_url=f"http://127.0.0.1:{port}",
            api_key="sk-test",
            protocol="openai-responses",
            challenge_length=5000,
            timeout=2.0,
        )
        assert res_missing["verdict"] == "FAIL"
        assert res_missing["baseline_input_tokens"] is None
        assert res_missing["challenge_input_tokens"] == 250
        assert res_missing["delta_input_tokens"] == 0
    finally:
        server.shutdown()
        server.server_close()


def test_probe_registration_corrupt_cache_counter_fails_closed() -> None:
    def fake_open(req: urllib.request.Request, timeout: float = 30.0) -> MagicMock:
        body = json.loads(req.data.decode("utf-8"))
        system = body.get("system", "")
        if "NONCE_" in system:
            import re
            m = re.search(r"NONCE_[a-f0-9]+", system)
            nonce = m.group(0) if m else "NONE"
            # Challenge has explicitly present corrupt cache_read_input_tokens
            resp_data = {
                "model": "claude-3-7-sonnet",
                "usage": {
                    "input_tokens": 1000,
                    "cache_read_input_tokens": "INVALID_CORRUPT",
                },
                "content": [{"type": "text", "text": f"Token: {nonce}"}],
            }
        else:
            resp_data = {
                "model": "claude-3-7-sonnet",
                "usage": {"input_tokens": 25},
                "content": [{"type": "text", "text": "No token."}],
            }
        resp = MagicMock()
        resp.read.return_value = json.dumps(resp_data).encode("utf-8")
        resp.__enter__.return_value = resp
        resp.__exit__.return_value = None
        return resp

    with patch("urllib.request.OpenerDirector.open", side_effect=fake_open):
        res = probe.probe_registration(
            provider_name="anthropic-prov",
            model_id="claude-3-7-sonnet",
            base_url="https://api.anthropic.com/v1",
            api_key="sk-ant-test",
            protocol="anthropic-messages",
            challenge_length=5000,
        )
        assert res["verdict"] == "FAIL"
        assert res["challenge_input_tokens"] is None
        assert "Missing or invalid challenge token usage" in res["error"]


def test_main_empty_targets_exit_contract(tmp_path: Any = None) -> None:
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tf:
        json.dump({"providers": {"empty-prov": {"baseUrl": "http://127.0.0.1", "models": []}}}, tf)
        tf_path = tf.name

    try:
        with patch("sys.argv", ["probe.py", "--models-json", tf_path, "--all"]):
            exit_code = probe.main()
            assert exit_code == 1
    finally:
        import os
        if os.path.exists(tf_path):
            os.remove(tf_path)


if __name__ == "__main__":
    test_resolve_credential_literal_and_env()
    test_sanitize_url()
    test_safe_redirect_handler()
    test_probe_registration_delivering_pass()
    test_probe_registration_non_delivering_fail()
    test_probe_registration_negative_control_hallucination()
    test_probe_registration_unknown_model_attribution()
    test_probe_registration_control_model_not_reused_when_challenge_missing_model()
    test_anthropic_messages_cache_tokens_summed()
    test_safe_redirect_handler_case_insensitive_header_purge()
    test_parse_token_count_boundaries()
    test_make_request_token_usage_boundaries()
    test_make_request_oversize_response_bound()
    test_make_request_malformed_json_and_encoding()
    test_extract_content_text_adversarial_shapes()
    test_probe_registration_missing_baseline_tokens_fails()
    test_probe_registration_zero_vs_missing_baseline_http()
    test_probe_registration_corrupt_cache_counter_fails_closed()
    test_main_empty_targets_exit_contract()
    print("All 19 regression tests passed successfully!")

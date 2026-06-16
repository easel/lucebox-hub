"""Per-adapter coverage for harness.clients.*.

Each client launcher shares the same shape:
  - ``write_config(...)`` emits a parseable config (TOML/JSON/YAML-ish)
    carrying the lucebox base_url + "/v1", model, and api_key.
  - ``launch(interactive=False, prompt=None)`` is a usage error (ValueError).
  - In print (non-interactive) mode the argv shape is stable.

We never exec a real binary: ``find_bin`` is monkeypatched to a fake path and
``_common.exec_client`` is captured so we can assert argv without a subprocess.
"""

from __future__ import annotations

import json
import tomllib
from pathlib import Path

import pytest

from harness.clients import (
    _common,
    claude_code,
    codex,
    hermes,
    openclaw,
    opencode,
    pi,
)

BASE_URL = "http://localhost:8080"
MODEL = "luce-dflash"
API_KEY = "sk-test-key"
EXPECTED_BASE = "http://localhost:8080/v1"


@pytest.fixture
def capture_exec(monkeypatch):
    """Capture argv/env passed to exec_client across all client modules.

    Each client imports ``exec_client`` by name into its own module
    namespace, so we patch the symbol in every module that uses it (plus
    ``_common`` for completeness). Returns a dict that the test fills in.
    """
    captured: dict = {}

    def fake_exec(argv, env, *, interactive, timeout=None):
        captured["argv"] = argv
        captured["env"] = env
        captured["interactive"] = interactive
        captured["timeout"] = timeout
        return 0

    for mod in (_common, codex, hermes, openclaw, opencode, pi):
        monkeypatch.setattr(mod, "exec_client", fake_exec, raising=False)
    return captured


@pytest.fixture
def fake_bins(monkeypatch):
    """Make find_bin resolve to a fake path everywhere it's imported."""
    def fake_find_bin(name, *, env_var, work_dir_hint=None):
        return f"/fake/bin/{name}"

    for mod in (_common, codex, hermes, openclaw, opencode, pi):
        monkeypatch.setattr(mod, "find_bin", fake_find_bin, raising=False)
    # claude_code uses its own find_claude_bin.
    monkeypatch.setattr(
        claude_code, "find_claude_bin", lambda: "/fake/bin/claude", raising=False
    )


# ── write_config: parseable + carries base_url/v1, model, api_key ───────────


def test_codex_write_config_is_toml(tmp_path: Path) -> None:
    codex.write_config(
        tmp_path, base_url=BASE_URL, model=MODEL, sandbox="read-only",
        wire_api="responses",
    )
    doc = tomllib.loads((tmp_path / "config.toml").read_text())
    assert doc["model"] == MODEL
    assert doc["model_providers"]["luce"]["base_url"] == EXPECTED_BASE


def test_openclaw_write_config_is_json(tmp_path: Path) -> None:
    patch_path = openclaw.write_config(
        tmp_path, base_url=BASE_URL, model=MODEL, api_key=API_KEY,
    )
    doc = json.loads(patch_path.read_text())
    prov = doc["models"]["providers"]["lucebox"]
    assert prov["baseUrl"] == EXPECTED_BASE
    assert prov["apiKey"] == API_KEY
    assert prov["models"][0]["id"] == MODEL


def test_opencode_write_config_is_json(tmp_path: Path) -> None:
    opencode.write_config(
        tmp_path, base_url=BASE_URL, model=MODEL, api_key=API_KEY,
    )
    doc = json.loads((tmp_path / "opencode.json").read_text())
    opts = doc["provider"]["lucebox"]["options"]
    assert opts["baseURL"] == EXPECTED_BASE
    assert opts["apiKey"] == API_KEY
    assert doc["model"] == f"lucebox/{MODEL}"


def test_pi_write_config_is_json(tmp_path: Path) -> None:
    pi.write_config(tmp_path, base_url=BASE_URL, model=MODEL, api_key=API_KEY)
    doc = json.loads((tmp_path / "agent" / "models.json").read_text())
    prov = doc["providers"]["lucebox"]
    assert prov["baseUrl"] == EXPECTED_BASE
    assert prov["apiKey"] == API_KEY
    assert prov["models"][0]["id"] == MODEL


def test_hermes_write_config_carries_wiring(tmp_path: Path) -> None:
    hermes.write_config(
        tmp_path, base_url=BASE_URL, model=MODEL, api_key=API_KEY,
        max_ctx=4096, max_tokens=512, repo_dir=str(tmp_path),
    )
    body = (tmp_path / "config.yaml").read_text()
    # YAML-ish: double-quoted JSON scalars for base_url/api_key/model.
    assert f'base_url: "{EXPECTED_BASE}"' in body
    assert f'api_key: "{API_KEY}"' in body
    assert f'default: "{MODEL}"' in body
    env = (tmp_path / ".env").read_text()
    assert f"OPENAI_BASE_URL={EXPECTED_BASE}" in env
    assert f"OPENAI_API_KEY={API_KEY}" in env


def test_claude_code_env_carries_base_and_key() -> None:
    env = claude_code.claude_env(BASE_URL, api_key=API_KEY)
    assert env["ANTHROPIC_BASE_URL"] == BASE_URL
    assert env["CLAUDE_CODE_API_BASE_URL"] == BASE_URL
    assert env["ANTHROPIC_API_KEY"] == API_KEY


# ── launch(interactive=False, prompt=None) → ValueError ─────────────────────


@pytest.mark.parametrize(
    "mod",
    [claude_code, codex, hermes, openclaw, opencode, pi],
    ids=lambda m: m.__name__.rsplit(".", 1)[-1],
)
def test_launch_noninteractive_requires_prompt(
    mod, fake_bins, capture_exec, tmp_path, monkeypatch
) -> None:
    # openclaw runs a `config patch` subprocess before the ValueError check;
    # stub subprocess.run there so the test stays hermetic.
    if mod is openclaw:
        monkeypatch.setattr(
            openclaw.subprocess, "run", lambda *a, **k: None, raising=False
        )
    kwargs: dict = {
        "base_url": BASE_URL,
        "model": MODEL,
        "prompt": None,
        "interactive": False,
    }
    # Steer config/state writes at tmp dirs for the dir-based clients.
    if mod in (codex, hermes, openclaw, pi):
        kwargs["work_dir"] = tmp_path
    elif mod is opencode:
        kwargs["project_dir"] = tmp_path
    with pytest.raises(ValueError):
        mod.launch(**kwargs)


# ── print-mode argv shape ───────────────────────────────────────────────────


def test_codex_print_argv(fake_bins, capture_exec, tmp_path) -> None:
    codex.launch(
        base_url=BASE_URL, model=MODEL, api_key=API_KEY, prompt="hi",
        interactive=False, work_dir=tmp_path,
    )
    argv = capture_exec["argv"]
    assert argv[0] == "/fake/bin/codex"
    assert "exec" in argv
    assert "--json" in argv
    assert argv[-1] == "hi"
    assert capture_exec["interactive"] is False


def test_opencode_print_argv(fake_bins, capture_exec, tmp_path) -> None:
    opencode.launch(
        base_url=BASE_URL, model=MODEL, api_key=API_KEY, prompt="hi",
        interactive=False, project_dir=tmp_path,
    )
    argv = capture_exec["argv"]
    assert argv[0] == "/fake/bin/opencode"
    assert "run" in argv
    assert "--format" in argv and "json" in argv
    assert argv[-1] == "hi"


def test_pi_print_argv(fake_bins, capture_exec, tmp_path) -> None:
    pi.launch(
        base_url=BASE_URL, model=MODEL, api_key=API_KEY, prompt="hi",
        interactive=False, work_dir=tmp_path,
    )
    argv = capture_exec["argv"]
    assert argv[0] == "/fake/bin/pi"
    assert "--print" in argv
    assert argv[-1] == "hi"


def test_hermes_print_argv(fake_bins, capture_exec, tmp_path) -> None:
    hermes.launch(
        base_url=BASE_URL, model=MODEL, api_key=API_KEY, prompt="hi",
        interactive=False, work_dir=tmp_path,
    )
    argv = capture_exec["argv"]
    assert argv[0] == "/fake/bin/hermes"
    assert "chat" in argv
    assert "--query" in argv
    assert argv[-1] == "hi"


def test_openclaw_print_argv(fake_bins, capture_exec, tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(
        openclaw.subprocess, "run", lambda *a, **k: None, raising=False
    )
    openclaw.launch(
        base_url=BASE_URL, model=MODEL, api_key=API_KEY, prompt="hi",
        interactive=False, work_dir=tmp_path,
    )
    argv = capture_exec["argv"]
    assert argv[0] == "/fake/bin/openclaw"
    assert "agent" in argv
    assert "--message" in argv
    assert argv[-1] == "hi"


# ── main() exit-code behavior ───────────────────────────────────────────────


CLIENT_MODULES = [claude_code, codex, hermes, openclaw, opencode, pi]


@pytest.mark.parametrize(
    "mod", CLIENT_MODULES, ids=lambda m: m.__name__.rsplit(".", 1)[-1]
)
def test_main_missing_binary_exits_127(mod, monkeypatch) -> None:
    """A missing client binary maps to exit 127 across every main()."""
    def boom(*a, **k):
        raise FileNotFoundError("binary not found")

    monkeypatch.setattr(mod, "find_bin", boom, raising=False)
    if mod is claude_code:
        monkeypatch.setattr(mod, "find_claude_bin", boom, raising=False)
    monkeypatch.setattr(
        "sys.argv", [f"harness-{mod.__name__.rsplit('.', 1)[-1]}",
                     "--base-url", "http://x"]
    )
    assert mod.main() == 127


def test_opencode_main_file_exists_exits_2(monkeypatch, tmp_path) -> None:
    """opencode main() maps a refused config overwrite to exit 2.

    Interactive mode (no --prompt) resolves cwd to the current directory and
    refuses to clobber an existing opencode.json there.
    """
    monkeypatch.setattr(
        opencode, "find_bin", lambda *a, **k: "/fake/bin/opencode", raising=False
    )
    # Pre-create opencode.json in the cwd so write_config (overwrite=False) refuses.
    (tmp_path / "opencode.json").write_text("{}")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "sys.argv", ["harness-opencode", "--base-url", "http://x"],
    )
    assert opencode.main() == 2


def test_hermes_main_default_timeout_is_420(monkeypatch, capture_exec, tmp_path) -> None:
    """hermes main() keeps the 420s default --timeout."""
    monkeypatch.setattr(
        hermes, "find_bin", lambda *a, **k: "/fake/bin/hermes", raising=False
    )
    monkeypatch.setenv("REPO_DIR", str(tmp_path))
    monkeypatch.setattr(
        "sys.argv",
        ["harness-hermes", "--base-url", "http://x", "--prompt", "hi"],
    )
    rc = hermes.main()
    assert rc == 0
    assert capture_exec["timeout"] == 420


def test_claude_code_print_argv(fake_bins, monkeypatch) -> None:
    captured: dict = {}

    def fake_exec(argv, env, *, interactive, timeout=None):
        captured["argv"] = argv
        captured["interactive"] = interactive
        return 0

    monkeypatch.setattr(claude_code, "exec_client", fake_exec)
    claude_code.launch(
        base_url=BASE_URL, model=MODEL, api_key=API_KEY, prompt="hi",
        interactive=False,
    )
    argv = captured["argv"]
    assert argv[0] == "/fake/bin/claude"
    assert "--print" in argv
    assert "--output-format" in argv and "json" in argv
    assert argv[-1] == "hi"
    assert captured["interactive"] is False

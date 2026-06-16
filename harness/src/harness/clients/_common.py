"""Shared helpers for harness client launchers.

Each ``harness.clients.<client>`` module exposes a ``launch()`` function with
the same shape (base_url, model, api_key, prompt, interactive, …). The
patterns below capture the bits that repeat: binary resolution, work-dir
setup, exec convention.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Callable
from pathlib import Path

DEFAULT_API_KEY = "sk-lucebox"
DEFAULT_MODEL_ID = "luce-dflash"


def find_bin(name: str, *, env_var: str, work_dir_hint: str | None = None) -> str:
    """Locate a client binary.

    Search order:
      1. ``$<env_var>`` (explicit override)
      2. ``$PATH``
      3. ``$CLIENT_WORK_DIR/<work_dir_hint>`` (test-box convention)

    Raises FileNotFoundError with a clear install hint otherwise.
    """
    explicit = os.environ.get(env_var)
    if explicit and _is_executable_file(Path(explicit)):
        return explicit
    on_path = shutil.which(name)
    if on_path:
        return on_path
    work_dir = os.environ.get("CLIENT_WORK_DIR")
    if work_dir and work_dir_hint:
        candidate = Path(work_dir) / work_dir_hint
        if _is_executable_file(candidate):
            return str(candidate)
    raise FileNotFoundError(
        f"{name!r} binary not found. Install it or set ${env_var} to its path."
    )


def _is_executable_file(p: Path) -> bool:
    """True iff ``p`` is a regular file (or symlink to one) that's +x.

    Used by find_bin so an env-var override pointing at a directory, a
    non-executable wrapper, or a stale path doesn't get returned to the
    launcher only to fail at exec time with a worse error.
    """
    return p.is_file() and os.access(p, os.X_OK)


def mktempdir(prefix: str) -> Path:
    """Make a working directory for client config/state. Returns Path."""
    return Path(tempfile.mkdtemp(prefix=f"lucebox-{prefix}-"))


def exec_client(
    argv: list[str],
    env: dict[str, str],
    *,
    interactive: bool,
    timeout: int | None = None,
) -> int:
    """Run a client binary with env, return its exit code.

    Interactive: inherits stdio (TUI works), no timeout.
    Non-interactive: stdin from /dev/null, optional wall-time timeout via
    ``subprocess.run(..., timeout=N)`` — no dependency on the external
    ``timeout`` binary, which isn't guaranteed across base images. On
    timeout we return 124 to match the conventional GNU ``timeout`` exit
    code, so harness scripts that branch on $? see the same value either
    way.
    """
    if interactive:
        return subprocess.run(argv, env=env).returncode
    try:
        return subprocess.run(
            argv, env=env, stdin=subprocess.DEVNULL, timeout=timeout
        ).returncode
    except subprocess.TimeoutExpired:
        return 124


def build_base_parser(prog: str, *, default_timeout: int | None = None) -> argparse.ArgumentParser:
    """Argparse parser with the args every client ``main()`` shares.

    Each launcher's CLI accepts the same base wiring
    (``--base-url``/``--model``/``--api-key``/``--prompt``/``--timeout``);
    clients add their own knobs to the returned parser before parsing. Pass
    ``default_timeout`` to override the ``None`` default (hermes uses 420).
    """
    parser = argparse.ArgumentParser(prog=prog)
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--model", default=DEFAULT_MODEL_ID)
    parser.add_argument("--api-key", default=DEFAULT_API_KEY)
    parser.add_argument("--prompt", default=None)
    parser.add_argument("--timeout", type=int, default=default_timeout)
    return parser


def run_main(
    launch: Callable[[], int],
    *,
    prog: str,
    handle_file_exists: bool = False,
) -> int:
    """Invoke a launcher's ``launch`` closure with the shared error tail.

    Every client ``main()`` ends the same way: call ``launch(...)`` and map a
    missing binary (``FileNotFoundError``) to exit 127, printing a ``[prog]``-
    prefixed message to stderr. ``opencode`` additionally maps a refused
    config overwrite (``FileExistsError``) to exit 2 — opt in via
    ``handle_file_exists=True``.
    """
    try:
        return launch()
    except FileNotFoundError as e:
        print(f"[{prog}] {e}", file=sys.stderr)
        return 127
    except FileExistsError as e:
        if not handle_file_exists:
            raise
        print(f"[{prog}] {e}", file=sys.stderr)
        return 2
